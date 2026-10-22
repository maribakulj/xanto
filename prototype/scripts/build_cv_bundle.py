"""Validate calculated predictions and package them separately from annotations."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def valid_bbox(box):
    return (isinstance(box, list) and len(box) == 4
            and all(type(v) in (int, float) and math.isfinite(v) for v in box)
            and box[0] >= 0 and box[1] >= 0 and box[2] > 0 and box[3] > 0
            and box[0] + box[2] <= 1.000001 and box[1] + box[3] <= 1.000001)


def validate_run(inputs, result, input_hash, script_name, root=ROOT):
    run = result["run"]
    require(run.get("input_sha256") == input_hash, "Les résultats ne correspondent pas aux entrées actuelles")
    script_hash = hashlib.sha256((root / "scripts" / script_name).read_bytes()).hexdigest()
    require(run.get("script_sha256") == script_hash, "Le code a changé depuis le calcul : relancer avant livraison")
    image_ids = {x["id"] for x in inputs["images"]}
    query_ids = {x["id"] for x in inputs["queries"]}
    expected = {(q, i) for q in query_ids for i in image_ids}
    seen = set()
    for row in result["results"]:
        key = row["query_id"], row["target_id"]
        require(key in expected and key not in seen, "Paire requête/cible manquante ou dupliquée")
        seen.add(key)
        scores = []
        require(len(row["proposals"]) <= inputs["parameters"]["top_k"], "Nombre de propositions incohérent")
        for rank, proposal in enumerate(row["proposals"], 1):
            require(proposal["rank"] == rank, "Rang de proposition incorrect")
            require(valid_bbox(proposal["bbox"]), "Proposition hors de l'image")
            score = proposal["score"]
            require(type(score) in (float, int) and math.isfinite(score), "Score non fini")
            scores.append(score)
        require(scores == sorted(scores, reverse=True), "Les propositions ne sont pas classées par score")
        require(row["candidate_count"] >= len(scores), "Nombre de fenêtres évaluées incohérent")
    require(seen == expected, "Une cible n'a pas été traitée")
    return result


def build():
    inputs_path = ROOT / "cv" / "inputs.json"
    inputs = json.loads(inputs_path.read_text())
    input_hash = hashlib.sha256(inputs_path.read_bytes()).hexdigest()
    for image in inputs["images"]:
        require(hashlib.sha256((ROOT / image["image"]).read_bytes()).hexdigest() == image["sha256"], "Une image d'entrée a changé")
    dino = json.loads((ROOT / "cv" / "results.json").read_text())
    baseline = json.loads((ROOT / "cv" / "baseline_results.json").read_text())
    validate_run(inputs, dino, input_hash, "run_cv.py")
    validate_run(inputs, baseline, input_hash, "cv_baseline.py")
    evaluation = json.loads((ROOT / "cv" / "evaluation.json").read_text())
    require(evaluation.get("reference_status"), "Le statut des références d'évaluation manque")
    provenance = evaluation["metrics_definition"]
    require(provenance.get("input_sha256_verified") == input_hash, "L'évaluation utilise d'autres entrées")
    for filename in ("results.json", "baseline_results.json"):
        require(provenance["prediction_file_sha256"].get(filename) == hashlib.sha256((ROOT / "cv" / filename).read_bytes()).hexdigest(), "Les prédictions ont changé depuis l'évaluation")
    reference_hash = hashlib.sha256((ROOT / "cv" / "references.json").read_bytes()).hexdigest()
    require(provenance.get("reference_file_sha256") == reference_hash, "Les références ont changé depuis l'évaluation")
    require(provenance.get("evaluation_script_sha256") == hashlib.sha256((ROOT / "scripts" / "evaluate_cv.py").read_bytes()).hexdigest(), "Le code d'évaluation a changé")
    for row in evaluation["results"]:
        for field in ("top1_iou", "best_top5_iou"):
            require(type(row[field]) in (float, int) and 0 <= row[field] <= 1, "IoU invalide")
    controls = json.loads((ROOT / "cv" / "trivial_controls.json").read_text())
    require(controls["run"]["input_sha256"] == input_hash and controls["run"]["reference_sha256"] == reference_hash, "Les diagnostics triviaux utilisent d'autres entrées ou références")
    require(controls["run"]["script_sha256"] == hashlib.sha256((ROOT / "scripts" / "trivial_controls.py").read_bytes()).hexdigest(), "Le code des diagnostics triviaux a changé")
    payload = {"inputs": inputs, "dino": dino, "baseline": baseline, "evaluation": evaluation, "controls": controls}
    target = ROOT / "data" / "cv_bundle.js"
    temporary = target.with_suffix(".js.tmp")
    temporary.write_text("// Calculated CV results, separate from historical annotations.\nwindow.XANTO_CV = " + json.dumps(payload, ensure_ascii=True, indent=2) + ";\n")
    temporary.replace(target)
    print(f"Calculs vérifiés : {len(dino['results'])} recherches DINOv2, {len(baseline['results'])} recherches de référence.")
    return payload


if __name__ == "__main__":
    build()
