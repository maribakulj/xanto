#!/usr/bin/env python3
"""Témoin positif LACMA : rapport taille sur le plat / taille sur l'estampe, figure par figure.
Usage : rapports.py <dossier> <prefixe_annotateur>. Lit feuilles.csv, <prefixe>_bords.csv, <prefixe>_figures.csv.
Les colonnes de bords sont lues par position (G/gauche, D/droite, H/haut, B/bas)."""
import csv, math, sys
from pathlib import Path
d, pre = Path(sys.argv[1]), sys.argv[2]
F = {r["image"]: r for r in csv.DictReader(open(d / "feuilles.csv"))}
B = {}
for r in csv.reader(open(d / f"{pre}_bords.csv")):
    if r[0] == "image" or not r[0]: continue
    try: B[r[0]] = [float(x) for x in r[1:5]]
    except ValueError: B[r[0]] = None
g, dr, h, b = B["plat.jpg"]; sx, sy = 45 / (dr - g), 45 / (b - h)
out = []
for r in csv.DictReader(open(d / f"{pre}_figures.csv")):
    e = r["estampe"].strip(); img = e if e.endswith(".jpg") else e + ".jpg"
    lp = math.hypot((float(r["plat_x1"]) - float(r["plat_x2"])) * sx, (float(r["plat_y1"]) - float(r["plat_y2"])) * sy)
    bb, f = B.get(img), F.get(img)
    if not bb or not f:
        out.append((r["figure_id"], e, r["confiance"], lp, None, None)); continue
    ex = float(f["feuille_cm_largeur"]) / (bb[1] - bb[0]); ey = float(f["feuille_cm_hauteur"]) / (bb[3] - bb[2])
    le = math.hypot((float(r["est_x1"]) - float(r["est_x2"])) * ex, (float(r["est_y1"]) - float(r["est_y2"])) * ey)
    out.append((r["figure_id"], e, r["confiance"], lp, le, lp / le))
for o in out:
    print(f"{o[0]:5} {o[1]:6} {o[2]:7} plat {o[3]:6.2f} cm  " + (f"estampe {o[4]:6.2f} cm  r = {o[5]:.2f}" if o[4] else "estampe non mesurable"))
