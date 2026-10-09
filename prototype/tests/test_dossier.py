import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_bundle", ROOT / "scripts" / "build_bundle.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DossierIntegrity(unittest.TestCase):
    def setUp(self):
        self.data = builder.load_data()

    def test_complete_dossier_and_traceability(self):
        builder.validate(self.data)

    def test_invalid_image_location_rejected(self):
        self.data["observations"][0]["bbox"] = [.9, .2, .5, .1]
        with self.assertRaisesRegex(ValueError, "hors image"):
            builder.validate(self.data)

    def test_untraceable_comparison_rejected(self):
        self.data["comparisons"][0]["observation_ids"] = ["invented-observation", "also-invented"]
        with self.assertRaisesRegex(ValueError, "références"):
            builder.validate(self.data)

    def test_same_witness_cannot_establish_pair(self):
        comparison = self.data["comparisons"][0]
        ids = [o["id"] for o in self.data["observations"] if o["object_id"] == comparison["from_id"]]
        comparison["observation_ids"] = ids[:2]
        with self.assertRaisesRegex(ValueError, "références"):
            builder.validate(self.data)

    def test_unknown_evidence_type_rejected(self):
        self.data["observations"][0]["evidence_kind"] = "scientifically_proven"
        with self.assertRaisesRegex(ValueError, "provenance"):
            builder.validate(self.data)

    def test_duplicate_observation_rejected(self):
        self.data["observations"].append(copy.deepcopy(self.data["observations"][0]))
        with self.assertRaisesRegex(ValueError, "dupliqués"):
            builder.validate(self.data)

    def test_source_missing_rejected(self):
        self.data["corpus"][0]["source_url"] = ""
        with self.assertRaises(ValueError):
            builder.validate(self.data)

    def test_crop_change_invalidates_annotation(self):
        self.data["observations"][0]["image_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "empreinte"):
            builder.validate(self.data)

    def test_entity_mismatch_rejected(self):
        self.data["comparisons"][0]["from_entity"] = "E99"
        with self.assertRaisesRegex(ValueError, "entité"):
            builder.validate(self.data)


if __name__ == "__main__":
    unittest.main()
