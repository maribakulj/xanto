#!/usr/bin/env python3
"""Post-hoc centering diagnostics, separate from localization and predictions."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


DRAWS = 10000
SEED = 0


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlaps(boxes, reference):
    boxes = np.asarray(boxes, dtype=np.float64)
    ref = np.asarray(reference, dtype=np.float64)
    intersection_size = np.maximum(
        0.0, np.minimum(boxes[:, :2] + boxes[:, 2:], ref[:2] + ref[2:])
        - np.maximum(boxes[:, :2], ref[:2]))
    intersection = intersection_size.prod(axis=1)
    union = boxes[:, 2:].prod(axis=1) + ref[2:].prod() - intersection
    return intersection / union


def main():
    root = Path(__file__).resolve().parents[1]
    input_path = root / "cv/inputs.json"
    reference_path = root / "cv/references.json"
    inputs = json.loads(input_path.read_text())
    references = json.loads(reference_path.read_text())
    query = inputs["queries"][0]
    width, height = query["bbox"][2:]
    if not (0 < width <= 1 and 0 < height <= 1):
        raise ValueError("Invalid normalized query size")
    centered = [(1 - width) / 2, (1 - height) / 2, width, height]
    rng = np.random.default_rng(SEED)
    random_xy = rng.uniform(size=(DRAWS, 2)) * np.array([1 - width, 1 - height])
    random_boxes = np.column_stack((random_xy, np.full(DRAWS, width), np.full(DRAWS, height)))
    assert np.all((random_boxes[:, :2] >= 0) & (random_boxes[:, :2] + random_boxes[:, 2:] <= 1))
    assert np.isclose(overlaps([centered], centered)[0], 1.0)
    reference_by_id = {item["target_id"]: item for item in references["boxes"]}
    results = []
    for image in inputs["images"]:
        reference = reference_by_id[image["id"]]["bbox"]
        values = overlaps(random_boxes, reference)
        percentiles = np.percentile(values, [50, 90, 95, 99], method="linear")
        results.append({
            "query_id": query["id"], "target_id": image["id"],
            "box": centered, "center_iou": float(overlaps([centered], reference)[0]),
            "normalized_box_size": [width, height], "random_draw_count": DRAWS,
            "random_iou": {**{f"p{p}": float(v) for p, v in zip([50, 90, 95, 99], percentiles)},
                           "max": float(values.max())}})
    output = {
        "schema_version": "1.0", "diagnostic_status": "post_hoc_evaluation_only",
        "reference_status": references["reference_status"],
        "run": {"generated_at": datetime.now(timezone.utc).isoformat(),
                "input_sha256": digest(input_path), "reference_sha256": digest(reference_path),
                "script_sha256": digest(Path(__file__).resolve()),
                "numpy_version": np.__version__, "seed": SEED, "random_generator": "numpy.default_rng / PCG64",
                "random_draw_count_per_target": DRAWS,
                "sampling": "Top-left coordinates uniform over [0, 1-width] x [0, 1-height]; same normalized draws reused for every target.",
                "size_policy": "Width and height equal the supplied primary query bbox fractions in each target image; no size fitting to references.",
                "percentile_method": "numpy.percentile, linear"},
        "query_id": query["id"], "source_id": query["source_id"],
        "query_bbox": query["bbox"], "results": results,
        "limitations": [
            "Post-hoc descriptive diagnostic using the existing approximate reference boxes; no localization program or prediction is changed.",
            "This is not a p-value or a calibrated significance test.",
            "A single uniform random box is not comparable to selecting the highest-scoring proposal from thousands of searched windows.",
            "The random boxes have one fixed relative size; the localization algorithms search multiple scales and have different image preprocessing.",
            "The empirical maximum is only the largest overlap among these 10000 draws, not a theoretical maximum.",
            "The source reference repeats the query. Two target works and approximate assisted references do not form an independent benchmark."
        ]}
    destination = root / "cv/trivial_controls.json"
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    for result in results:
        print(result["target_id"], "center_iou=", round(result["center_iou"], 4),
              "random_iou=", {k: round(v, 4) for k, v in result["random_iou"].items()})
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
