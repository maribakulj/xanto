#!/usr/bin/env python3
"""Test d'échelle n° 2 : Métabus (Bartsch XIV 420, Marco Dente) dans la série du Sauvetage de Camille.
Lit les CSV des annotateurs (images anonymisées A-E) et la correspondance (privée, recopiée ici sans images).
Hauteur = distance tête (casque compris) → orteils du pied le plus bas, en cm, l'échelle venant du diamètre
publié divisé par le diamètre horizontal mesuré en pixels par l'annotateur lui-même."""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
corr = {r["image"]: r for r in csv.DictReader(open(HERE / "camille_correspondance.csv"))}
res = {}
for f in sorted(HERE.glob("camille_annotateur*.csv")):
    for r in csv.DictReader(open(f)):
        c = corr[r["image"]]
        dpx = float(r["D_x"]) - float(r["G_x"])
        cm = float(c["diametre_cm"]) / dpx
        h = math.hypot(float(r["T_x"]) - float(r["P_x"]), float(r["T_y"]) - float(r["P_y"])) * cm
        res.setdefault(r["image"], {**c, "mesures": {}})["mesures"][f.stem] = {"hauteur_cm": round(h, 2), "diametre_px": dpx,
                                                                                "ratio_vertical": round((float(r["B_y"]) - float(r["H_y"])) / dpx, 3)}
for k, v in res.items():
    hs = [m["hauteur_cm"] for m in v["mesures"].values()]
    v["moyenne_cm"] = round(sum(hs) / len(hs), 2)
    print(f"{k} {v['lieu']:28} {v['annee']} diam {v['diametre_cm']:>5} cm  hauteurs {hs}  moyenne {v['moyenne_cm']}  "
          f"(rapport à la figure/diamètre {v['moyenne_cm']/float(v['diametre_cm']):.3f})")
json.dump(res, open(HERE / "camille_resultats.json", "w"), ensure_ascii=False, indent=1)

# --- Cas pour la démo (même format que cas.json) ---
IMG = {"A": "corpus-images/met-plats/met_460208.jpg", "B": "corpus-images/rovigo/845__238.-01.jpg",
       "C": "corpus-images/rovigo/859__242.-01.jpg", "D": "corpus-images/rovigo/620__156.-01.jpg", "E": "corpus-images/rovigo/883__253.-01.jpg",
       "F": "corpus-images/louvre/0000801027_OG.JPG"}
a1 = {r["image"]: r for r in csv.DictReader(open(HERE / "camille_annotateur1.csv"))}
a2 = {r["image"]: r for r in csv.DictReader(open(HERE / "camille_annotateur2.csv"))}
temoins = []
ref = res["B"]
for k in "AFBCDE":
    r, c = a1[k], corr[k]
    cm = float(c["diametre_cm"]) / (float(r["D_x"]) - float(r["G_x"]))
    xs = [float(r[p]) for p in ("T_x", "P_x", "P2_x")]; ys = [float(r[p]) for p in ("T_y", "P_y", "P2_y")]
    pad = 0.35 * (max(ys) - min(ys))
    crop = [int(min(xs) - pad), int(min(ys) - 0.1 * pad), int(max(xs) + pad), int(max(ys) + 0.2 * pad)]
    bonne = c["qualite_image"] in ("haute", "moyenne")
    note = f"image de qualité {c['qualite_image']}"
    if k == "D":
        note = "ancienne photo en noir et blanc : les deux annotateurs ont pris le sommet du bouclier pour celui du casque ; remplacée par la photo du Louvre (F)"
    if k == "E":
        note = "plat de 280 px seulement sur la photo : mesure non fiable"
    temoins.append({"type": "plat", "objet": f"Sauvetage de Camille, {c['annee']} ({c['lieu']})", "fiche_rovigo": c["fiche_rovigo"],
                    "image": IMG[k], "crop": [max(0, v) for v in crop], "reference_cm": float(c["diametre_cm"]), "cm_par_px": cm,
                    "reperes": {"tete": [float(r["T_x"]), float(r["T_y"])], "pied_tendu": [float(r["P_x"]), float(r["P_y"])]},
                    "hauteur_cm": res[k]["mesures"]["camille_annotateur1"]["hauteur_cm"],
                    "hauteur_cm_independant": res[k]["mesures"]["camille_annotateur2"]["hauteur_cm"],
                    "prediction_proportionnelle_cm": round(ref["moyenne_cm"] * float(c["diametre_cm"]) / float(ref["diametre_cm"]), 2),
                    "comparable": bonne, "note": note})
cas = {"id": "camille-metabus", "titre": "Métabus dans le Sauvetage de Camille (Marco Dente, Bataille entre Romains et Carthaginois, Bartsch XIV 420)",
       "resume": "Xanto peint le Sauvetage de Camille au moins dix fois entre 1532 et 1542, toujours avec le même Métabus tiré de la gravure de Marco Dente. Cinq plats ont une image utilisable ; deux annotateurs indépendants, qui ignoraient l'hypothèse et les diamètres, ont relevé la tête et le pied de Métabus et mesuré eux-mêmes les plats sur des images anonymisées.",
       "conclusion": "Sur quatre plats datés de 1533 à 1539, de 26 à 31 cm de diamètre, Métabus mesure 10,8 à 11,3 cm (moyenne des deux annotateurs) : sa taille ne suit pas le diamètre, alors qu'une figure adaptée au plat varierait de 19 %. C'est la signature d'un même patron réutilisé à taille fixe pendant au moins six ans. Une première mesure du plat du Louvre (12,2 cm) venait d'une erreur : sur une vieille photo en noir et blanc, le sommet d'un bouclier avait été pris pour celui du casque ; la photo du musée corrige l'erreur.",
       "limites": "Annotateurs : deux instances d'IA (écart entre elles de 0,2 à 4 %). La photo du plat de Toronto est trop petite pour être utilisée. Estampe source pas encore mesurée ; quatre autres plats de la série (Venise 1534, Padoue 1542, Sèvres 1541, collection privée 1532) n'ont pas d'image accessible.",
       "temoins": temoins}
json.dump(cas, open(HERE / "cas_camille.json", "w"), ensure_ascii=False, indent=1)
