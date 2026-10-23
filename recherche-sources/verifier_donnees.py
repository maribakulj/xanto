#!/usr/bin/env python3
"""Vérifie les manifestes de données.

Sans dossier : contrôles de cohérence sur les CSV publics (aucune image requise).
Avec un dossier (argument ou $XANTO_PRIVE) : recalcule le SHA-256 des fichiers présents.
  - photos des plats et épreuves « connues » (empreinte stable) : l'empreinte doit être identique ;
  - estampes du Met et galerie agrandie (réduites à 1200 px par Pillow, empreinte non stable d'une version de
    Pillow à l'autre) : empreinte comparée à titre indicatif, dimensions comparées strictement si l'empreinte diffère.
Usage : python3 recherche-sources/verifier_donnees.py [dossier]      Bibliothèque standard (+ Pillow si dossier)."""
import csv
import hashlib
import os
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
echecs = []


def lire(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def verifie(nom, ok, detail=""):
    print(("ok     " if ok else "ÉCHEC  ") + nom + (f" : {detail}" if detail else ""))
    if not ok:
        echecs.append(nom)


est, plats = lire(ICI / "manifeste_estampes.csv"), lire(ICI / "manifeste_plats.csv")
verifie("estampes : 1536 Met + 68 connues + 1285 galerie agrandie", len(est) == 2889, str(len(est)))
verifie("plats : 295 photos", len(plats) == 295, str(len(plats)))
verifie("estampes : chemins distincts", len({r["chemin"] for r in est}) == len(est))
verifie("estampes : notice, licence, empreinte renseignées",
        all(r["url_notice"] and r["licence"] and len(r["sha256"]) == 64 for r in est))
verifie("plats : fiche, URL d'image, empreinte renseignées",
        all(r["url_fiche"] and r["url_image"] and len(r["sha256"]) == 64 for r in plats))
galerie = {"recherche-sources/" + r["image"] for r in lire(ICI / "galerie.csv")}
verifie("galerie.csv (1 604 images) entièrement couverte par le manifeste", galerie <= {r["chemin"] for r in est})
noms = {r["fichier"] for r in plats}
vus = {r["photo"] for r in lire(ICI / "requetes_boites.csv")}
verifie("photos de requetes_boites.csv présentes dans manifeste_plats.csv", vus <= noms)

racine = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("XANTO_PRIVE")
if racine:
    from PIL import Image
    racine = Path(racine).expanduser()
    n = ident = absent = 0
    stricts, dimensions = [], []
    tout = [(r["chemin"], r["sha256"], r["empreinte_stable"] == "oui", (r["largeur"], r["hauteur"])) for r in est]
    tout += [("corpus-images/rovigo/" + r["fichier"], r["sha256"], True, (r["largeur"], r["hauteur"])) for r in plats]
    for chemin, sha, stable, wh in tout:
        f = racine / chemin
        if not f.exists():
            absent += 1
            continue
        n += 1
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        if h == sha:
            ident += 1
        elif stable:
            stricts.append(chemin)
        else:
            with Image.open(f) as im:
                if (str(im.size[0]), str(im.size[1])) != wh:
                    dimensions.append(chemin)
    print(f"fichiers présents : {n}, absents : {absent}, empreinte identique : {ident}")
    verifie("empreintes stables (plats, épreuves connues) identiques", not stricts, ", ".join(stricts[:5]))
    verifie("images réduites : dimensions identiques quand l'empreinte diffère", not dimensions, ", ".join(dimensions[:5]))
else:
    print("(pas de dossier : contrôles de cohérence seulement)")
if echecs:
    sys.exit(1)
print("Données cohérentes.")
