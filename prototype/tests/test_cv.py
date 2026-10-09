"""Numerical and integrity checks for saved CV runs; standard library only.

Run with: python3 -B -m unittest discover -s tests -p test_cv.py -v
No model is imported or recomputed, and all invalid fixtures stay in memory.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_overlap(first, second):
    """Recompute rectangle overlap without calling the production evaluator."""
    corners = [(box[0], box[1], box[0] + box[2], box[1] + box[3])
               for box in (first, second)]
    ax, ay, ar, ab = corners[0]
    bx, by, br, bb = corners[1]
    if ar <= bx or br <= ax or ab <= by or bb <= ay:
        intersection = 0.0
    else:
        intersection = (min(ar, br) - max(ax, bx)) * (min(ab, bb) - max(ay, by))
    area_first = (ar - ax) * (ab - ay)
    area_second = (br - bx) * (bb - by)
    return intersection / (area_first + area_second - intersection)


class CVIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs_path = ROOT / "cv/inputs.json"
        cls.inputs = json.loads(cls.inputs_path.read_text())
        cls.runs = {
            "baseline_results.json": (json.loads((ROOT / "cv/baseline_results.json").read_text()), "cv_baseline.py"),
            "results.json": (json.loads((ROOT / "cv/results.json").read_text()), "run_cv.py"),
        }
        cls.evaluation = json.loads((ROOT / "cv/evaluation.json").read_text())
        cls.references = json.loads((ROOT / "cv/references.json").read_text())
        # These two scripts use only the standard library and have guarded main functions.
        cls.evaluator = runpy.run_path(str(ROOT / "scripts/evaluate_cv.py"), run_name="cv_evaluator_under_test")
        cls.builder = runpy.run_path(str(ROOT / "scripts/build_cv_bundle.py"), run_name="cv_validator_under_test")

    def test_iou_known_geometry(self):
        cases = [
            ("identical", [0, 0, 0.5, 0.5], [0, 0, 0.5, 0.5], 1.0),
            ("disjoint", [0, 0, 0.2, 0.2], [0.7, 0.7, 0.2, 0.2], 0.0),
            ("edge_touch", [0, 0, 0.5, 0.5], [0.5, 0, 0.5, 0.5], 0.0),
            ("overlap", [0, 0, 0.5, 0.5], [0.25, 0.25, 0.5, 0.5], 1 / 7),
            ("contained", [0, 0, 1, 1], [0.25, 0.25, 0.5, 0.5], 0.25),
        ]
        for name, a, b, expected in cases:
            with self.subTest(name=name):
                self.assertAlmostEqual(self.evaluator["iou"](a, b), expected, places=14)
                self.assertAlmostEqual(self.evaluator["iou"](b, a), expected, places=14)
                self.assertAlmostEqual(independent_overlap(a, b), expected, places=14)

    def test_center_membership_and_boundary(self):
        contains = self.evaluator["center_inside"]
        reference = [0.25, 0.25, 0.5, 0.5]
        self.assertTrue(contains([0.3, 0.3, 0.2, 0.2], reference))
        self.assertTrue(contains([0, 0, 0.5, 0.5], reference))  # center on boundary
        self.assertFalse(contains([0, 0, 0.2, 0.2], reference))

    def test_inputs_have_only_images_source_query_and_parameters(self):
        self.assertEqual(set(self.inputs), {"images", "queries", "parameters"})
        image_ids = {item["id"] for item in self.inputs["images"]}
        self.assertEqual(len(image_ids), len(self.inputs["images"]))
        for image in self.inputs["images"]:
            self.assertEqual(set(image), {"id", "image", "width", "height", "sha256"})
        for query in self.inputs["queries"]:
            self.assertEqual(set(query), {"id", "source_id", "bbox", "provenance"})
            self.assertIn(query["source_id"], image_ids)
        self.assertEqual(set(self.inputs["parameters"]), {
            "model_id", "model_revision", "max_image_side", "top_k", "seed", "selection_policy"})
        forbidden = {"references", "observations", "comparisons", "annotations", "reference_bbox",
                     "target_bbox", "target_boxes", "ground_truth", "labels"}

        def inspect(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        inspect(self.inputs)

    def test_input_images_and_saved_run_hashes(self):
        input_hash = digest(self.inputs_path)
        for image in self.inputs["images"]:
            with self.subTest(image=image["id"]):
                self.assertEqual(digest(ROOT / image["image"]), image["sha256"])
        for filename, (run, script_name) in self.runs.items():
            with self.subTest(run=filename):
                self.assertEqual(run["run"]["input_sha256"], input_hash)
                self.assertEqual(run["run"]["script_sha256"], digest(ROOT / "scripts" / script_name))
                self.assertEqual(run["queries"], self.inputs["queries"])
                self.builder["validate_run"](self.inputs, run, input_hash, script_name, root=ROOT)

    def test_saved_proposal_bounds_ranks_scores_and_coverage(self):
        expected = {(query["id"], image["id"])
                    for query in self.inputs["queries"] for image in self.inputs["images"]}
        for filename, (run, _) in self.runs.items():
            pairs = [(row["query_id"], row["target_id"]) for row in run["results"]]
            self.assertEqual(set(pairs), expected)
            self.assertEqual(len(pairs), len(expected))
            for row in run["results"]:
                with self.subTest(run=filename, target=row["target_id"]):
                    self.assertEqual(row["method"], run["run"]["method"])
                    proposals = row["proposals"]
                    self.assertGreater(len(proposals), 0)
                    self.assertLessEqual(len(proposals), self.inputs["parameters"]["top_k"])
                    self.assertGreaterEqual(row["candidate_count"], len(proposals))
                    self.assertEqual([item["rank"] for item in proposals], list(range(1, len(proposals) + 1)))
                    scores = [item["score"] for item in proposals]
                    self.assertEqual(scores, sorted(scores, reverse=True))
                    for proposal in proposals:
                        self.assertTrue(math.isfinite(proposal["score"]))
                        self.assertGreaterEqual(proposal["score"], -1.000001)
                        self.assertLessEqual(proposal["score"], 1.000001)
                        box = proposal["bbox"]
                        self.assertEqual(len(box), 4)
                        self.assertTrue(all(math.isfinite(value) for value in box))
                        x, y, w, h = box
                        self.assertGreaterEqual(x, 0)
                        self.assertGreaterEqual(y, 0)
                        self.assertGreater(w, 0)
                        self.assertGreater(h, 0)
                        self.assertLessEqual(x + w, 1.000001)
                        self.assertLessEqual(y + h, 1.000001)

    def test_evaluation_matches_independent_recomputation(self):
        references = {row["target_id"]: row["bbox"] for row in self.references["boxes"]}
        predictions = {(row["method"], row["target_id"]): row
                       for run, _ in self.runs.values() for row in run["results"]}
        evaluated = {(row["method"], row["target_id"]): row for row in self.evaluation["results"]}
        self.assertEqual(set(evaluated), set(predictions))
        self.assertEqual(len(evaluated), len(self.evaluation["results"]))
        for key, row in evaluated.items():
            with self.subTest(method=key[0], target=key[1]):
                reference = references[key[1]]
                self.assertEqual(row["reference_bbox"], reference)
                proposals = predictions[key]["proposals"][:5]
                values = [independent_overlap(p["bbox"], reference) for p in proposals]
                best = max(range(len(values)), key=values.__getitem__)
                self.assertAlmostEqual(row["top1_iou"], values[0], places=12)
                self.assertAlmostEqual(row["best_top5_iou"], values[best], places=12)
                self.assertEqual(row["best_top5_rank"], proposals[best]["rank"])
                box = proposals[0]["bbox"]
                cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
                expected_inside = (reference[0] <= cx <= reference[0] + reference[2]
                                   and reference[1] <= cy <= reference[1] + reference[3])
                self.assertIs(row["top1_center_inside"], expected_inside)

    def test_evaluation_hashes_are_current(self):
        provenance = self.evaluation["metrics_definition"]
        self.assertEqual(provenance["input_sha256_verified"], digest(self.inputs_path))
        self.assertEqual(provenance["reference_file_sha256"], digest(ROOT / "cv/references.json"))
        self.assertEqual(provenance["evaluation_script_sha256"], digest(ROOT / "scripts/evaluate_cv.py"))
        self.assertEqual(set(provenance["prediction_file_sha256"]), set(self.runs))
        for filename, expected in provenance["prediction_file_sha256"].items():
            self.assertEqual(expected, digest(ROOT / "cv" / filename))

    def test_validator_rejects_invalid_in_memory_fixtures(self):
        original, script_name = self.runs["baseline_results.json"]
        original_bytes = (ROOT / "cv/baseline_results.json").read_bytes()
        mutations = {
            "stale_inputs": lambda run: run["run"].update(input_sha256="0" * 64),
            "stale_script": lambda run: run["run"].update(script_sha256="0" * 64),
            "outside_image": lambda run: run["results"][0]["proposals"][0].update(bbox=[0.9, 0, 0.2, 0.2]),
            "negative_width": lambda run: run["results"][0]["proposals"][0].update(bbox=[0, 0, -0.1, 0.2]),
            "wrong_rank": lambda run: run["results"][0]["proposals"][0].update(rank=2),
            "unsorted_score": lambda run: run["results"][0]["proposals"][-1].update(score=2.0),
            "nonfinite_score": lambda run: run["results"][0]["proposals"][0].update(score=float("nan")),
            "missing_target": lambda run: run["results"].pop(),
        }
        for name, mutate in mutations.items():
            with self.subTest(fixture=name):
                fixture = copy.deepcopy(original)
                mutate(fixture)
                with self.assertRaises(ValueError):
                    self.builder["validate_run"](self.inputs, fixture, digest(self.inputs_path), script_name, root=ROOT)
        self.assertEqual((ROOT / "cv/baseline_results.json").read_bytes(), original_bytes)
        self.assertEqual(json.loads(original_bytes), original)


if __name__ == "__main__":
    unittest.main()
