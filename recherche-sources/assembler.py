#!/usr/bin/env python3
"""Assemble galerie.csv (image,composition) et requetes_boites.csv dans le dossier privé.
Usage : assembler.py <dossier_prive>"""
import csv, sys, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; D = Path(sys.argv[1]).resolve(); E = D.parent / "corpus-images" / "estampes"
(D / "connues").mkdir(exist_ok=True)
rows, met_connus = [], set()
for r in csv.DictReader(open(E / "index.csv")):
    f = E / r["local_path"]
    if not f.exists(): continue
    shutil.copy(f, D / "connues" / f.name) if not (D / "connues" / f.name).exists() else None
    rows.append({"image": f"connues/{f.name}", "composition": f"{r['tib_vol']}/{r['tib_n'].lstrip('0')}", "musee": r["museum"]})
    if "Metropolitan" in r["museum"] or r["museum"] == "Met": met_connus.add(str(r["object_id"]))
n_met = 0
for r in csv.DictReader(open(D / "galerie_met.csv")):
    if r["object_id"] in met_connus or not (D / r["fichier"]).exists(): continue
    rows.append({"image": r["fichier"], "composition": f"met:{r['object_id']}", "musee": "Met"}); n_met += 1
with open(D / "galerie.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["image", "composition", "musee"]); w.writeheader(); w.writerows(rows)
q = {r["requete"]: r for r in csv.DictReader(open(ROOT / "recherche-sources" / "requetes.csv"))}
out = []
for p in sorted(D.glob("boites_*_boites.csv")):
    for b in csv.DictReader(open(p)):
        out.append({**b, "plat_id": q[b["requete"]]["plat_id"], "bartsch_vol": q[b["requete"]]["bartsch_vol"], "bartsch_n": q[b["requete"]]["bartsch_n"]})
out = [o for o in out if o["trouve"] != "non"]
with open(D / "requetes_boites.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(sorted(out, key=lambda o: o["requete"]))
print(len(rows), "images (", n_met, "distracteurs Met ) ;", len(out), "requêtes utilisables")
