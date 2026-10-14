#!/usr/bin/env python3
"""Test de l'oracle (PREINSCRIPTION_ORACLE.md), étape A : détecte les figures humaines (Grounding DINO, invite « person »,
seuil 0,30) dans toutes les images de la galerie ; écrit <dossier>/oracle_temoins.csv (image,x0,y0,x1,y1,score). Reprend là où il s'est arrêté.
Usage : oracle_detection.py <dossier_prive> [limite]"""
import csv, sys
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
D = Path(sys.argv[1]).resolve(); LIM = int(sys.argv[2]) if len(sys.argv) > 2 else None
dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
M = "IDEA-Research/grounding-dino-base"
proc = AutoProcessor.from_pretrained(M); model = AutoModelForZeroShotObjectDetection.from_pretrained(M).to(dev).eval()
out = D / "oracle_temoins.csv"
done = {r["image"] for r in csv.DictReader(open(out))} if out.exists() else set()
fh = open(out, "a", newline=""); w = csv.writer(fh)
if not done: w.writerow(["image", "x0", "y0", "x1", "y1", "score"])
gal = [g["image"] for g in csv.DictReader(open(D / "galerie.csv"))][:LIM]
for i, img in enumerate(gal):
    if img in done: continue
    im = Image.open(D / img).convert("RGB"); im.thumbnail((1200, 1200))
    inp = proc(images=im, text="person.", return_tensors="pt").to(dev)
    with torch.no_grad(): o = model(**inp)
    res = proc.post_process_grounded_object_detection(o, inp.input_ids, threshold=0.30, text_threshold=0.25, target_sizes=[im.size[::-1]])[0]
    sx = Image.open(D / img).size[0] / im.size[0]
    rows = [[img] + [round(float(v) * sx) for v in b] + [round(float(s), 3)] for b, s in zip(res["boxes"], res["scores"])]
    w.writerows(rows or [[img, "", "", "", "", ""]]); fh.flush()
    if i % 50 == 0: print(i, len(gal), len(rows), flush=True)
