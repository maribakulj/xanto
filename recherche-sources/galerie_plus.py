#!/usr/bin/env python3
"""Agrandit la galerie d'estampes (domaine public) au-delà du Met : Rijksmuseum (API Linked Art), Art Institute of Chicago,
Cleveland Museum of Art, National Gallery of Art (données ouvertes, fichiers CSV dans <dossier>/plus/nga/).
Graveurs : ceux que le catalogue de Rovigo cite le plus (Marcantonio, Agostino Veneziano, Marco Dente, Caraglio) et leur entourage.
Sortie : <dossier>/plus/galerie_plus_<sources>.csv (image,composition,musee,titre,artiste,date) + images réduites à 1200 px dans <dossier>/plus/img/.
Reprend là où il s'est arrêté. Usage : galerie_plus.py <dossier_prive_recherche_sources> [rijks|aic|cma|nga ...]"""
import csv, io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image
D = Path(sys.argv[1]).resolve(); P = D / "plus"; (P / "img").mkdir(parents=True, exist_ok=True)
SOURCES = sys.argv[2:] or ["rijks", "aic", "cma", "nga"]
UA = {"User-Agent": "Mozilla/5.0 (xanto research)", "AIC-User-Agent": "xanto-research", "Accept": "application/ld+json"}
RIJKS = ["Marcantonio Raimondi", "Agostino Veneziano", "Marco Dente", "Jacopo Caraglio", "Giulio Bonasone", "Master of the Die",
         "Giovanni Battista Palumba", "Enea Vico", "Nicolas Beatrizet", "Ugo da Carpi"]
AIC = ["Marcantonio Raimondi", "Agostino Veneziano", "Marco Dente", "Giovanni Jacopo Caraglio", "Master of the Die", "Giulio Bonasone"]
NGA = ["Raimondi", "Agostino Veneziano", "Musi", "Marco Dente", "Caraglio", "Master of the Die", "Bonasone", "Palumba", "Master I.B.", "Vico", "Beatrizet", "Ugo da Carpi"]

def get(url, data=None, tries=4, headers=UA):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers | ({"Content-Type": "application/json"} if data else {}))
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception:
            time.sleep(4 * (i + 1))
    return None

out = P / f"galerie_plus_{'_'.join(SOURCES)}.csv"; done = {r["composition"] for r in csv.DictReader(open(out))} if out.exists() else set()
fh = open(out, "a", newline=""); w = csv.writer(fh)
if not done: w.writerow(["image", "composition", "musee", "titre", "artiste", "date"])
def save(cid, url, musee, titre, artiste, date):
    if cid in done: return
    b = get(url, headers={"User-Agent": UA["User-Agent"], "AIC-User-Agent": UA["AIC-User-Agent"]})
    if not b: print("échec", cid, flush=True); return
    try: im = Image.open(io.BytesIO(b)).convert("RGB")
    except Exception: print("image illisible", cid, flush=True); return
    im.thumbnail((1200, 1200)); f = f"plus/img/{cid.replace(':', '_')}.jpg"; im.save(D / f, quality=90)
    w.writerow([f, cid, musee, titre, artiste, date]); fh.flush(); done.add(cid)

if "rijks" in SOURCES:
    for a in RIJKS:
        url = f"https://data.rijksmuseum.nl/search/collection?creator={urllib.parse.quote(a)}&type=print"; n = 0
        while url:
            page = json.loads(get(url) or b"{}")
            for it in page.get("orderedItems", []):
                oid = it["id"].rsplit("/", 1)[1]; cid = f"rijks:{oid}"
                if cid in done: continue
                o = json.loads(get(it["id"]) or b"{}"); time.sleep(0.3)
                ident = [x.get("content", "") for x in o.get("identified_by", [])]
                try:
                    vi = json.loads(get(o["shows"][0]["id"])); do = json.loads(get(vi["digitally_shown_by"][0]["id"]))
                    img = do["access_point"][0]["id"].replace("/full/max/", "/full/1200,/")
                except Exception: continue
                save(cid, img, "Rijksmuseum", (ident[1] if len(ident) > 1 else "")[:200], a, ident[0] if ident else "")  # « date » = numéro d'inventaire ici; n += 1
            url = (page.get("next") or {}).get("id")
        print("rijks", a, n, flush=True)

if "aic" in SOURCES:
    for a in AIC:
        q = {"query": {"bool": {"must": [{"match_phrase": {"artist_title": a}}, {"term": {"is_public_domain": True}}]}},
             "limit": 100, "fields": ["id", "title", "artist_title", "date_display", "image_id", "classification_title"]}
        d = json.loads(get("https://api.artic.edu/api/v1/artworks/search", json.dumps(q).encode()) or b"{}")
        for r in d.get("data", []):
            if r.get("image_id"): save(f"aic:{r['id']}", f"https://www.artic.edu/iiif/2/{r['image_id']}/full/843,/0/default.jpg", "Art Institute of Chicago", r["title"][:200], r["artist_title"], r["date_display"])
            time.sleep(1)
        print("aic", a, len(d.get("data", [])), flush=True)

if "cma" in SOURCES:
    for a in ["Marcantonio Raimondi", "Agostino Veneziano", "Marco Dente", "Caraglio", "Master of the Die", "Giulio Bonasone"]:
        d = json.loads(get(f"https://openaccess-api.clevelandart.org/api/artworks/?q={urllib.parse.quote(a)}&has_image=1&cc0=1&type=Print&limit=500") or b"{}")
        for r in d.get("data", []):
            cr = "; ".join(c.get("description", "") for c in r.get("creators", []))
            if a.split()[-1] not in cr: continue
            save(f"cma:{r['id']}", r["images"]["web"]["url"], "Cleveland Museum of Art", r["title"][:200], cr[:120], r.get("creation_date", ""))
        print("cma", a, len(d.get("data", [])), flush=True)

if "nga" in SOURCES:
    csv.field_size_limit(10**9); N = P / "nga"; objs = {}
    for r in csv.DictReader(open(N / "objects.csv", encoding="utf-8")):
        if r["classification"] == "Print" and any(x in r["attribution"] for x in NGA): objs[r["objectid"]] = r
    for r in csv.DictReader(open(N / "published_images.csv", encoding="utf-8")):
        o = objs.get(r["depictstmsobjectid"])
        if o and r["openaccess"] == "1" and r["viewtype"] == "primary":
            save(f"nga:{o['objectid']}", r["iiifurl"] + "/full/!1200,1200/0/default.jpg", "National Gallery of Art", o["title"][:200], o["attribution"][:120], o["displaydate"])
            time.sleep(0.5)
    print("nga", len(objs), flush=True)
