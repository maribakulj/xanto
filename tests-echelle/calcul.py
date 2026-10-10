#!/usr/bin/env python3
"""Test d'échelle, pilote : la même figure (Apollon du Parnasse) a-t-elle la même taille absolue
sur des plats de diamètres différents, et la taille de l'estampe ?
Repères relevés à la main par un seul annotateur (Claude), informé des sources : pilote, pas preuve."""
import csv, math
rows = list(csv.DictReader(open("mesures_apollon_parnasse.csv")))
def d(r, a, b):
    return math.hypot(float(r[a + "_x"]) - float(r[b + "_x"]), float(r[a + "_y"]) - float(r[b + "_y"]))
print(f"{'témoin':58} {'cm/px':>8} {'tête-pied':>10} {'genou-pied':>10} {'tête-genou':>10}")
ref = None
for r in rows:
    scale = float(r["diametre_ou_largeur_cm"]) / (float(r["reference_px_droite"]) - float(r["reference_px_gauche"]))
    hf, kf, hk = (d(r, "tete", "pied_tendu") * scale, d(r, "genou_tendu", "pied_tendu") * scale, d(r, "tete", "genou_tendu") * scale)
    print(f"{r['objet'][:58]:58} {scale:8.5f} {hf:9.2f}  {kf:9.2f}  {hk:9.2f}")
