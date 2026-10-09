"""Validate the source dossier and build a dependency-free browser bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"image", "catalogue", "interpretation"}
CERTAINTIES = {"clear", "probable", "indeterminate"}
TYPES = {"POSE", "ATTRIBUTE", "RELATION", "ACTION", "INSCRIPTION"}
STATUSES = {"observed_difference", "catalogue_attribution", "hypothesis", "indeterminate"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_ids(rows, name):
    require(isinstance(rows, list) and len(rows) > 0, f"{name}: liste vide ou invalide")
    ids = [row.get("id") for row in rows]
    require(all(isinstance(x, str) and x.strip() for x in ids), f"{name}: identifiant manquant")
    require(len(set(ids)) == len(ids), f"{name}: identifiants dupliqués")
    return set(ids)


def validate(data, root=ROOT):
    objects = unique_ids(data["corpus"], "corpus")
    observation_ids = unique_ids(data["observations"], "observations")
    unique_ids(data["comparisons"], "comparisons")
    require(objects == {"parnassus", "apollo", "paris"}, "Le pilote A comprend exactement les trois témoins retenus")
    for obj in data["corpus"]:
        tag = obj["id"]
        for key in ("title", "institution", "inventory", "date", "medium", "image", "image_url", "source_url", "physical_dimensions", "image_status", "attribution_note", "license"):
            require(isinstance(obj.get(key), str) and obj[key].strip(), f"{tag}: {key} manquant")
        asset = (root / obj["image"]).resolve()
        require(asset.is_relative_to((root / "assets").resolve()) and asset.is_file(), f"{tag}: image locale absente ou hors assets")
        for key in ("image_width", "image_height"):
            require(type(obj.get(key)) is int and obj[key] > 0, f"{tag}: {key} invalide")
        require(obj["source_url"].startswith("https://"), f"{tag}: URL source invalide")
        require(isinstance(obj.get("limitations"), list), f"{tag}: limites manquantes")
    lookup = {row["id"]: row for row in data["observations"]}
    object_lookup = {obj["id"]: obj for obj in data["corpus"]}
    for row in data["observations"]:
        tag = row["id"]
        require(row.get("object_id") in objects, f"{tag}: objet inconnu")
        require(row.get("type") in TYPES, f"{tag}: type invalide")
        require(row.get("certainty") in CERTAINTIES, f"{tag}: confiance invalide")
        require(row.get("evidence_kind") in KINDS, f"{tag}: provenance invalide")
        for key in ("entity_id", "statement", "source_url", "note"):
            require(isinstance(row.get(key), str), f"{tag}: {key} absent")
        require(row["statement"].strip(), f"{tag}: constat vide")
        obj = object_lookup[row["object_id"]]
        require(row.get("image") == obj["image"], f"{tag}: repère rattaché à une autre image")
        require(row.get("image_width") == obj["image_width"] and row.get("image_height") == obj["image_height"], f"{tag}: dimensions de référence différentes")
        actual_hash = hashlib.sha256((root / obj["image"]).read_bytes()).hexdigest()
        require(row.get("image_sha256") == actual_hash, f"{tag}: empreinte image différente")
        require(isinstance(row.get("observer"), str) and row["observer"].strip(), f"{tag}: auteur absent")
        require(isinstance(row.get("created"), str) and row["created"].strip(), f"{tag}: date absente")
        box = row.get("bbox")
        if box is not None:
            require(isinstance(box, list) and len(box) == 4, f"{tag}: repère invalide")
            require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in box), f"{tag}: coordonnées non normalisées")
            x, y, w, h = box
            require(w > 0 and h > 0 and x+w <= 1.000001 and y+h <= 1.000001, f"{tag}: repère hors image")
    for row in data["comparisons"]:
        tag = row["id"]
        require(row.get("from_id") in objects and row.get("to_id") in objects, f"{tag}: objet inconnu")
        require(row["from_id"] != row["to_id"], f"{tag}: auto-comparaison")
        require(row.get("operation_status") in STATUSES, f"{tag}: statut invalide")
        refs = row.get("observation_ids", [])
        require(isinstance(refs, list) and len(refs) >= 2 and all(r in observation_ids for r in refs), f"{tag}: références manquantes")
        referenced_objects = {lookup[r]["object_id"] for r in refs}
        require(referenced_objects == {row["from_id"], row["to_id"]}, f"{tag}: références ne couvrant pas la paire")
        require(row.get("correspondence_basis") in {"image", "catalogue"}, f"{tag}: base de correspondance absente")
        for ref in refs:
            observation = lookup[ref]
            expected_entity = row.get("from_entity") if observation["object_id"] == row["from_id"] else row.get("to_entity")
            require(observation["entity_id"] == expected_entity, f"{tag}: entité non reliée dans {ref}")
        for key in ("subject", "difference", "interpretation"):
            require(isinstance(row.get(key), str) and row[key].strip(), f"{tag}: {key} absent")
        require(isinstance(row.get("limitations"), list) and row["limitations"], f"{tag}: limites absentes")
    return data


def load_data(root=ROOT):
    return {name: json.loads((root / "data" / f"{name}.json").read_text()) for name in ("corpus", "observations", "comparisons")}


def build(check_only=False):
    data = validate(load_data())
    canonical = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    data["meta"] = {
        "schema_version": "1.0", "dataset_id": "mnemosyne-xanto-a-v0.1",
        "dataset_hash": hashlib.sha256(canonical).hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Mnemosyne · Les transformations du réemploi",
        "annotation_status": "Premier relevé par un assistant informé des sujets ; à examiner et corriger.",
        "limitations": [
            "Une source conservée et deux réemplois attribués ; aucun échantillon statistique.",
            "Les repères sont approximatifs. Les dimensions photographiques ne constituent pas une mesure physique.",
            "Une différence entre témoins ne prouve ni une opération de Xanto ni une réception historique.",
            "La comparaison avec Rome et le test d'une formalisation de la Pathosformel ne sont pas exécutés ici."
        ],
        "asset_hashes": {obj["id"]: hashlib.sha256((ROOT / obj["image"]).read_bytes()).hexdigest() for obj in data["corpus"]}
    }
    if not check_only:
        out = ROOT / "data" / "bundle.js"
        temporary = out.with_suffix(".js.tmp")
        temporary.write_text("// Generated by scripts/build_bundle.py; edit the JSON sources.\nwindow.MNEMOSYNE_DATA = " + json.dumps(data, ensure_ascii=True, indent=2) + ";\n")
        temporary.replace(out)
    print(f"Dossier vérifié : {len(data['corpus'])} objets, {len(data['observations'])} observations, {len(data['comparisons'])} comparaisons.")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Valider sans réécrire le bundle")
    options = parser.parse_args()
    try:
        build(options.check)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Erreur de dossier : {exc}\n")
