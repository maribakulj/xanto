#!/usr/bin/env python3
"""Tests d'échelle : hauteur réelle (cm) d'une même figure sur l'estampe et sur les plats.
Lit mesures.csv (repères relevés à la main, pixels de l'image d'origine) ; écrit cas.json pour la démo.
Une ligne = un témoin d'un cas. Échelle de l'image = longueur connue (feuille ou diamètre du plat)
divisée par sa longueur en pixels, mesurée sur le bord extérieur."""
import csv
import json
import math
from collections import defaultdict

PTS = ["tete", "genou_tendu", "pied_tendu"]


def dist(r, a, b):
    if not r.get(a + "_x") or not r.get(b + "_x"):
        return None
    return math.hypot(float(r[a + "_x"]) - float(r[b + "_x"]), float(r[a + "_y"]) - float(r[b + "_y"]))


def main():
    cases = defaultdict(list)
    for r in csv.DictReader(open("mesures.csv")):
        cases[r["cas"]].append(r)
    out = {"cas": []}
    for cid, rows in cases.items():
        temoins = []
        print(f"\n== {cid}")
        for r in rows:
            scale = float(r["diametre_ou_largeur_cm"]) / (float(r["reference_px_droite"]) - float(r["reference_px_gauche"]))
            h = dist(r, "tete", "pied_tendu")
            t = {"type": r["temoin"], "objet": r["objet"], "fiche_rovigo": r.get("fiche_rovigo", ""),
                 "image": r["image_privee"], "crop": [int(v) for v in r["crop"].split(",")],
                 "reference_cm": float(r["diametre_ou_largeur_cm"]), "cm_par_px": scale,
                 "reperes": {p: [float(r[p + "_x"]), float(r[p + "_y"])] for p in PTS if r.get(p + "_x")},
                 "hauteur_cm": round(h * scale, 2) if h else None, "comparable": r.get("comparable", "oui") == "oui",
                 "note": r["note"]}
            temoins.append(t)
            print(f"  {r['objet'][:60]:60} {t['hauteur_cm']} cm")
        est = next((t for t in temoins if t["type"] == "estampe"), None)
        plats = [t for t in temoins if t["type"] == "plat" and t["comparable"]]
        if est and len(plats) >= 1:
            ref_plat = plats[0]
            for t in plats:
                # prédiction « adapté au plat » : la figure grandit avec le diamètre, calée sur le premier plat
                t["prediction_proportionnelle_cm"] = round(ref_plat["hauteur_cm"] * t["reference_cm"] / ref_plat["reference_cm"], 2)
                t["rapport_a_l_estampe"] = round(t["hauteur_cm"] / est["hauteur_cm"], 3)
        meta = json.load(open("cas_meta.json")).get(cid, {}) if __import__("os").path.exists("cas_meta.json") else {}
        out["cas"].append({"id": cid, **meta, "temoins": temoins})
    json.dump(out, open("cas.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
