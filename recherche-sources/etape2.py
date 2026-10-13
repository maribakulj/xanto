#!/usr/bin/env python3
"""Étape 2 (PREINSCRIPTION_ETAPE2.md) : reclasse les 50 premiers candidats de l'étape 1 par le nombre de
correspondances locales DINOv2 mutuelles et spatialement cohérentes (RANSAC sur une similitude).
Usage : etape2.py <dossier_prive>   (réutilise cache_dinov2-base.npz de recherche.py)"""
import csv, math, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModel

D = Path(sys.argv[1]).resolve(); dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
model = AutoModel.from_pretrained("facebook/dinov2-base").to(dev).eval(); proc = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
MEAN, STD = np.array(proc.image_mean), np.array(proc.image_std); P = 14

def tens(im):
    a = (np.asarray(im.convert("L").convert("RGB"), dtype=np.float32) / 255 - MEAN) / STD
    return torch.from_numpy(a.transpose(2, 0, 1).astype(np.float32))[None].to(dev)

SIZE = 224
MEAN_T = torch.tensor(proc.image_mean, dtype=torch.float32, device=dev).view(1, 3, 1, 1)
STD_T = torch.tensor(proc.image_std, dtype=torch.float32, device=dev).view(1, 3, 1, 1)

@torch.no_grad()
def cls_gpu(im, mirror=False):
    """Même vecteur de requête que recherche.py (redimensionnement sur la carte graphique)."""
    g = torch.from_numpy(np.asarray(im.convert("L"), dtype=np.float32) / 255).to(dev)
    if mirror: g = torch.flip(g, dims=[1])
    x = torch.nn.functional.interpolate(g[None, None], size=(SIZE, SIZE), mode="bicubic", antialias=True, align_corners=False).clamp(0, 1).repeat(1, 3, 1, 1)
    return torch.nn.functional.normalize(model(pixel_values=(x - MEAN_T) / STD_T).last_hidden_state[:, 0], dim=-1).cpu().numpy()

@torch.no_grad()
def cls(ims):
    x = torch.cat([tens(i.resize((224, 224), Image.BICUBIC)) for i in ims])
    return torch.nn.functional.normalize(model(pixel_values=x).last_hidden_state[:, 0], dim=-1).cpu().numpy()

@torch.no_grad()
def patches(im, side):
    s = side / max(im.size); w, h = max(P, round(im.width * s / P) * P), max(P, round(im.height * s / P) * P)
    f = model(pixel_values=tens(im.resize((w, h), Image.BICUBIC))).last_hidden_state[0, 1:]
    gw, gh = w // P, h // P
    f = torch.nn.functional.normalize(f[: gw * gh], dim=-1).cpu().numpy()
    xy = np.stack(np.meshgrid(np.arange(gw), np.arange(gh)), -1).reshape(-1, 2).astype(np.float64)
    return f, xy

def ransac(a, b, rng, iters=2000, thr=1.5):
    """a, b : points appariés (requête, estampe). Similitude b = s R a + t. Renvoie le nombre d'inliers."""
    n = len(a)
    if n < 3: return n
    A, B = a[:, 0] + 1j * a[:, 1], b[:, 0] + 1j * b[:, 1]
    I = rng.integers(0, n, size=(iters, 2)); I = I[A[I[:, 0]] != A[I[:, 1]]]
    m = (B[I[:, 0]] - B[I[:, 1]]) / (A[I[:, 0]] - A[I[:, 1]]); t = B[I[:, 0]] - m * A[I[:, 0]]
    best = 0
    for k in range(0, len(m), 250):
        best = max(best, int((np.abs(m[k:k + 250, None] * A[None] + t[k:k + 250, None] - B[None]) < thr).sum(1).max()))
    return best

def score(qf, qxy, gf, gxy, rng):
    S = qf @ gf.T; a2b = S.argmax(1); b2a = S.argmax(0)
    mut = np.where(b2a[a2b] == np.arange(len(qf)))[0]
    return ransac(qxy[mut], gxy[a2b[mut]], rng)

gal = list(csv.DictReader(open(D / "galerie.csv"))); comp = np.array([g["composition"] for g in gal])
z = np.load(D / "cache_dinov2-base.npz"); Vt = torch.from_numpy(z["V"].astype(np.float32)); owner = z["owner"]
gcache = {}
rows = []
for q in csv.DictReader(open(D / "requetes_boites.csv")):
    im = Image.open(D.parent / "corpus-images" / "rovigo" / q["photo"]).convert("RGB")
    crop = im.crop(tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1")))
    qv = torch.from_numpy(np.concatenate([cls_gpu(crop), cls_gpu(crop, mirror=True)]))
    s = (Vt @ qv.T).max(1).values.numpy(); best = np.full(len(gal), -9.0); np.maximum.at(best, owner, s)
    order1 = list(np.argsort(-best))
    rng = np.random.default_rng(13102026)
    q1, q2 = patches(crop, 448), patches(ImageOps.mirror(crop), 448)
    sc = {}
    for gi in order1[:50]:
        if gi not in gcache: gcache[gi] = patches(Image.open(D / gal[gi]["image"]).convert("RGB"), 896)
        gf, gxy = gcache[gi]
        sc[gi] = max(score(*q1, gf, gxy, rng), score(*q2, gf, gxy, rng))
    order2 = sorted(order1[:50], key=lambda g: (-sc[g], order1.index(g))) + order1[50:]
    truth = f"{q['bartsch_vol']}/{q['bartsch_n']}"; tidx = set(np.where(comp == truth)[0])
    r1 = min(order1.index(i) for i in tidx) + 1; r2 = min(order2.index(i) for i in tidx) + 1
    rows.append({"requete": q["requete"], "bartsch": truth, "type": q["type"], "trouve": q["trouve"], "rang_etape1": r1, "rang_etape2": r2,
                 "score_vraie": max(sc.get(i, -1) for i in tidx), "score_premier": sc[order2[0]], "top5": ";".join(gal[i]["image"] for i in order2[:5])})
    print(q["requete"], r1, r2, flush=True)
with open(D / "resultats_etape2.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for k in (1, 10, 50):
    print(f"rappel@{k} : étape 1 {sum(r['rang_etape1'] <= k for r in rows)}/{len(rows)}, étape 2 {sum(r['rang_etape2'] <= k for r in rows)}/{len(rows)}")
