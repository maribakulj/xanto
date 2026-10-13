#!/usr/bin/env python3
"""Essai de recherche automatique de sources (méthode fixée dans PREINSCRIPTION.md).
Étape 1 : galerie -> fenêtres -> vecteurs DINOv2 (cache). Étape 2 : requêtes (figure + miroir) -> rang de la vraie estampe.
Usage : recherche.py <dossier_prive> [modele]   (modele : facebook/dinov2-base par défaut)
Lit <dossier_prive>/galerie.csv (image,composition) et <dossier_prive>/requetes_boites.csv ; écrit resultats_<modele>.csv."""
import csv, math, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModel, CLIPModel, CLIPProcessor

D = Path(sys.argv[1]).resolve(); MOD = sys.argv[2] if len(sys.argv) > 2 else "facebook/dinov2-base"
tag = MOD.split("/")[-1]
dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
if "clip" in MOD:
    model = CLIPModel.from_pretrained(MOD).to(dev).eval(); proc = CLIPProcessor.from_pretrained(MOD).image_processor
    embed_fn = lambda px: model.get_image_features(pixel_values=px)
else:
    model = AutoModel.from_pretrained(MOD).to(dev).eval(); proc = AutoImageProcessor.from_pretrained(MOD)
    embed_fn = lambda px: model(pixel_values=px).last_hidden_state[:, 0]
SIZE = 224

def prep(im):
    im = im.convert("L").convert("RGB").resize((SIZE, SIZE), Image.BICUBIC)
    a = (np.asarray(im, dtype=np.float32) / 255 - np.array(proc.image_mean)) / np.array(proc.image_std)
    return torch.from_numpy(a.transpose(2, 0, 1).astype(np.float32))

@torch.no_grad()
def embed(ims, bs=64):
    out = []
    for i in range(0, len(ims), bs):
        v = embed_fn(torch.stack([prep(x) for x in ims[i:i + bs]]).to(dev))
        out.append(torch.nn.functional.normalize(v, dim=-1).cpu().numpy().astype(np.float16))
    return np.concatenate(out)

def fenetres(W, H):
    boxes = [(0, 0, W, H)]
    for fh in (0.9, 0.6, 0.4):
        h = fh * H
        for a in (0.5, 0.8, 1.2):
            w = min(a * h, W)
            sx, sy = max(w / 3, 1), max(h / 3, 1)
            nx, ny = int(math.floor((W - w) / sx)) + 1, int(math.floor((H - h) / sy)) + 1
            for j in range(ny):
                for i in range(nx):
                    boxes.append((int(i * sx), int(j * sy), int(i * sx + w), int(j * sy + h)))
    return boxes

gal = list(csv.DictReader(open(D / "galerie.csv")))
cache = D / f"cache_{tag}.npz"; parts = D / f"cache_{tag}"; parts.mkdir(exist_ok=True)
if cache.exists():
    z = np.load(cache); V, owner = z["V"], z["owner"]
else:
    # une sauvegarde par estampe : le calcul reprend là où il s'est arrêté
    for gi, g in enumerate(gal):
        fp = parts / f"{gi:05d}.npy"
        if fp.exists(): continue
        im = Image.open(D / g["image"]); im.thumbnail((1200, 1200))
        np.save(fp, embed([im.crop(b) for b in fenetres(*im.size)]))
        if gi % 50 == 0: print(gi, len(gal), file=sys.stderr, flush=True)
    Vs = [np.load(parts / f"{gi:05d}.npy") for gi in range(len(gal))]
    V = np.concatenate(Vs); owner = np.concatenate([[gi] * len(v) for gi, v in enumerate(Vs)]).astype(int)
    np.savez(cache, V=V, owner=owner)
print("fenêtres :", len(V), "images :", len(gal), file=sys.stderr)
Vt = torch.from_numpy(V.astype(np.float32))
comp = np.array([g["composition"] for g in gal])
rows = []
for q in csv.DictReader(open(D / "requetes_boites.csv")):
    im = Image.open(D.parent / "corpus-images" / "rovigo" / q["photo"]).convert("RGB")
    crop = im.crop(tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1")))
    qv = torch.from_numpy(embed([crop, ImageOps.mirror(crop)]).astype(np.float32))
    s = (Vt @ qv.T).max(1).values.numpy()
    best = np.full(len(gal), -9.0); np.maximum.at(best, owner, s)
    order = np.argsort(-best)
    truth = f"{q['bartsch_vol']}/{q['bartsch_n']}"
    ranks = [int(np.where(order == i)[0][0]) + 1 for i in np.where(comp == truth)[0]]
    t, N = len(ranks), len(gal)
    k10 = min(10, N); chance10 = 1 - math.comb(N - t, k10) / math.comb(N, k10) if t else 0
    rows.append({**{k: q[k] for k in ("requete", "plat_id", "bartsch_vol", "bartsch_n", "type", "trouve")},
                 "rang": min(ranks) if ranks else "", "n_epreuves": t, "hasard_top10": round(chance10, 4),
                 "top5": ";".join(gal[i]["image"] for i in order[:5])})
with open(D / f"resultats_{tag}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
r = [x["rang"] for x in rows if x["rang"] != ""]
for k in (1, 10, 50): print(f"rappel@{k} : {sum(x <= k for x in r)}/{len(rows)}")
print("rang médian :", sorted(r)[len(r) // 2])
