#!/usr/bin/env python3
"""Vérifie que les chiffres publiés se retrouvent dans les CSV publics (aucune donnée privée, aucun modèle).

1. Évaluation finale (RESULTAT_EVALUATION.md) : resultats/evaluation_base_dinov3_large.csv et
   resultats/evaluation_candidate_regions.csv, 105 requêtes, galerie de 1 604 images.
2. Analyses sur les fiches (analyses/RESULTATS.md) : analyses/resultats.json recoupé avec data/*.csv.

Attention au nommage dans evaluation_candidate_regions.csv (voir DONNEES.md) : la colonne `rang_aikon` y est
le rang FINAL, après SegSwap sur la région ; `rang_cosinus` est le rang de la PRÉSÉLECTION (avant SegSwap).

Usage : python3 recherche-sources/verifier_resultats.py      (code de sortie 1 si un chiffre ne se retrouve pas)
Bibliothèque standard seulement."""
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from math import comb, sqrt
from pathlib import Path

ICI = Path(__file__).resolve().parent
DEPOT = ICI.parent
echecs = []


def verifie(nom, obtenu, attendu):
    ok = obtenu == attendu
    print(("ok     " if ok else "ÉCHEC  ") + f"{nom} : {obtenu}" + ("" if ok else f" (attendu {attendu})"))
    if not ok:
        echecs.append(nom)


def lire(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def resume(rangs):
    return (sum(r == 1 for r in rangs), sum(r <= 10 for r in rangs), sum(r <= 50 for r in rangs),
            statistics.median(rangs))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / 2 / n) / d
    h = z * sqrt(p * (1 - p) / n + z * z / 4 / n / n) / d
    return round(100 * (centre - h)), round(100 * (centre + h))


def signe_bilateral(montent, descendent):
    n = montent + descendent
    k = min(montent, descendent)
    return 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n


# --------------------------------------------------------------------------- 1. évaluation

def evaluation():
    print("== Évaluation finale (105 requêtes)")
    cand = lire(ICI / "resultats" / "evaluation_candidate_regions.csv")
    base = lire(ICI / "resultats" / "evaluation_base_dinov3_large.csv")
    verifie("nombre de requêtes (candidate)", len(cand), 105)
    verifie("nombre de requêtes (base)", len(base), 105)
    verifie("mêmes requêtes dans les deux fichiers", {r["requete"] for r in cand} == {r["requete"] for r in base}, True)
    verifie("requêtes distinctes", len({r["requete"] for r in cand}), 105)
    verifie("estampes distinctes", len({r["bartsch"] for r in cand}), 18)
    lot = {r["requete"] for r in lire(ICI / "lots.csv") if r["lot"] == "evaluation"}
    boites = {r["requete"] for r in lire(ICI / "requetes_boites.csv")}
    verifie("lot « evaluation » de lots.csv : 107 requêtes, dont 105 avec une boîte (requetes_boites.csv)", (len(lot), len(lot & boites)), (107, 105))
    verifie("les 105 requêtes évaluées sont exactement celles du lot avec boîte", {r["requete"] for r in cand}, lot & boites)
    galerie = lire(ICI / "galerie.csv")
    verifie("images de la galerie (galerie.csv)", len(galerie), 1604)

    # candidate : rang_aikon = rang final après SegSwap ; rang_cosinus = présélection
    c_final = [int(r["rang_aikon"]) for r in cand]
    c_pre = [int(r["rang_cosinus"]) for r in cand]
    b_final = [int(r["rang_aikon"]) for r in base]
    b_pre = [int(r["rang_cosinus"]) for r in base]
    verifie("candidate, rang final : rang 1 / top10 / top50 / médiane", resume(c_final), (22, 40, 61, 34))
    verifie("base, rang final : rang 1 / top10 / top50 / médiane", resume(b_final), (5, 14, 27, 195))
    verifie("candidate avant SegSwap (présélection) : rang 1 / top10 / top50", resume(c_pre)[:3], (17, 40, 61))
    verifie("base avant SegSwap : rang 1 / top10 / top50", resume(b_pre)[:3], (5, 15, 27))

    verifie("intervalles de Wilson (%), candidate rang 1 / top10 / top50",
            [wilson(k, 105) for k in (22, 40, 61)], [(14, 30), (29, 48), (49, 67)])
    verifie("intervalles de Wilson (%), base rang 1 / top10 / top50",
            [wilson(k, 105) for k in (5, 14, 27)], [(2, 11), (8, 21), (18, 35)])

    # la vraie estampe monte ou descend (rang final candidate contre rang final base)
    par = {r["requete"]: int(r["rang_aikon"]) for r in base}
    monte = sum(int(r["rang_aikon"]) < par[r["requete"]] for r in cand)
    descend = sum(int(r["rang_aikon"]) > par[r["requete"]] for r in cand)
    verifie("la vraie estampe monte / descend", (monte, descend), (85, 15))
    verifie("test du signe bilatéral, p arrondi à 1 chiffre (5e-13)", f"{signe_bilateral(monte, descend):.0e}", "5e-13")

    # par estampe (une voix par estampe)
    bilan = defaultdict(lambda: [0, 0])
    for r in cand:
        a, b = int(r["rang_aikon"]), par[r["requete"]]
        bilan[r["bartsch"]][0] += a < b
        bilan[r["bartsch"]][1] += a > b
    verifie("par estampe : montent / descendent",
            (sum(m > d for m, d in bilan.values()), sum(m < d for m, d in bilan.values())), (13, 5))

    pertes = [r["requete"] for r in cand if int(r["rang_aikon"]) - par[r["requete"]] > 50]
    verifie("grandes pertes (plus de 50 rangs)", len(pertes), 9)
    ex = {r["requete"]: (par[r["requete"]], int(r["rang_aikon"])) for r in cand}
    verifie("exemples de pertes Q107 / Q152 / Q17 / Q129",
            [ex[q] for q in ("Q107", "Q152", "Q17", "Q129")], [(2, 119), (73, 260), (46, 157), (80, 299)])


# --------------------------------------------------------------------------- 2. analyses

def analyses():
    print("== Analyses sur les fiches (analyses/resultats.json recoupé avec data/*.csv)")
    chemin = DEPOT / "analyses" / "resultats.json"
    res = json.loads(chemin.read_text(encoding="utf-8"))
    emprunts = lire(DEPOT / "data" / "emprunts.csv")
    pieces = lire(DEPOT / "data" / "pieces.csv")

    def estampe(r):  # même forme que le JSON : B26.247 (zéros de tête retirés)
        n = int(r["bartsch_n"])
        if (r["bartsch_vol"], n) == ("26", 11726):  # fiche 112 : « 117 » collé à un renvoi « 26 » ; analyses/commun.py lit 117
            n = 117
        return f"B{int(r['bartsch_vol'])}.{n}"

    verifie("fiches (pieces.csv) et analyses (t_dates.n_pieces)", (len(pieces), res["t_dates"]["n_pieces"]), (374, 374))
    verifie("références Bartsch (emprunts.csv) et t_inversion.global.n_references",
            (len(emprunts), res["t_inversion"]["global"]["n_references"]), (576, 576))
    fiches = {r["id"] for r in emprunts}
    verifie("fiches avec au moins une référence", (len(fiches), res["t_inversion"]["fiches_avec_reference"]), (278, 278))
    verifie("références inversées (t_inversion.global.n_inversees)", res["t_inversion"]["global"]["n_inversees"], 63)
    verifie("périodes (<=1530 / 1531-1535 / 1536-1542 / sans)",
            tuple(res["t_dates"]["par_periode"][k] for k in ("<=1530", "1531-1535", "1536-1542", "None")),
            (101, 164, 101, 8))
    verifie("somme des périodes = nombre de fiches", sum(res["t_dates"]["par_periode"].values()), 374)

    ent = res["t_entier"]["global"]
    verifie("classement entier/groupe/figure/partie/non classé = 576",
            sum(ent[k] for k in ("composition entière", "groupe", "figure isolée", "partie de figure", "non classé")), 576)

    # estampes par pièce, recalculé depuis emprunts.csv (une estampe citée deux fois dans une fiche compte une fois)
    par_piece = defaultdict(set)
    for r in emprunts:
        par_piece[r["id"]].add(estampe(r))
    distribution = Counter(len(par_piece.get(r["id"], ())) for r in pieces)
    attendu = {int(k): v for k, v in res["t_sources_par_piece"]["global_bartsch"]["distribution"].items()}
    verifie("estampes par pièce : distribution recalculée depuis emprunts.csv", dict(sorted(distribution.items())), attendu)
    verifie("pièces avec au moins une estampe", sum(v for k, v in distribution.items() if k), 278)

    # nombre de pièces par estampe, recalculé
    n_pieces = Counter(e for s in par_piece.values() for e in s)
    json_estampes = {x["estampe"]: x["n_pieces"] for x in res["t_reemploi"]["par_estampe"]}
    ecarts = {e: (n_pieces.get(e), n) for e, n in json_estampes.items() if n_pieces.get(e) != n}
    verifie("estampes du JSON dont le nombre de pièces diffère de emprunts.csv", ecarts, {})
    verifie("estampes de emprunts.csv absentes du JSON", sorted(set(n_pieces) - set(json_estampes)), [])
    verifie("estampes les plus citées (Parnaso, Contesa, San Lorenzo)",
            [json_estampes[k] for k in ("B26.247", "B28.53", "B26.104")], [76, 71, 52])


if __name__ == "__main__":
    evaluation()
    analyses()
    print()
    if echecs:
        print(f"{len(echecs)} vérification(s) en échec.")
        sys.exit(1)
    print("Toutes les vérifications passent.")
