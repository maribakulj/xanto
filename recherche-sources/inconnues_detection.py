#!/usr/bin/env python3
"""Recherche de sources inconnues (PROTOCOLE_INCONNUES.md), étape A : figures humaines des plats choisis, détectées par
Grounding DINO (invite « person », seuil 0,30, comme pour la galerie). On garde les 5 plus grandes boîtes dont le petit côté
dépasse 8 % de la photo, plus la scène entière (requête « composition »).
Usage : inconnues_detection.py <dossier_prive>   → écrit <dossier_prive>/recherche-sources/inconnues_requetes.csv"""
import csv, os, sys
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
P = Path(sys.argv[1]).resolve(); PH = P / "corpus-images" / "rovigo"
# plats sans emprunt (315, salière, et 1175, décor sans scène, retirés après la planche de contrôle)
# plats sans emprunt Bartsch dans le catalogue de Rovigo, sans source citée ; puis « invention de Xanto » selon la fiche
SANS = "230 608 883 241 859 504 173 305 205 288 107 129 123 565 499 373 947 808 1163".split()
INVENTION = "383 1347 1179 709".split()
# témoins : la fiche cite une gravure sans numéro Bartsch (contrôle de bon fonctionnement, pas une découverte)
TEMOINS = "942 1103 1144 629 435 466".split()
dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
M = "IDEA-Research/grounding-dino-base"
proc = AutoProcessor.from_pretrained(M); model = AutoModelForZeroShotObjectDetection.from_pretrained(M).to(dev).eval()
photos = {}
for f in sorted(os.listdir(PH)): photos.setdefault(f.split("__")[0], f)  # première vue (-01 : le recto peint)
photos["499"] = "499__119.-03.jpg"  # la première vue de 499 est le revers (planche de contrôle)
rows = []
for groupe, ids in (("sans_source", SANS), ("invention", INVENTION), ("temoin", TEMOINS)):
    for pid in ids:
        f = photos[pid]; full = Image.open(PH / f).convert("RGB"); W, H = full.size
        im = full.copy(); im.thumbnail((1200, 1200)); sx = W / im.size[0]
        inp = proc(images=im, text="person.", return_tensors="pt").to(dev)
        with torch.no_grad(): o = model(**inp)
        res = proc.post_process_grounded_object_detection(o, inp.input_ids, threshold=0.30, text_threshold=0.25, target_sizes=[im.size[::-1]])[0]
        bx = [[round(float(v) * sx) for v in b] for b in res["boxes"]]
        bx = [b for b in bx if min(b[2] - b[0], b[3] - b[1]) >= 0.08 * min(W, H)]
        bx = sorted(bx, key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))[:5]
        rows.append([f"{pid}-scene", groupe, pid, f, 0, 0, W, H, "composition"])
        rows += [[f"{pid}-f{k + 1}", groupe, pid, f, *b, "figure"] for k, b in enumerate(bx)]
        print(pid, groupe, len(bx), flush=True)
with open(P / "recherche-sources" / "inconnues_requetes.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["requete", "groupe", "plat_id", "photo", "x0", "y0", "x1", "y1", "type"]); w.writerows(rows)
print(len(rows), "requêtes")
