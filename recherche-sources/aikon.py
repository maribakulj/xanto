#!/usr/bin/env python3
"""Étape 1 du plan : AIKON tel quel (PREINSCRIPTION_AIKON.md). DINOv2 ViT-B/14 (vecteur de classe, image 224 x 224) -> 20 premières
-> reclassement SegSwap (poids hard_mining_neg5, images 244 x 244), comme le module `similarity` d'aikon-api.
Le calcul du score SegSwap reprend celui du dépôt d'origine (XiSHEN0220/SegSwap, licence MIT) et d'aikon-api.
Usage : aikon.py <dossier_prive> <dossier_segswap> [lot] [modele] [taille]   (dossier_segswap : transformer.py + hard_mining_neg5.pth ;
lot : mise_au_point par défaut, mise_au_point_nouvelles = seulement les requêtes de l'agrandissement Q055+ ; modele : facebook/dinov2-base par défaut ; taille de la présélection : 224 par défaut)
[canal] : rgb (défaut), gris, flou, trait ou fusion (étape 4, PREINSCRIPTION_CANAUX.md) ; ne touche que la présélection.
Écrit <dossier_prive>/resultats_aikon_<lot>.csv (ou resultats_aikon_<lot>_<modele>_<taille>[_<canal>].csv si modele/taille/canal changent)."""
import csv, sys
from pathlib import Path
from scipy.ndimage import gaussian_filter
import numpy as np, torch, torch.nn.functional as F, torchvision.models as tvm, torchvision.transforms as T
from PIL import Image, ImageFilter, ImageOps
from transformers import AutoModel

D = Path(sys.argv[1]).resolve(); S = Path(sys.argv[2]).resolve(); LOT = sys.argv[3] if len(sys.argv) > 3 else "mise_au_point"
MOD = sys.argv[4] if len(sys.argv) > 4 else "facebook/dinov2-base"; SZ = int(sys.argv[5]) if len(sys.argv) > 5 else 224
CANAL = sys.argv[6] if len(sys.argv) > 6 else "rgb"
BASE_TAG = "" if (MOD, SZ) == ("facebook/dinov2-base", 224) else f"_{MOD.split('/')[-1]}_{SZ}"
TAG = BASE_TAG if CANAL == "rgb" else f"_{MOD.split('/')[-1]}_{SZ}_{CANAL}"
sys.path.insert(0, str(S)); import transformer  # noqa: E402  (SegSwap, MIT)
dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
HERE = Path(__file__).resolve().parent
COS_TOPK, MAX_SIZE, STRIDE = 20, 244, 16  # aikon-api, similarity/lib/const.py
NORM = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
RESIZE = T.Resize((SZ, SZ), antialias=True); TO_T = T.Compose([T.ToTensor(), NORM])

def xdog(g):
    """Dessin au trait (XDoG, Winnemöller 2012), réglages fixés d'avance : sigma = max(0,7 ; taille/512), k = 1,6, tau = 0,98, eps = 0, phi = 200."""
    a = np.asarray(g, dtype=np.float32) / 255; s_ = max(0.7, SZ / 512)
    d = gaussian_filter(a, s_) - 0.98 * gaussian_filter(a, 1.6 * s_)
    e = np.where(d >= 0, 1.0, 1 + np.tanh(200 * d))
    return Image.fromarray((np.clip(e, 0, 1) * 255).astype(np.uint8))

def prep(im, canal, requete):
    """Transformation de présélection, appliquée après le redimensionnement. flou : seules les estampes sont floutées (tailles gommées)."""
    im = RESIZE(im)
    if canal == "rgb": return im
    g = ImageOps.grayscale(im)
    if canal == "flou" and not requete: g = g.filter(ImageFilter.GaussianBlur(SZ / 256))
    if canal == "trait": g = xdog(g)
    return g.convert("RGB")
T_SEG = T.Compose([T.Resize((MAX_SIZE, MAX_SIZE), antialias=True), T.ToTensor(), NORM])

dino = AutoModel.from_pretrained(MOD).to(dev).eval()  # dinov2-base : mêmes poids que torch.hub dinov2_vitb14

@torch.no_grad()
def cls(ims, canal="rgb", requete=False):
    out = []
    for i in range(0, len(ims), 32):
        x = torch.stack([TO_T(prep(im, canal, requete)) for im in ims[i:i + 32]]).to(dev)
        out.append(F.normalize(dino(pixel_values=x).last_hidden_state[:, 0], dim=-1).cpu())
    return torch.cat(out)

def load(p): return Image.open(p).convert("RGB")
def gpath(img): return D / img if (D / img).exists() else D / "connues" / img.split("/")[-1]

# --- galerie : un vecteur par image et par canal (cache ; les canaux manquants sont calculés en une seule lecture des images)
gal = list(csv.DictReader(open(D / "galerie.csv")))
CANAUX = ["rgb", "gris", "flou", "trait"] if CANAL == "fusion" else [CANAL]
def cache_of(c):
    if c == "rgb": return D / ("cache_aikon_dinov2.pt" if not BASE_TAG else f"cache_aikon{BASE_TAG}.pt")
    return D / f"cache_aikon_{MOD.split('/')[-1]}_{SZ}_{c}.pt"
G = {c: torch.load(cache_of(c)) for c in CANAUX if cache_of(c).exists()}
todo = [c for c in CANAUX if c not in G]
if todo:
    acc = {c: [] for c in todo}
    for k in range(0, len(gal), 64):
        ims = [load(gpath(g["image"])) for g in gal[k:k + 64]]
        for c in todo: acc[c].append(cls(ims, c))
        print("galerie", k + 64, flush=True)
    for c in todo: G[c] = torch.cat(acc[c]); torch.save(G[c], cache_of(c))

# --- SegSwap
param = torch.load(S / "hard_mining_neg5.pth", map_location="cpu", weights_only=True)
r = tvm.resnet50(weights=None)
backbone = torch.nn.Sequential(r.conv1, r.bn1, r.relu, r.maxpool, r.layer1, r.layer2, r.layer3)
backbone.load_state_dict(param["backbone"]); backbone = backbone.to(dev).eval()
enc = transformer.TransEncoder(feat_dim=1024, pos_weight=0.1, feat_weight=1, dropout=0.1, activation="relu", mode="small",
                               layer_type=["I", "C", "I", "C", "I", "N"], drop_feat=0.1)
enc.load_state_dict(param["encoder"]); enc = enc.to(dev).eval()
NF = MAX_SIZE // STRIDE
yg, xg = np.where(np.ones((NF, NF), dtype=bool))

@torch.no_grad()
def segswap(q, cands):
    """Score SegSwap de la requête q (PIL) contre chaque candidate (PIL), comme aikon-api segswap.compute_score."""
    t1 = T_SEG(q)[None].repeat(len(cands), 1, 1, 1).to(dev); t2 = torch.stack([T_SEG(c) for c in cands]).to(dev)
    f1 = F.normalize(backbone(t1)); f2 = F.normalize(backbone(t2))
    o1, o2 = enc(f1, f2); o1, o2 = o1.cpu(), o2.cpu(); f1, f2 = f1.cpu(), f2.cpu()
    m1, m2 = o1[:, 2:].numpy(), o2[:, 2:].numpy()
    flow12 = (o1.narrow(1, 0, 2).permute(0, 2, 3, 1) - 0.5) * 2  # masque cohérent par aller-retour du flot
    m1f = m1 * F.grid_sample(torch.from_numpy(m2.astype(np.float32)), flow12, mode="bilinear", align_corners=False).numpy()
    x2 = np.round(o1[:, 0, yg, xg].numpy() * (NF - 1)).astype(int); y2 = np.round(o1[:, 1, yg, xg].numpy() * (NF - 1)).astype(int)
    w = m1f[:, 0, yg, xg]
    scores = []
    for j in range(len(cands)):
        a = f1[j][:, yg, xg].T; b = f2[j][:, y2[j], x2[j]].T
        s = (a * b).sum(1).numpy() * w[j]
        best = {}
        for i in range(len(s)): best[(y2[j, i], x2[j, i])] = max(best.get((y2[j, i], x2[j, i]), 0), s[i])
        scores.append(sum(best.values()))
    return np.array(scores)

# --- requêtes du lot
lots = {r["requete"]: r["lot"] for r in csv.DictReader(open(HERE / "lots.csv"))}
comp = np.array([g["composition"] for g in gal])
rows = []
for q in csv.DictReader(open(D / "requetes_boites.csv")):
    if lots.get(q["requete"]) != LOT.removesuffix("_nouvelles") or (LOT.endswith("_nouvelles") and len(q["requete"]) < 4): continue
    im = load(D.parent / "corpus-images" / "rovigo" / q["photo"]).crop(tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1")))
    sens = [im, ImageOps.mirror(im)]
    C = {c: (G[c] @ cls(sens, c, requete=True).T).numpy() for c in CANAUX}  # (n_galerie, 2) par canal
    if CANAL == "fusion":  # fusion des rangs (reciprocal rank fusion, k = 60) ; le sens vient du canal couleur
        cos = sum(1 / (60 + np.argsort(np.argsort(-C[c].max(1))) + 1) for c in CANAUX); best_t = C["rgb"].argmax(1)
    else: best_t = C[CANAL].argmax(1); cos = C[CANAL].max(1)
    target = f"{q['bartsch_vol']}/{q['bartsch_n']}"; vrai = comp == target
    order = np.argsort(-cos)
    top = list(order[:COS_TOPK]); top_abs = [i for i in order if not vrai[i]][:COS_TOPK]
    pool = sorted(set(top) | set(top_abs))
    # sens retenu par la présélection pour chaque candidate
    sc = {}
    for t in (0, 1):
        idx = [i for i in pool if best_t[i] == t]
        if idx: sc.update(zip(idx, segswap(sens[t], [load(gpath(gal[i]["image"])) for i in idx])))
    rer = sorted(top, key=lambda i: -sc[i]) + list(order[COS_TOPK:])
    rang = next(k for k, i in enumerate(rer) if vrai[i]) + 1
    rang_cos = next(k for k, i in enumerate(order) if vrai[i]) + 1
    sv = max([sc[i] for i in top if vrai[i]], default="")
    rows.append({"requete": q["requete"], "bartsch": target, "type": q["type"], "trouve": q["trouve"], "rang_cosinus": rang_cos,
                 "rang_aikon": rang, "sens": "miroir" if best_t[rer[rang - 1]] == 1 else "endroit",
                 "score_vraie": round(float(sv), 2) if sv != "" else "", "score_premier": round(float(sc[rer[0]]), 2),
                 "score_absente": round(float(max(sc[i] for i in top_abs)), 2)})
    print(rows[-1], flush=True)
with open(D / f"resultats_aikon_{LOT}{TAG}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
r = [x["rang_aikon"] for x in rows]
for k in (1, 10, 50): print(f"rappel@{k} : {sum(x <= k for x in r)}/{len(rows)}")
print("rang médian :", sorted(r)[len(r) // 2])
