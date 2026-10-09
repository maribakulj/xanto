#!/usr/bin/env python3
"""Evaluate saved predictions without changing localization scripts or proposals.

References are opened only after the requested prediction files exist and their
input checksums have been validated. --baseline-only supports an earlier partial
evaluation while the independent DINO run is still computing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_box(box):
    if len(box) != 4 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in box):
        raise ValueError(f"Invalid box: {box}")
    x, y, w, h = box
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > 1 + 1e-8 or y + h > 1 + 1e-8:
        raise ValueError(f"Box outside normalized image bounds: {box}")


def iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    union = a[2] * a[3] + b[2] * b[3] - intersection
    return intersection / union if union > 0 else 0.0


def center_inside(prediction, reference):
    center_x = prediction[0] + prediction[2] / 2
    center_y = prediction[1] + prediction[3] / 2
    return (reference[0] <= center_x <= reference[0] + reference[2]
            and reference[1] <= center_y <= reference[1] + reference[3])


def self_check_metrics():
    a = [0.0, 0.0, 0.5, 0.5]
    assert iou(a, a) == 1.0
    assert iou(a, [0.5, 0.5, 0.5, 0.5]) == 0.0
    assert math.isclose(iou(a, [0.25, 0.25, 0.5, 0.5]), 1 / 7)
    assert center_inside(a, a)
    assert not center_inside(a, [0.5, 0.5, 0.5, 0.5])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--baseline-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    self_check_metrics()
    prediction_paths = [root / "cv/baseline_results.json"]
    if not args.baseline_only:
        prediction_paths.append(root / "cv/results.json")
    for path in prediction_paths:
        if not path.is_file():
            raise SystemExit(f"Predictions not ready: {path}. Wait for computation or use --baseline-only.")
    input_path = root / "cv/inputs.json"
    expected_input_sha256 = sha256(input_path)
    inputs = json.loads(input_path.read_text())
    expected_pairs = {(query["id"], image["id"])
                      for query in inputs["queries"] for image in inputs["images"]}
    predictions = []
    for path in prediction_paths:
        output = json.loads(path.read_text())
        if output["run"]["input_sha256"] != expected_input_sha256:
            raise ValueError(f"Input checksum mismatch: {path}")
        pairs = {(item["query_id"], item["target_id"]) for item in output["results"]}
        if pairs != expected_pairs or len(output["results"]) != len(expected_pairs):
            raise ValueError(f"Missing or duplicated query/target predictions: {path}")
        for result in output["results"]:
            scores = []
            for expected_rank, proposal in enumerate(result["proposals"], 1):
                validate_box(proposal["bbox"])
                if proposal["rank"] != expected_rank or not math.isfinite(proposal["score"]):
                    raise ValueError(f"Invalid prediction rank/score: {path}")
                scores.append(proposal["score"])
            if scores != sorted(scores, reverse=True):
                raise ValueError(f"Predictions are not sorted by descending similarity: {path}")
        predictions.append(output)

    # Deliberately after prediction availability and integrity checks.
    reference_path = root / "cv/references.json"
    references = json.loads(reference_path.read_text())
    reference_by_id = {item["target_id"]: item for item in references["boxes"]}
    if len(reference_by_id) != len(references["boxes"]):
        raise ValueError("Duplicate reference target ids")
    for reference in reference_by_id.values():
        validate_box(reference["bbox"])

    results = []
    for output in predictions:
        for predicted in output["results"]:
            reference = reference_by_id[predicted["target_id"]]
            bbox = reference["bbox"]
            top_five = predicted["proposals"][:5]
            overlaps = [iou(item["bbox"], bbox) for item in top_five]
            best_index = max(range(len(overlaps)), key=overlaps.__getitem__) if overlaps else None
            results.append({
                "target_id": predicted["target_id"], "method": predicted["method"],
                "reference_bbox": bbox,
                "top1_iou": overlaps[0] if overlaps else 0.0,
                "best_top5_iou": overlaps[best_index] if best_index is not None else 0.0,
                "best_top5_rank": top_five[best_index]["rank"] if best_index is not None else None,
                "top1_center_inside": center_inside(top_five[0]["bbox"], bbox) if top_five else False})

    evaluation = {
        "reference_status": references["reference_status"],
        "metrics_definition": {
            "top1_iou": "Area of intersection divided by area of union for the highest-similarity proposal and approximate reference; range 0 to 1.",
            "best_top5_iou": "Maximum IoU among the first five proposals already saved after NMS; evaluation does not reorder predictions.",
            "best_top5_rank": "Original similarity rank of maximum-IoU proposal; first rank wins ties. It does not select a new prediction.",
            "top1_center_inside": "Whether the center of the top similarity proposal lies in the reference rectangle, including its boundary.",
            "input_sha256_verified": expected_input_sha256,
            "prediction_file_sha256": {path.name: sha256(path) for path in prediction_paths},
            "reference_file_sha256": sha256(reference_path),
            "evaluation_script_sha256": sha256(Path(__file__).resolve())},
        "results": results,
        "limitations": [
            "Approximate references come from pre-existing assistant-assisted annotation, not an independent human benchmark.",
            "The source control reuses the supplied query; it tests implementation, not generalization.",
            "Only two target works are evaluated. No aggregate accuracy, historical conclusion or model ranking is justified.",
            "Box overlap does not evaluate identity, hand contacts, narrative action or historical transmission.",
            "Similarity scores are not probabilities and are not calibrated across methods.",
            "Both methods use the same six height fractions, 14-pixel window grid and NMS 0.35; image and query preprocessing differ."
        ]}
    if args.baseline_only:
        evaluation["limitations"].append("Partial evaluation: baseline only; DINO predictions were not requested by this invocation.")
    destination = root / "cv/evaluation.json"
    destination.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    print(f"Wrote {destination}; no localization script or proposal was modified.")


if __name__ == "__main__":
    main()
