#!/usr/bin/env python3
"""Rassemble les données du dépôt en un seul fichier JavaScript lu par la démo (fonctionne en file://).

Sources : data/pieces.csv, data/emprunts.csv, demo/data/litterature.json,
analyses/resultats.json (si présent), tests-echelle/*.csv et tests-echelle/cas.json (si présent).
Copie aussi, depuis le dossier privé, les images utiles dans demo/assets/ (non versionné).
"""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
PRIVATE = Path.home() / "Documents/Codex/2026-10-08-continuation-claude"


def read_csv(path):
    return list(csv.DictReader(open(path))) if path.exists() else []


def main():
    data = {
        "pieces": read_csv(ROOT / "data/pieces.csv"),
        "emprunts": read_csv(ROOT / "data/emprunts.csv"),
        "litterature": json.load(open(DEMO / "data/litterature.json")) if (DEMO / "data/litterature.json").exists() else None,
        "analyses": json.load(open(DEMO / "data/tests_demo.json")) if (DEMO / "data/tests_demo.json").exists() else None,
        "echelle": json.load(open(ROOT / "tests-echelle/cas.json")) if (ROOT / "tests-echelle/cas.json").exists() else None,
        "estampes": read_csv(PRIVATE / "corpus-images/estampes/index.csv"),
        "titres": read_csv(ROOT / "data/titres_estampes.csv"),
    }
    # Images : on ne copie que celles que la démo affiche (cas d'échelle, vignettes de plats).
    assets = DEMO / "assets"
    assets.mkdir(exist_ok=True)
    wanted = set()
    if data["echelle"]:
        for cas in data["echelle"]["cas"]:
            for t in cas["temoins"]:
                wanted.add(t["image"])
    rovigo = PRIVATE / "corpus-images/rovigo"
    thumbs = {}
    if (rovigo / "index.csv").exists():
        for row in read_csv(rovigo / "index.csv"):
            if row.get("local_path") and Path(row["local_path"]).exists():
                thumbs.setdefault(row["id"], Path(row["local_path"]).name)
                wanted.add(str(Path(row["local_path"])))
    copied = 0
    for src in wanted:
        p = Path(src)
        if not p.is_absolute():
            p = PRIVATE / src
        if p.exists() and not (assets / p.name).exists():
            shutil.copy2(p, assets / p.name); copied += 1
    data["vignettes"] = thumbs
    out = DEMO / "data/bundle.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("window.XANTO = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print(f"bundle : {len(data['pieces'])} pièces, {len(data['emprunts'])} emprunts, "
          f"litterature={'oui' if data['litterature'] else 'non'}, analyses={'oui' if data['analyses'] else 'non'}, "
          f"echelle={'oui' if data['echelle'] else 'non'} ; {copied} images copiées dans demo/assets/")


if __name__ == "__main__":
    main()
