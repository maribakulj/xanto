#!/usr/bin/env python3
"""Tire au sort les requêtes de l'essai : emprunts du catalogue de Rovigo dont la source a une épreuve libre
dans data/estampes_sources.csv et dont le plat a une photographie. Au plus 2 par estampe, plats distincts, graine fixe.
Usage : selection_requetes.py <emprunts_complet_avec_phrases.csv> <dossier_photos_rovigo> > requetes.csv"""
import csv, os, random, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
known = {(r["tib_vol"], r["tib_n"].lstrip("0")) for r in csv.DictReader(open(f"{ROOT}/data/estampes_sources.csv"))}
photos = defaultdict(list)
for f in sorted(os.listdir(sys.argv[2])): photos[f.split("__")[0]].append(f)
cand = defaultdict(list)
for r in csv.DictReader(open(sys.argv[1])):
    k = (r["bartsch_vol"], r["bartsch_n"].lstrip("0"))
    if k in known and r["id"] in photos: cand[k].append(r)
rng = random.Random(13102026); used = set()
w = csv.writer(sys.stdout); w.writerow(["requete", "plat_id", "titolo", "data", "bartsch_vol", "bartsch_n", "inversione", "photos", "phrase"])
n = 0
for k in sorted(cand):
    rows = cand[k][:]; rng.shuffle(rows); took = 0
    for r in rows:
        if took == 2: break
        if r["id"] in used: continue
        used.add(r["id"]); took += 1; n += 1
        w.writerow([f"Q{n:02d}", r["id"], r["titolo"], r["data"], k[0], k[1], r["inversione"], ";".join(photos[r["id"]]), r["phrase"]])
