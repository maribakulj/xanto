#!/usr/bin/env python3
"""Prépare le paquet PRIVÉ d'annotation (page + vignettes + données) dans un dossier de sortie.

Usage :
  ~/caypollard/.venv/bin/python annotation/preparer.py <dossier_donnees> <dossier_sortie>

<dossier_donnees> : dossier privé qui contient corpus-images/rovigo/, recherche-sources/ (images des estampes,
inconnues_requetes.csv, candidats_inconnues_requetes_plus.csv, plus/galerie_plus.csv, galerie_met.csv) et
sources-libres/emprunts_complet_avec_phrases.csv (liens des fiches Rovigo).
Les tableaux publics (requetes_boites.csv, lots.csv, requetes*.csv, galerie.csv) sont lus dans recherche-sources/ du dépôt.

Le paquet produit contient des photos de plats : il reste PRIVÉ (Drive), il ne va jamais dans le dépôt."""
import csv, hashlib, json, shutil, sys
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ICI = Path(__file__).resolve().parent
PUB = ICI.parent / "recherche-sources"
if len(sys.argv) != 3:
    sys.exit(__doc__)
D = Path(sys.argv[1]).expanduser().resolve()
OUT = Path(sys.argv[2]).expanduser().resolve()
RS = D / "recherche-sources"
(OUT / "img").mkdir(parents=True, exist_ok=True)
COTE_BOITES, COTE_CANDIDATS = 1600, 1100   # côté max des vignettes (px)


def lire(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


_cache = {}
def vignette(chemin, cote, q):
    """Écrit une vignette JPEG, renvoie (chemin relatif, w orig, h orig, w vignette, h vignette)."""
    k = (str(chemin), cote)
    if k in _cache:
        return _cache[k]
    nom = "img/" + hashlib.sha1(str(chemin).encode()).hexdigest()[:12] + f"_{cote}.jpg"
    im = Image.open(chemin); ow, oh = im.size
    im = im.convert("RGB"); im.thumbnail((cote, cote), Image.LANCZOS)
    im.save(OUT / nom, "JPEG", quality=q, optimize=True)
    _cache[k] = (nom, ow, oh, im.width, im.height)
    return _cache[k]


def info(chemin, cote, q):
    n, ow, oh, tw, th = vignette(chemin, cote, q)
    return {"src": n, "ow": ow, "oh": oh, "tw": tw, "th": th}


def gpath(img):
    p = RS / img
    return p if p.exists() else RS / "connues" / img.split("/")[-1]


def lien_musee(comp="", fichier=""):
    """URL de la notice du musée, d'après la composition (met:123) ou le nom de fichier (26_10__rijks_RP-P-OB-12.100.jpg)."""
    src, _, i = comp.partition(":")
    if not i and "__" in fichier:
        s = fichier.split("__", 1)[1].rsplit(".", 1)[0]
        src, _, i = s.partition("_")
    return {"met": f"https://www.metmuseum.org/art/collection/search/{i}",
            "rijks": f"https://www.rijksmuseum.nl/en/collection/{i}",
            "aic": f"https://www.artic.edu/artworks/{i}",
            "cma": f"https://www.clevelandart.org/art/{i}",
            "nga": f"https://www.nga.gov/collection/art-object-page.{i}.html"}.get(src, "") if i else ""


# ---- métadonnées
fiches = {}
for r in lire(D / "sources-libres" / "emprunts_complet_avec_phrases.csv"):
    fiches.setdefault(r["id"], r["link"])
phrases = {}
for f in ("requetes.csv", "requetes2.csv"):
    for r in lire(PUB / f):
        phrases[r["requete"]] = r
lots = {r["requete"]: r["lot"] for r in lire(PUB / "lots.csv")}
galerie = {}
for r in lire(PUB / "galerie.csv"):
    galerie.setdefault(r["composition"], []).append(r)
meta = {f"met:{r['object_id']}": r for r in lire(RS / "galerie_met.csv")}
for r in lire(RS / "plus" / "galerie_plus.csv"):
    meta[r["composition"]] = r

# ---- 1. paires connues
paires = []
for q in lire(PUB / "requetes_boites.csv"):
    ph = phrases.get(q["requete"], {})
    comp = f"{q['bartsch_vol']}/{q['bartsch_n']}"
    eps = []
    for g in galerie.get(comp, []):
        p = gpath(g["image"])
        if not p.exists():
            continue
        e = info(p, COTE_BOITES, 82)
        e.update({"id": g["image"].split("/")[-1], "musee": g["musee"], "lien": lien_musee(g["composition"], g["image"].split("/")[-1])})
        eps.append(e)
    paires.append({
        "id": q["requete"], "lot": lots.get(q["requete"], ""), "plat": q["plat_id"], "titre": ph.get("titolo", ""),
        "date": ph.get("data", ""), "phrase": ph.get("phrase", ""), "fiche": fiches.get(q["plat_id"], ""),
        "bartsch": comp, "photo": info(D / "corpus-images" / "rovigo" / q["photo"], COTE_BOITES, 82), "photo_nom": q["photo"],
        "ia": [int(float(q[k])) for k in ("x0", "y0", "x1", "y1")], "ia_trouve": q["trouve"], "ia_type": q["type"],
        "epreuves": eps})

# ---- 2 et 3. sources inconnues
cands = {}
for c in lire(RS / "candidats_inconnues_requetes_plus.csv"):
    cands.setdefault(c["requete"], []).append(c)
sources = []
for q in lire(RS / "inconnues_requetes.csv"):
    lst = []
    for c in sorted(cands.get(q["requete"], []), key=lambda c: int(c["rang"])):
        m = meta.get(c["composition"], {})
        e = info(gpath(c["image"]), COTE_CANDIDATS, 75)
        e.update({"rang": int(c["rang"]), "id": c["composition"], "sens": c["sens"], "score": c["score_segswap"],
                  "region": [int(v) for v in c["region"].split(",")] if c["region"] else None,
                  "titre": (m.get("titre") or c["image"].split("/")[-1])[:200], "artiste": m.get("artiste", ""),
                  "date": m.get("date", ""), "musee": m.get("musee", ""), "lien": lien_musee(c["composition"])})
        lst.append(e)
    sources.append({"id": q["requete"], "groupe": q["groupe"], "plat": q["plat_id"], "type": q["type"],
                    "titre": phrases.get(q["requete"], {}).get("titolo", ""), "fiche": fiches.get(q["plat_id"], ""),
                    "photo": info(D / "corpus-images" / "rovigo" / q["photo"], COTE_BOITES, 82), "photo_nom": q["photo"],
                    "box": [int(float(q[k])) for k in ("x0", "y0", "x1", "y1")], "cands": lst})

(OUT / "data.js").write_text("const DATA=" + json.dumps({"version": 1, "paires": paires, "sources": sources}, ensure_ascii=False) + ";\n", encoding="utf-8")
for f in (ICI / "page").iterdir():
    shutil.copy(f, OUT / f.name)
mo = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
print(f"{len(paires)} paires, {len(sources)} figures sans source, {len(_cache)} vignettes, {mo:.0f} Mo -> {OUT}/index.html")
