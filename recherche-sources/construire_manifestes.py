#!/usr/bin/env python3
"""Construit les deux manifestes publics à partir du dossier privé (à relancer seulement si les images changent) :

  manifeste_estampes.csv : toutes les images d'estampes (Met, épreuves « connues », galerie agrandie) avec
                           identifiant du musée, URL de la notice, licence, empreinte SHA-256 et dimensions du fichier utilisé ;
  manifeste_plats.csv    : photographies des plats (Rovigo) : identifiant de fiche, nom de fichier, URL de la fiche,
                           URL de l'image, empreinte, dimensions. Les images elles-mêmes ne sont PAS publiées.

Usage : XANTO_PRIVE=/chemin/prive python3 recherche-sources/construire_manifestes.py
Entrées privées : $XANTO_PRIVE/recherche-sources/{met,connues,plus}/, $XANTO_PRIVE/corpus-images/rovigo/index.csv,
$XANTO_PRIVE/sources-libres/Rovigo_Xanto_catalogo_374_schede.json. Nécessite Pillow (dimensions)."""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

from PIL import Image

ICI = Path(__file__).resolve().parent
if not os.environ.get("XANTO_PRIVE"):
    sys.exit("Variable d'environnement XANTO_PRIVE absente (dossier privé). Voir REPRODUIRE.md.")
P = Path(os.environ["XANTO_PRIVE"]).expanduser()

LICENCE = {
    "Met": "CC0 (Met Open Access)",
    "Rijksmuseum": "Domaine public (image), métadonnées CC0",
    "Art Institute of Chicago": "CC0 (domaine public)",
    "Cleveland Museum of Art": "CC0 (Open Access)",
    "National Gallery of Art": "NGA Open Access (CC0)",
}
NOTICE = {
    "met": "https://www.metmuseum.org/art/collection/search/{}",
    "rijks": "https://id.rijksmuseum.nl/{}",
    "aic": "https://www.artic.edu/artworks/{}",
    "cma": "https://openaccess-api.clevelandart.org/api/artworks/{}",
    "nga": "https://www.nga.gov/collection/art-object-page.{}.html",
}


def empreinte(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dims(p):
    with Image.open(p) as im:
        return im.size


def lire(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def estampes():
    sources = {r["image_url"]: r for r in lire(ICI.parent / "data" / "estampes_sources.csv")}
    lignes = []
    for r in lire(ICI / "manifeste_images.csv"):
        if r["musee"] == "Rovigo":
            continue
        f = P / r["chemin"]
        if not f.exists():
            print("absent :", r["chemin"], file=sys.stderr)
            continue
        if r["source"] == "met":
            cid, partie, notice, img, musee = r["composition"], "met", NOTICE["met"].format(r["url"]), r["url_image"], "Met"
            sur = ""
        else:
            s = sources.get(r["url"], {})
            musee = "Met" if "Metropolitan" in r["musee"] else r["musee"]
            cid, partie, notice, img = r["composition"], "connues", s.get("object_url", ""), r["url"]
            sur = s.get("accession", "")
        w, h = dims(f)
        lignes.append({"chemin": r["chemin"], "partie": partie, "composition": cid, "musee": musee,
                       "identifiant_musee": (r["url"] if partie == "met" else sur),
                       "url_notice": notice, "url_image": img,
                       "licence": (sources.get(r["url"], {}).get("license") or LICENCE[musee]),
                       "titre": sources.get(r["url"], {}).get("title", ""), "artiste": sources.get(r["url"], {}).get("engraver", ""),
                       "date_ou_inventaire": "", "sha256": empreinte(f), "largeur": w, "hauteur": h,
                       "empreinte_stable": "non" if partie == "met" else "oui"})
    for r in lire(P / "recherche-sources" / "plus" / "galerie_plus.csv"):
        f = P / "recherche-sources" / r["image"]
        if not f.exists():
            print("absent :", r["image"], file=sys.stderr)
            continue
        pref, ident = r["composition"].split(":", 1)
        w, h = dims(f)
        lignes.append({"chemin": "recherche-sources/" + r["image"], "partie": "plus", "composition": r["composition"],
                       "musee": r["musee"], "identifiant_musee": ident, "url_notice": NOTICE[pref].format(ident),
                       "url_image": "", "licence": LICENCE[r["musee"]], "titre": r["titre"], "artiste": r["artiste"],
                       "date_ou_inventaire": r["date"], "sha256": empreinte(f), "largeur": w, "hauteur": h,
                       "empreinte_stable": "non"})
    return lignes


def plats():
    fiches = {str(x["id"]): x["link"] for x in json.load(open(P / "sources-libres" / "Rovigo_Xanto_catalogo_374_schede.json"))}
    lignes = []
    for r in lire(P / "corpus-images" / "rovigo" / "index.csv"):
        nom = Path(r["local_path"]).name
        f = P / "corpus-images" / "rovigo" / nom
        w, h = dims(f)
        sha = empreinte(f)
        assert sha == r["sha256"] and (w, h) == (int(r["width"]), int(r["height"])), nom
        lignes.append({"id_fiche": r["id"], "fichier": nom, "url_fiche": fiches.get(r["id"], ""), "url_image": r["url"],
                       "sha256": sha, "largeur": w, "hauteur": h})
    return sorted(lignes, key=lambda x: (int(x["id_fiche"]), x["fichier"]))


def ecrire(chemin, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    print(chemin.name, len(lignes), "lignes")


if __name__ == "__main__":
    ecrire(ICI / "manifeste_estampes.csv", estampes())
    ecrire(ICI / "manifeste_plats.csv", plats())
