#!/usr/bin/env python3
"""Constitue la galerie d'estampes (Met, domaine public) : graveurs de l'entourage de Marcantonio,
estampes datées 1500-1570. Sortie : <dossier>/galerie_met.csv + images réduites (1200 px) dans <dossier>/met/.
Usage : galerie_met.py <dossier>"""
import csv, io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (xanto research)"}
API = "https://collectionapi.metmuseum.org/public/collection/v1.1"
GRAVEURS = ["Marcantonio Raimondi", "Agostino Veneziano", "Marco Dente", "Gian Jacopo Caraglio", "Giulio Bonasone",
            "Master of the Die", "Enea Vico", "Giorgio Ghisi", "Nicolas Beatrizet", "Antonio Fantuzzi", "Ugo da Carpi",
            "Benedetto Montagna", "Giovanni Battista Franco", "Battista Angolo del Moro", "Giovanni Antonio da Brescia"]

def get(url, tries=4):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception:
            time.sleep(3 * (i + 1))
    return None

out = Path(sys.argv[1]); (out / "met").mkdir(parents=True, exist_ok=True)
ids = []
for g in GRAVEURS:
    off = 0
    while True:
        d = json.loads(get(f"{API}/search?q={urllib.parse.quote(g)}&hasImages=true&limit=100&offset={off}") or b"{}")
        page = d.get("objectIDs") or []
        ids += page; off += 100
        if len(page) < 100 or off >= 1500: break
        time.sleep(0.3)
ids = list(dict.fromkeys(ids)); print(len(ids), "identifiants", file=sys.stderr)
rows = []
fp = out / "galerie_met.csv"
done = {r["object_id"] for r in csv.DictReader(open(fp))} if fp.exists() else set()
w = csv.writer(open(fp, "a", newline=""))
if not done: w.writerow(["object_id", "titre", "artiste", "date", "debut", "fin", "medium", "fichier"])
for i, oid in enumerate(ids):
    if str(oid) in done: continue
    o = json.loads(get(f"{API.replace('v1.1','v1')}/objects/{oid}") or b"{}")
    time.sleep(0.15)
    if not o.get("isPublicDomain") or o.get("department") != "Drawings and Prints": continue
    if not (1490 <= (o.get("objectBeginDate") or 0) <= 1570): continue
    if not any(k in (o.get("medium") or "").lower() for k in ("engraving", "etching", "woodcut", "chiaroscuro")): continue
    url = o.get("primaryImageSmall") or o.get("primaryImage")
    b = get(url) if url else None
    if not b: continue
    try:
        im = Image.open(io.BytesIO(b)).convert("RGB"); im.thumbnail((1200, 1200)); im.save(out / "met" / f"{oid}.jpg", quality=88)
    except Exception:
        continue
    w.writerow([oid, o.get("title", ""), o.get("artistDisplayName", ""), o.get("objectDate", ""), o.get("objectBeginDate"), o.get("objectEndDate"), o.get("medium", ""), f"met/{oid}.jpg"])
    if i % 50 == 0: print(i, file=sys.stderr)
