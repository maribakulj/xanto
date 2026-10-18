#!/usr/bin/env python3
"""Vecteurs de la galerie agrandie (galerie_plus.py), calculés exactement comme pour la galerie d'origine :
1. figures humaines par Grounding DINO (invite « person », seuil 0,30, image réduite à 1200 px ; comme oracle_detection.py) ;
2. régions : grille 2 x 2 et 3 x 3 + boîtes « person » agrandies de 10 % (côté >= 32 px) (comme regions.py) ;
3. vecteur de classe DINOv3 large des régions complétées en carré gris, 384 px (comme regions.py) ;
4. vecteur de l'image entière réduite à 512 x 512 (comme aikon.py, canal rgb).
Fusionne plus/galerie_plus_*.csv en plus/galerie_plus.csv (sans les estampes du Rijksmuseum déjà dans galerie.csv).
Caches par paquets, reprise possible. Usage : galerie_plus_vecteurs.py <dossier_prive_recherche_sources>"""
import csv, glob, re, sys
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F, torchvision.transforms as T
from PIL import Image, ImageOps
from transformers import AutoModel, AutoProcessor, AutoModelForZeroShotObjectDetection
D = Path(sys.argv[1]).resolve(); P = D / "plus"; Image.MAX_IMAGE_PIXELS = None
import os
dev = os.environ.get("DEV") or ("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
NORM = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]); TO_T = T.Compose([T.ToTensor(), NORM])
MOD, PAQUET = "facebook/dinov3-vitl16-pretrain-lvd1689m", 2000

# --- 0. fusion
deja = {re.sub(r".*rijks_", "", g["image"]).removesuffix(".jpg") for g in csv.DictReader(open(D / "galerie.csv")) if "rijks_" in g["image"]}
rows, vus = [], set()
for f in sorted(glob.glob(str(P / "galerie_plus_*.csv"))):
    for r in csv.DictReader(open(f)):
        if r["composition"] in vus or (r["musee"] == "Rijksmuseum" and r["date"] in deja): continue
        vus.add(r["composition"]); rows.append(r)
GP = P / "galerie_plus.csv"
with open(GP, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["image", "composition", "musee", "titre", "artiste", "date"]); w.writeheader(); w.writerows(rows)
print(len(rows), "estampes ajoutées", flush=True)
def load(img): return Image.open(D / img).convert("RGB")

# --- 1. personnes
PER = P / "personnes_plus.csv"; fait = {r["image"] for r in csv.DictReader(open(PER))} if PER.exists() else set()
todo = [r["image"] for r in rows if r["image"] not in fait]
if todo:
    M = "IDEA-Research/grounding-dino-base"
    proc = AutoProcessor.from_pretrained(M); gd = AutoModelForZeroShotObjectDetection.from_pretrained(M).to(dev).eval()
    fh = open(PER, "a", newline=""); w = csv.writer(fh)
    if not fait: w.writerow(["image", "x0", "y0", "x1", "y1", "score"])
    for k, img in enumerate(todo):
        full = load(img); im = full.copy(); im.thumbnail((1200, 1200))
        inp = proc(images=im, text="person.", return_tensors="pt").to(dev)
        with torch.no_grad(): o = gd(**inp)
        res = proc.post_process_grounded_object_detection(o, inp.input_ids, threshold=0.30, text_threshold=0.25, target_sizes=[im.size[::-1]])[0]
        sx = full.size[0] / im.size[0]
        out = [[img] + [round(float(v) * sx) for v in b] + [round(float(s), 3)] for b, s in zip(res["boxes"], res["scores"])]
        w.writerows(out or [[img, "", "", "", "", ""]]); fh.flush()
        if k % 100 == 0: print("personnes", k, len(todo), flush=True)
    del gd; fh.close()

# --- 2. régions (mêmes règles que regions.py)
pers = {}
for r in csv.DictReader(open(PER)):
    if r["x0"]: pers.setdefault(r["image"], []).append(tuple(float(r[k]) for k in ("x0", "y0", "x1", "y1")))
regs = []
for i, g in enumerate(rows):
    W, H = Image.open(D / g["image"]).size
    for n in (2, 3):
        for a in range(n):
            for b in range(n): regs.append((i, f"grille{n}", round(b * W / n), round(a * H / n), round((b + 1) * W / n), round((a + 1) * H / n)))
    for x0, y0, x1, y1 in pers.get(g["image"], []):
        mx, my = 0.1 * (x1 - x0), 0.1 * (y1 - y0)
        x0, y0, x1, y1 = max(0, x0 - mx), max(0, y0 - my), min(W, x1 + mx), min(H, y1 + my)
        if min(x1 - x0, y1 - y0) >= 32: regs.append((i, "personne", round(x0), round(y0), round(x1), round(y1)))
with open(P / "regions_plus.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["image", "type", "x0", "y0", "x1", "y1"]); w.writerows(regs)
print(len(regs), "régions", flush=True)

# --- 3 et 4. vecteurs DINOv3 large
dino = AutoModel.from_pretrained(MOD).to(dev).eval()
@torch.no_grad()
def cls(ims):
    out = []
    for i in range(0, len(ims), 8):
        x = torch.stack([TO_T(im) for im in ims[i:i + 8]]).to(dev)
        out.append(F.normalize(dino(pixel_values=x).last_hidden_state[:, 0], dim=-1).cpu())
    return torch.cat(out)
def carre(im, sz):
    w, h = im.size; s = max(w, h); g = int(np.asarray(ImageOps.grayscale(im)).mean())
    c = Image.new("RGB", (s, s), (g, g, g)); c.paste(im, ((s - w) // 2, (s - h) // 2))
    return c.resize((sz, sz), Image.BICUBIC)
CE = P / "cache_entiere_plus_512.pt"
if not CE.exists():
    rs = T.Resize((512, 512), antialias=True); acc = []
    for k in range(0, len(rows), 64): acc.append(cls([rs(load(g["image"])) for g in rows[k:k + 64]]))
    torch.save(torch.cat(acc), CE); print("images entières", len(rows), flush=True)
for k in range(0, len(regs), PAQUET):
    p = P / f"cache_regions_plus_384_{k // PAQUET:03d}.pt"
    if p.exists(): continue
    part, cur, ims = regs[k:k + PAQUET], None, []
    for i, _, x0, y0, x1, y1 in part:
        if i != cur: cur, im = i, load(rows[i]["image"])
        ims.append(carre(im.crop((x0, y0, x1, y1)), 384))
    torch.save(cls(ims), p); print("régions", k + len(part), "/", len(regs), flush=True)
print("fini")
