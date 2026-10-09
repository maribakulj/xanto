#!/usr/bin/env python3
"""Fixed multi-scale NCC baseline; localization reads only cv/inputs.json.

No target annotations, object titles, catalogue descriptions or reference boxes
are used. All image coordinates refer to the unmodified source files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import PIL
import scipy
from PIL import Image
from scipy.ndimage import sobel
from scipy.signal import fftconvolve


HEIGHT_FRACTIONS = (0.18, 0.24, 0.32, 0.42, 0.55, 0.72)
STRIDE = 14
NMS_IOU = 0.35
CHANNEL_WEIGHTS = (0.25, 0.75)
METHOD = "gradient_ncc"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def features(im):
    gray = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
    gradient = np.hypot(sobel(gray, axis=0, mode="reflect"),
                        sobel(gray, axis=1, mode="reflect"))
    return (gray, gradient)


def window_sum(a, height, width):
    integral = np.pad(a.astype(np.float64), ((1, 0), (1, 0)))
    integral = integral.cumsum(0).cumsum(1)
    return (integral[height:, width:] - integral[:-height, width:]
            - integral[height:, :-width] + integral[:-height, :-width])


def ncc(target, template):
    """Zero-mean, locally variance-normalized cross correlation per channel."""
    height, width = template.shape
    zero = template.astype(np.float64) - float(template.mean())
    template_energy = np.square(zero).sum()
    sums = window_sum(target, height, width)
    patch_energy = window_sum(np.square(target.astype(np.float64)), height, width)
    patch_energy -= np.square(sums) / (height * width)
    numerator = fftconvolve(target, zero[::-1, ::-1], mode="valid")
    denominator = np.sqrt(np.maximum(patch_energy, 0.0) * template_energy)
    score = np.zeros_like(numerator)
    np.divide(numerator, denominator, out=score, where=denominator > 1e-10)
    return np.clip(score, -1.0, 1.0)


def iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    union = a[2] * a[3] + b[2] * b[3] - intersection
    return intersection / union if union else 0.0


def load_images(root, inputs):
    images = {}
    for item in inputs["images"]:
        path = root / item["image"]
        if digest(path) != item["sha256"]:
            raise ValueError(f"Image checksum mismatch: {item['id']}")
        with Image.open(path) as opened:
            im = opened.convert("RGB")
        if im.size != (item["width"], item["height"]):
            raise ValueError(f"Image dimensions mismatch: {item['id']}")
        images[item["id"]] = im
    return images


def localize(query_image, target, top_k):
    width, height = target.size
    aspect = query_image.width / query_image.height
    target_channels = features(target)
    candidates = []
    windows = []
    seen_shapes = set()
    for fraction in HEIGHT_FRACTIONS:
        h = max(28, round(height * fraction / STRIDE) * STRIDE)
        w = max(28, round(h * aspect / STRIDE) * STRIDE)
        if h > height or w > width or (w, h) in seen_shapes:
            continue
        seen_shapes.add((w, h))
        template = features(query_image.resize((w, h), Image.Resampling.LANCZOS))
        scores = sum(weight * ncc(channel, templ)
                     for weight, channel, templ in zip(CHANNEL_WEIGHTS, target_channels, template))
        xs = range(0, width - w + 1, STRIDE)
        ys = range(0, height - h + 1, STRIDE)
        windows.append({"requested_height_fraction": fraction, "width": w, "height": h,
                        "positions": len(xs) * len(ys)})
        for y in ys:
            for x in xs:
                candidates.append({"bbox": [x / width, y / height, w / width, h / height],
                                   "score": float(scores[y, x])})
    candidates.sort(key=lambda item: item["score"], reverse=True)
    selected = []
    for candidate in candidates:
        if all(iou(candidate["bbox"], other["bbox"]) <= NMS_IOU for other in selected):
            selected.append(candidate)
            if len(selected) == top_k:
                break
    for rank, proposal in enumerate(selected, 1):
        proposal["rank"] = rank
    return selected, len(candidates), windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    started = time.monotonic()
    input_path = root / "cv/inputs.json"
    inputs = json.loads(input_path.read_text())
    parameters = inputs["parameters"]
    max_side = parameters["max_image_side"]
    top_k = parameters["top_k"]
    images = load_images(root, inputs)
    results = []
    actual_windows = {}
    for query in inputs["queries"]:
        source = images[query["source_id"]]
        x, y, w, h = query["bbox"]
        # PIL floating-point crop uses the supplied box without a target-aware adjustment.
        query_image = source.crop((x * source.width, y * source.height,
                                   (x + w) * source.width, (y + h) * source.height))
        for target_id, original in images.items():
            scale = min(1.0, max_side / max(original.size))
            size = (round(original.width * scale), round(original.height * scale))
            target = original.resize(size, Image.Resampling.LANCZOS)
            proposals, count, windows = localize(query_image, target, top_k)
            actual_windows[f"{query['id']}:{target_id}"] = {"working_size": list(size), "windows": windows}
            results.append({"query_id": query["id"], "target_id": target_id, "method": METHOD,
                            "proposals": proposals, "candidate_count": count, "heatmap": None,
                            "notes": ["NCC similarity, not a probability; all grid candidates searched.",
                                      "No mirror, rotation or perspective correction.",
                                      "Source image is a technical control; query box was not inserted among candidates."
                                      if target_id == query["source_id"] else "Target reference boxes were not read."]})
            print(f"{target_id}: {count} candidates, {len(proposals)} retained", flush=True)
    output = {
        "schema_version": "1.0",
        "run": {"method": METHOD,
                "method_label": "Gabarit multiechelle : NCC gris et magnitude des gradients",
                "model_id": "none", "model_revision": "not-applicable", "device": "cpu",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": round(time.monotonic() - started, 3),
                "input_sha256": digest(input_path),
                "script_sha256": digest(Path(__file__).resolve()),
                "library_versions": {"numpy": np.__version__, "scipy": scipy.__version__, "Pillow": PIL.__version__},
                "parameters": {"max_image_side": max_side, "top_k": top_k,
                               "height_fractions": HEIGHT_FRACTIONS, "stride_pixels": STRIDE,
                               "window_quantization_pixels": STRIDE, "min_window_side": 28,
                               "nms_iou_threshold": NMS_IOU, "grayscale_weight": CHANNEL_WEIGHTS[0],
                               "sobel_magnitude_weight": CHANNEL_WEIGHTS[1],
                               "resize_policy": "Preserve image aspect ratio; round dimensions to pixels, not to patches. This differs slightly from DINO patch-grid resizing.",
                               "score_unit": "Weighted normalized cross correlation in [-1, 1]; similarity, not probability.",
                               "selection_policy": parameters["selection_policy"],
                               "actual_search_grids": actual_windows},
                "limitations": ["Appearance baseline sensitive to medium, pose, illumination and framing changes.",
                                "Aspect ratio follows query, rounded to the fixed 14-pixel grid.",
                                "Not a model of body articulation, narrative meaning or historical transmission.",
                                "No fitting or parameter selection using target references."]},
        "queries": inputs["queries"], "results": results}
    destination = root / "cv/baseline_results.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {destination}; elapsed {time.monotonic() - started:.2f}s")


if __name__ == "__main__":
    main()
