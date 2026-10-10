#!/usr/bin/env python3
"""Construit la table pièce ↔ estampe à partir du catalogue « Xanto nel mondo »
(Fondazione Banca del Monte di Rovigo), récupéré par l'API WordPress du site.

Entrée : le JSON brut des fiches (non versionné ; textes sous droits du site).
Sorties (faits extraits, avec lien vers la fiche) :
  data/pieces.csv     une ligne par fiche : date, forme, diamètre, lieu, inscription
  data/emprunts.csv   une ligne par référence Bartsch citée dans une fiche, avec des indicateurs
                      (graveur cité, inversion) ; la phrase d'origine n'est écrite que dans la
                      version privée (second argument facultatif : chemin du CSV complet)
Extraction par expressions régulières : chaque ligne est À VÉRIFIER sur la fiche.
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[1] / "data"
ENGRAVERS = ["Marcantonio", "Marco Dente", "Agostino", "Caraglio", "Ugo da Carpi", "Pencz", "Beham",
             "Dürer", "Durer", "Bonasone", "Maestro del Dado", "Maestro IB", "Giovanni Antonio da Brescia",
             "Vico", "Robetta", "Giovanni Jacopo", "Parmigianino", "Mantegna", "Musi", "Veneziano"]
INVERSION = re.compile(r"invers|controparte|specular|rovesciat|capovolt|a specchio", re.I)


def text(h):
    h = re.sub(r"<figure.*?</figure>", "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", h)
    return re.sub(r"[ \t\xa0]+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()


def field(t, label):
    m = re.search(label + r"\s*:?\s*\n?(.*?)(?:\n\s*\n|$)", t, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main():
    rows, loans = [], []
    for e in json.load(open(SRC)):
        t = text(e["html"])
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        date = next((l for l in lines[3:8] if re.search(r"1[45]\d\d", l)), "")
        diam = re.search(r"Diametro\s*:?\s*([\d,\.]+)\s*cm", t, re.I)
        place_i = next((i for i, l in enumerate(lines) if l.lower().startswith("diametro") or l.lower().startswith("dimensioni") or l.lower().startswith("altezza")), None)
        place = lines[place_i + 1] if place_i is not None and place_i + 1 < len(lines) else ""
        images = re.findall(r'href="(https?://[^"]+\.(?:jpe?g|png))"', e["html"], re.I)
        title = html.unescape(e["title"])
        rows.append({"id": e["id"], "titolo": title, "data": date,
                     "forma": next((l for l in lines[3:9] if l.isupper() and not re.search(r"\d", l) and l != title.upper()), ""),
                     "diametro_cm": diam.group(1).replace(",", ".") if diam else "",
                     "luogo": place, "iscrizione": field(t, "Iscrizion[ei]")[:400],
                     "n_bartsch": 0, "inversione_citata": int(bool(INVERSION.search(t))),
                     "immagini": " ".join(dict.fromkeys(images)), "link": e["link"]})
        comment = t.split("Commento dell", 1)[-1]
        protected = re.sub(r"\b(pp?|nn?|fig|figg|cfr|ca|vol|tav|inv|cat|ibid|op|cit)\.", lambda m: m.group(1) + "§", comment, flags=re.I)
        for sent in (x.replace("§", ".") for x in re.split(r"(?<=[\.;])\s+(?=[A-ZÈÉ“\"(])", protected)):
            for m in re.finditer(r"Bartsch\s*(\d+)\s*(?:,\s*p\.\s*(\d+))?\s*(?:,\s*n\.\s*(\d+))?", sent):
                loans.append({"id": e["id"], "titolo": title, "data": date,
                              "bartsch_vol": m.group(1), "bartsch_p": m.group(2) or "", "bartsch_n": m.group(3) or "",
                              "graveur_cite": "; ".join(g for g in ENGRAVERS if g.lower() in sent.lower()),
                              "inversione": int(bool(INVERSION.search(sent))),
                              "phrase": re.sub(r"\s+", " ", sent)[:300], "link": e["link"]})
                rows[-1]["n_bartsch"] += 1
    OUT.mkdir(exist_ok=True)
    # Version complète (avec les phrases du site de Rovigo) : à garder en privé, hors du dépôt.
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(loans[0].keys())); w.writeheader(); w.writerows(loans)
    public = [{k: v for k, v in x.items() if k != "phrase"} for x in loans]
    for name, data in (("pieces.csv", rows), ("emprunts.csv", public)):
        with open(OUT / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader(); w.writerows(data)
    print(f"{len(rows)} fiches, {len(loans)} références Bartsch, "
          f"{sum(1 for r in rows if r['n_bartsch'])} fiches avec au moins une référence, "
          f"{sum(r['inversione_citata'] for r in rows)} fiches mentionnant une inversion")


if __name__ == "__main__":
    main()
