#!/usr/bin/env python3
"""Reconstitue les données de l'essai à partir des sources publiques (manifeste_images.csv) :
épreuves des musées (empreinte SHA-256 vérifiée), estampes du Met (API, réduites à 1200 px comme galerie_met.py),
photographies des plats (site du catalogue de Rovigo, empreinte vérifiée).
Usage : telecharger_donnees.py <dossier_sortie>"""
import csv, hashlib, io, json, shutil, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; OUT = Path(sys.argv[1])
UA = {"User-Agent": "Mozilla/5.0 (xanto research)"}

def get(url, tries=5):
    h = dict(UA, **({"AIC-User-Agent": "xanto-research"} if "artic.edu" in url else {}))  # l'Art Institute exige cet en-tête
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=90).read()
        except Exception: time.sleep(3 * (i + 1))
    return None

def one(r):
    dst = OUT / r["chemin"]; dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists(): return "déjà là"
    if r["source"] == "met":
        o = json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{r['url']}") or b"{}")
        b = get(o.get("primaryImageSmall") or o.get("primaryImage") or "") if o else None
        if not b: return "ÉCHEC"
        im = Image.open(io.BytesIO(b)).convert("RGB"); im.thumbnail((1200, 1200)); im.save(dst, quality=88); return "ok"
    b = get(r["url"])
    if not b: return "ÉCHEC"
    for _ in range(3):  # le serveur d'images du Met renvoie parfois une autre version : on réessaie
        if not r["sha256"] or hashlib.sha256(b).hexdigest() == r["sha256"]: break
        time.sleep(5); b = get(r["url"]) or b""
    if r["sha256"] and hashlib.sha256(b).hexdigest() != r["sha256"]: return "EMPREINTE DIFFÉRENTE"
    dst.write_bytes(b); return "ok"

rows = list(csv.DictReader(open(HERE / "manifeste_images.csv")))
with ThreadPoolExecutor(6) as ex: res = list(ex.map(one, rows))
for f in ("galerie.csv", "requetes_boites.csv"):
    (OUT / "recherche-sources").mkdir(parents=True, exist_ok=True); shutil.copy(HERE / f, OUT / "recherche-sources" / f)
from collections import Counter
print(Counter(res))
for r, s in zip(rows, res):
    if s not in ("ok", "déjà là"): print(s, r["chemin"], r["url"])
