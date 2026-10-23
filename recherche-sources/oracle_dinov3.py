#!/usr/bin/env python3
"""Oracle avec DINOv3 (PREINSCRIPTION_ORACLE_DINOV3_TOP100.md, test 1) : même protocole que oracle_rangs.py, vecteurs de la chaîne
retenue (DINOv3-L, vecteur de classe, découpe complétée en carré par le gris moyen, 384 px, couleur).
Usage : oracle_dinov3.py <dossier_prive>   (écrit resultats_oracle_dinov3.csv ; vecteurs des découpes en cache)"""
import csv, glob, os, sys
from pathlib import Path
import numpy as np, torch
import torchvision.transforms as T
from PIL import Image, ImageOps
from transformers import AutoModel
D = Path(sys.argv[1]).resolve()
dev = os.environ.get("DEV") or ("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
M = "facebook/dinov3-vitl16-pretrain-lvd1689m"; model = AutoModel.from_pretrained(M).to(dev).eval()
NORM = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]); TO_T = T.Compose([T.ToTensor(), NORM]); Image.MAX_IMAGE_PIXELS = None

def carre(im, sz):
    """Comme regions.py : complète en carré par le gris moyen, puis réduit à sz x sz."""
    w, h = im.size; s = max(w, h); g = int(np.asarray(ImageOps.grayscale(im)).mean())
    c = Image.new("RGB", (s, s), (g, g, g)); c.paste(im, ((s - w) // 2, (s - h) // 2))
    return c.resize((sz, sz), Image.BICUBIC)

@torch.no_grad()
def embed(im, boxes, mirror=False, bs=8):
    im = im.convert("RGB"); W, H = im.size
    if mirror: im = ImageOps.mirror(im)
    boxes = [(max(0, min(x0, W - 8)), max(0, min(y0, H - 8)), max(min(x1, W), min(x0, W - 8) + 8), max(min(y1, H), min(y0, H - 8) + 8)) for (x0, y0, x1, y1) in boxes]
    ims = [carre(im.crop(b), 384) for b in boxes]; out = []
    for i in range(0, len(ims), bs):
        x = torch.stack([TO_T(c) for c in ims[i:i + bs]]).to(dev)
        out.append(torch.nn.functional.normalize(model(pixel_values=x).last_hidden_state[:, 0], dim=-1).cpu().numpy())
    return np.concatenate(out)

def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); inter = ix * iy
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter + 1e-9)

orc = {}; vus = set()  # vus : les 49 requêtes du protocole (requetes_boites.csv en contient 163 depuis le 14/10)
for f in sorted(glob.glob(str(D / "?_oracle.csv"))):  # a_, b_, c_oracle.csv (pas resultats_oracle.csv)
    for r in csv.DictReader(open(f)):
        vus.add(r["requete"])
        if r["trouve"] != "non" and r["x0"]: orc[r["requete"]] = (r["estampe"], tuple(int(float(r[k])) for k in ("x0", "y0", "x1", "y1")), r["trouve"])
crops = []  # (image, box, etiquette)
for q, (img, b, _) in orc.items(): crops.append((img, b, "oracle:" + q))
for r in csv.DictReader(open(D / "oracle_temoins.csv")):
    if not r["x0"]: continue
    b = tuple(int(r[k]) for k in ("x0", "y0", "x1", "y1"))
    if b[2] - b[0] < 8 or b[3] - b[1] < 8: continue
    img = r["image"]
    if any(o[0].split("/")[-1] == img.split("/")[-1] and iou(o[1], b) > 0.5 for o in orc.values()): continue
    crops.append((img, b, "temoin"))
by = {}
for i, (img, b, _) in enumerate(crops): by.setdefault(img, []).append(i)
CACHE = D / "cache_oracle_dinov3l_384.npy"
if CACHE.exists(): V = np.load(CACHE)
else:
    V = np.zeros((len(crops), 1024), dtype=np.float32)
    for n, (img, idx) in enumerate(by.items()):
        path = D / img if (D / img).exists() else D / "connues" / img.split("/")[-1]
        V[idx] = embed(Image.open(path), [crops[i][1] for i in idx])
        if n % 100 == 0: print("images", n, "/", len(by), flush=True)
    np.save(CACHE, V)
labels = [c[2] for c in crops]
rows = []
for q in csv.DictReader(open(D / "requetes_boites.csv")):
    if q["requete"] not in vus: continue
    t = "oracle:" + q["requete"]
    if t not in labels:
        rows.append({"requete": q["requete"], "type": q["type"], "trouve_plat": q["trouve"], "oracle": "introuvable", "rang": "", "rang_meme_estampe": ""}); continue
    im = Image.open(D.parent / "corpus-images" / "rovigo" / q["photo"])
    crop = im.crop(tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1")))
    full = [(0, 0, crop.width, crop.height)]
    qv = np.concatenate([embed(crop, full), embed(crop, full, mirror=True)])
    s = (V @ qv.T).max(1); ti = labels.index(t)
    # les autres découpes oracle qui recouvrent la même figure ne sont pas des concurrents
    same = [i for i, (img, b, l) in enumerate(crops) if l.startswith("oracle:") and i != ti and img == crops[ti][0] and iou(b, crops[ti][1]) > 0.5]
    s[same] = -9
    rang = int((s > s[ti]).sum()) + 1
    # sensibilité (borne haute, non préinscrite) : meilleure découpe issue de n'importe quelle épreuve de la même estampe, quelle que soit la figure
    pre = crops[ti][0].split("/")[-1].split("__")[0] + "__"
    mine = np.array([c[0].split("/")[-1].startswith(pre) for c in crops])
    best = s[mine].max()
    rang_e = int((s[~mine] > best).sum()) + 1
    rows.append({"requete": q["requete"], "type": q["type"], "trouve_plat": q["trouve"], "oracle": orc[q["requete"]][2], "rang": rang, "rang_meme_estampe": rang_e})
with open(D / "resultats_oracle_dinov3.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
r = [x["rang"] for x in rows if x["rang"] != ""]
print("découpes :", len(crops), "dont témoins", labels.count("temoin"))
for k in (1, 10, 50): print(f"rappel@{k} : {sum(x <= k for x in r)}/{len(rows)}")
print("rang médian :", sorted(r)[len(r) // 2] if r else None)
re_ = [x["rang_meme_estampe"] for x in rows if x["rang_meme_estampe"] != ""]
for k in (1, 10, 50): print(f"sensibilité, même estampe, rappel@{k} : {sum(x <= k for x in re_)}/{len(rows)}")
