#!/usr/bin/env python3
"""Agrandissement du jeu de paires (PREINSCRIPTION_PAIRES.md). Tire de nouvelles requêtes parmi les emprunts du catalogue de Rovigo
dont la source a une épreuve dans data/estampes_sources.csv et dont le plat a une photographie, en excluant les plats déjà tirés
dans requetes.csv. Au plus 8 nouvelles par estampe, plats distincts, graine fixe. Le lot de chaque requête est celui de son estampe
dans lots.csv ; une estampe absente de lots.csv va au lot d'évaluation.
Usage : selection_requetes2.py <emprunts_complet_avec_phrases.csv> <dossier_photos_rovigo> > requetes2.csv"""
import csv, os, random, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); HERE = os.path.dirname(os.path.abspath(__file__))
known = {(r["tib_vol"], r["tib_n"].lstrip("0")) for r in csv.DictReader(open(f"{ROOT}/data/estampes_sources.csv"))}
used = {r["plat_id"] for r in csv.DictReader(open(f"{HERE}/requetes.csv"))}
lots = {r["bartsch"]: r["lot"] for r in csv.DictReader(open(f"{HERE}/lots.csv"))}
photos = defaultdict(list)
for f in sorted(os.listdir(sys.argv[2])): photos[f.split("__")[0]].append(f)
cand = defaultdict(list)
for r in csv.DictReader(open(sys.argv[1])):
    k = (r["bartsch_vol"], r["bartsch_n"].lstrip("0"))
    if k in known and r["id"] in photos and r["id"] not in used: cand[k].append(r)
rng = random.Random(15102026); taken = set()
w = csv.writer(sys.stdout); w.writerow(["requete", "plat_id", "titolo", "data", "bartsch_vol", "bartsch_n", "inversione", "photos", "phrase", "lot"])
n = 54
for k in sorted(cand):
    rows = cand[k][:]; rng.shuffle(rows); took = 0
    for r in rows:
        if took == 8: break
        if (r["id"], k) in taken: continue
        taken.add((r["id"], k)); took += 1; n += 1
        w.writerow([f"Q{n:03d}", r["id"], r["titolo"], r["data"], k[0], k[1], r["inversione"], ";".join(photos[r["id"]]), r["phrase"],
                    lots.get(f"{k[0]}/{k[1]}", "evaluation")])
