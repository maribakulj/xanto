#!/usr/bin/env python3
"""Étape 3 du plan (PREINSCRIPTION_REGIONS.md) : régions côté estampe, sans déformation.
Régions de chaque image de la galerie = grille 2 x 2 et 3 x 3 + boîtes « person » de Grounding DINO (oracle_temoins.csv) agrandies de 10 %,
complétées en carré (bordure du gris moyen), 384 px, vecteur de classe DINOv3 large. Score d'une estampe = max(score de la base
sur l'image entière, meilleur score de ses régions), figure à l'endroit et en miroir ; 20 premières reclassées par SegSwap comme dans aikon.py.
Usage : regions.py <dossier_prive> <dossier_segswap> [lot]   (étape longue : vecteurs des régions mis en cache par paquets, reprise possible)
Écrit <dossier_prive>/resultats_regions_<lot>.csv."""
import csv, os, sys
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F, torchvision.models as tvm, torchvision.transforms as T
from PIL import Image, ImageOps
from transformers import AutoModel

D = Path(sys.argv[1]).resolve(); S = Path(sys.argv[2]).resolve(); LOT = sys.argv[3] if len(sys.argv) > 3 else "mise_au_point"
sys.path.insert(0, str(S)); import transformer  # noqa: E402  (SegSwap, MIT)
dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
HERE = Path(__file__).resolve().parent
MOD, SZ_BASE, SZ_REG, PAQUET = "facebook/dinov3-vitl16-pretrain-lvd1689m", 512, 384, 2000
COS_TOPK, MAX_SIZE, STRIDE = 20, 244, 16
NORM = T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]); TO_T = T.Compose([T.ToTensor(), NORM])
Image.MAX_IMAGE_PIXELS = None

def carre(im, sz):
    """Complète en carré par une bordure du gris moyen (sans déformation), puis réduit à sz x sz."""
    w, h = im.size; s = max(w, h); g = int(np.asarray(ImageOps.grayscale(im)).mean())
    c = Image.new("RGB", (s, s), (g, g, g)); c.paste(im, ((s - w) // 2, (s - h) // 2))
    return c.resize((sz, sz), Image.BICUBIC)

dino = AutoModel.from_pretrained(MOD).to(dev).eval()
@torch.no_grad()
def cls(ims):
    out = []
    for i in range(0, len(ims), 8):
        x = torch.stack([TO_T(im) for im in ims[i:i + 8]]).to(dev)
        out.append(F.normalize(dino(pixel_values=x).last_hidden_state[:, 0], dim=-1).cpu())
    return torch.cat(out)

def load(p): return Image.open(p).convert("RGB")
def gpath(img): return D / img if (D / img).exists() else D / "connues" / img.split("/")[-1]

# --- régions de la galerie
gal = list(csv.DictReader(open(D / "galerie.csv"))); idx = {g["image"]: i for i, g in enumerate(gal)}
pers = {}
for r in csv.DictReader(open(D / "oracle_temoins.csv")):
    if r["x0"]: pers.setdefault(r["image"], []).append(tuple(float(r[k]) for k in ("x0", "y0", "x1", "y1")))
REG = D / "regions_dinov3l_384.csv"
if not REG.exists():
    rows = []
    for i, g in enumerate(gal):
        W, H = Image.open(gpath(g["image"])).size
        for n in (2, 3):
            for a in range(n):
                for b in range(n): rows.append((i, f"grille{n}", round(b * W / n), round(a * H / n), round((b + 1) * W / n), round((a + 1) * H / n)))
        for x0, y0, x1, y1 in pers.get(g["image"], []):
            mx, my = 0.1 * (x1 - x0), 0.1 * (y1 - y0)
            x0, y0, x1, y1 = max(0, x0 - mx), max(0, y0 - my), min(W, x1 + mx), min(H, y1 + my)
            if min(x1 - x0, y1 - y0) >= 32: rows.append((i, "personne", round(x0), round(y0), round(x1), round(y1)))
    with open(REG, "w", newline="") as f: w = csv.writer(f); w.writerow(["image", "type", "x0", "y0", "x1", "y1"]); w.writerows(rows)
regs = [(int(r["image"]), r["type"], *(int(r[k]) for k in ("x0", "y0", "x1", "y1"))) for r in csv.DictReader(open(REG))]
RECLASSE = os.environ.get("RECLASSE", "entiere")  # "region" : SegSwap sur la région gagnante (PREINSCRIPTION_RECLASSEMENT_REGION.md)
ESSAI = int(os.environ.get("ESSAI", 0))  # essai à blanc : seulement les ESSAI premières régions, caches à part, 2 requêtes
if ESSAI: regs = regs[:ESSAI]; PAQUET = 40
print(len(regs), "régions", flush=True)
vecs = []
for k in range(0, len(regs), PAQUET):
    p = D / f"cache_regions_dinov3l_384_{k // PAQUET:03d}{'_essai' if ESSAI else ''}.pt"
    if not p.exists():
        part, cur, ims = regs[k:k + PAQUET], None, []
        for i, _, x0, y0, x1, y1 in part:
            if i != cur: cur, im = i, load(gpath(gal[i]["image"]))
            ims.append(carre(im.crop((x0, y0, x1, y1)), SZ_REG))
        torch.save(cls(ims), p); print("régions", k + len(part), "/", len(regs), flush=True)
    vecs.append(torch.load(p))
R = torch.cat(vecs); rimg = np.array([r[0] for r in regs]); rtyp = np.array([r[1] for r in regs])
G = torch.load(D / "cache_aikon_dinov3-vitl16-pretrain-lvd1689m_512.pt")  # base : image entière écrasée à 512 px

def par_image(s, masque):
    """Meilleur score de région par image (et indice de la région), -inf sans région."""
    best = np.full(len(gal), -np.inf); arg = np.full(len(gal), -1)
    for j in np.where(masque)[0]:
        if s[j] > best[rimg[j]]: best[rimg[j]] = s[j]; arg[rimg[j]] = j
    return best, arg

# --- SegSwap (identique à aikon.py)
T_SEG = T.Compose([T.Resize((MAX_SIZE, MAX_SIZE), antialias=True), T.ToTensor(), NORM])
param = torch.load(S / "hard_mining_neg5.pth", map_location="cpu", weights_only=True)
r50 = tvm.resnet50(weights=None)
backbone = torch.nn.Sequential(r50.conv1, r50.bn1, r50.relu, r50.maxpool, r50.layer1, r50.layer2, r50.layer3)
backbone.load_state_dict(param["backbone"]); backbone = backbone.to(dev).eval()
enc = transformer.TransEncoder(feat_dim=1024, pos_weight=0.1, feat_weight=1, dropout=0.1, activation="relu", mode="small",
                               layer_type=["I", "C", "I", "C", "I", "N"], drop_feat=0.1)
enc.load_state_dict(param["encoder"]); enc = enc.to(dev).eval()
NF = MAX_SIZE // STRIDE; yg, xg = np.where(np.ones((NF, NF), dtype=bool))
@torch.no_grad()
def segswap(q, cands):
    t1 = T_SEG(q)[None].repeat(len(cands), 1, 1, 1).to(dev); t2 = torch.stack([T_SEG(c) for c in cands]).to(dev)
    f1 = F.normalize(backbone(t1)); f2 = F.normalize(backbone(t2))
    o1, o2 = enc(f1, f2); o1, o2 = o1.cpu(), o2.cpu(); f1, f2 = f1.cpu(), f2.cpu()
    m1, m2 = o1[:, 2:].numpy(), o2[:, 2:].numpy()
    flow12 = (o1.narrow(1, 0, 2).permute(0, 2, 3, 1) - 0.5) * 2
    m1f = m1 * F.grid_sample(torch.from_numpy(m2.astype(np.float32)), flow12, mode="bilinear", align_corners=False).numpy()
    x2 = np.round(o1[:, 0, yg, xg].numpy() * (NF - 1)).astype(int); y2 = np.round(o1[:, 1, yg, xg].numpy() * (NF - 1)).astype(int)
    w = m1f[:, 0, yg, xg]; scores = []
    for j in range(len(cands)):
        a = f1[j][:, yg, xg].T; b = f2[j][:, y2[j], x2[j]].T; s = (a * b).sum(1).numpy() * w[j]; best = {}
        for i in range(len(s)): best[(y2[j, i], x2[j, i])] = max(best.get((y2[j, i], x2[j, i]), 0), s[i])
        scores.append(sum(best.values()))
    return np.array(scores)

# --- requêtes
lots = {r["requete"]: r["lot"] for r in csv.DictReader(open(HERE / "lots.csv"))}
comp = np.array([g["composition"] for g in gal]); rows = []
def rang(score, vrai): o = np.argsort(-score); return next(k for k, i in enumerate(o) if vrai[i]) + 1
for q in csv.DictReader(open(D / "requetes_boites.csv")):
    if lots.get(q["requete"]) != LOT or (ESSAI and len(rows) >= 2): continue
    im = load(D.parent / "corpus-images" / "rovigo" / q["photo"]).crop(tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1")))
    sens = [im, ImageOps.mirror(im)]
    cb = (G @ cls([T.Resize((SZ_BASE, SZ_BASE), antialias=True)(s) for s in sens]).T).numpy()      # base (n_galerie, 2)
    cr = (R @ cls([carre(s, SZ_REG) for s in sens]).T).numpy()                                 # régions (n_regions, 2)
    sr = cr.max(1); tr = cr.argmax(1)
    reg_all, arg_all = par_image(sr, np.ones(len(regs), bool))
    reg_gr, _ = par_image(sr, np.char.startswith(rtyp.astype(str), "grille")); reg_pe, _ = par_image(sr, rtyp == "personne")
    base = cb.max(1); score = np.maximum(base, reg_all)
    best_t = np.where(reg_all > base, tr[np.maximum(arg_all, 0)], cb.argmax(1))
    target = f"{q['bartsch_vol']}/{q['bartsch_n']}"; vrai = comp == target
    order = np.argsort(-score); top = list(order[:COS_TOPK]); top_abs = [i for i in order if not vrai[i]][:COS_TOPK]
    def cand(i):
        im_i = load(gpath(gal[i]["image"]))
        if RECLASSE == "region" and reg_all[i] > base[i]: return carre(im_i.crop(regs[arg_all[i]][2:]), MAX_SIZE)
        return im_i
    sc = {}
    for t in (0, 1):
        ids = [i for i in sorted(set(top) | set(top_abs)) if best_t[i] == t]
        if ids: sc.update(zip(ids, segswap(sens[t], [cand(i) for i in ids])))
    rer = sorted(top, key=lambda i: -sc[i]) + list(order[COS_TOPK:])
    rk = next(k for k, i in enumerate(rer) if vrai[i]) + 1
    jv = max(np.where(vrai[rimg])[0], key=lambda j: sr[j], default=None)
    sv = max([sc[i] for i in top if vrai[i]], default="")
    rows.append({"requete": q["requete"], "bartsch": target, "type": q["type"], "trouve": q["trouve"],
                 "rang_cosinus": rang(score, vrai), "rang_aikon": rk, "rang_grille_seule": rang(np.maximum(base, reg_gr), vrai),
                 "rang_personnes_seules": rang(np.maximum(base, reg_pe), vrai), "rang_regions_sans_base": rang(reg_all, vrai),
                 "region_vraie": f"{rtyp[jv]}:{','.join(str(v) for v in regs[jv][2:])}" if jv is not None else "",
                 "sens": "miroir" if best_t[rer[rk - 1]] == 1 else "endroit",
                 "score_vraie": round(float(sv), 2) if sv != "" else "", "score_premier": round(float(sc[rer[0]]), 2),
                 "score_absente": round(float(max(sc[i] for i in top_abs)), 2)})
    print(rows[-1], flush=True)
with open(D / f"resultats_regions_{LOT}{'_reclasse_region' if RECLASSE == 'region' else ''}{'_essai' if ESSAI else ''}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
r = [x["rang_aikon"] for x in rows]
for k in (1, 10, 50): print(f"rappel@{k} : {sum(x <= k for x in r)}/{len(rows)}")
print("rang médian :", sorted(r)[len(r) // 2])
