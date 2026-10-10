#!/usr/bin/env python3
"""Lance les sept tests (plus l'analyse de sensibilité) et rassemble leurs résultats dans analyses/resultats.json
(format lisible par une démo de visualisation). Usage : python3 analyses/tout.py"""
import datetime

import commun
import t_dates
import t_entier
import t_inversion
import t_rebapteme
import t_reemploi
import t_revers
import t_sensibilite
import t_sources_par_piece


def main():
    res = {
        "meta": {
            "source": "Catalogue « Xanto nel mondo », Fondazione Banca del Monte di Rovigo (374 fiches)",
            "statut": "Extraction automatique par expressions régulières (text-mining) : chaque chiffre est à "
                      "vérifier sur les fiches (liens fournis). Ce sont des affirmations du catalogue, pas des "
                      "observations sur les objets.",
            "genere_le": datetime.date.today().isoformat(),
            "periodes": [p[0] for p in commun.PERIODES],
        },
        "t_dates": t_dates.main(),
        "t_inversion": t_inversion.main(),
        "t_reemploi": t_reemploi.main(),
        "t_revers": t_revers.main(),
        "t_rebapteme": t_rebapteme.main(),
        "t_entier": t_entier.main(),
        "t_sources_par_piece": t_sources_par_piece.main(),
    }
    res["t_sensibilite"] = t_sensibilite.main()
    res["p_valeurs"] = p_valeurs(res)
    commun.ecrire_json(commun.ICI / "resultats.json", res)
    for x in res["p_valeurs"]["liste"]:
        print("  p", x["p"], "Holm(toutes)", x["p_holm_toutes"], x["test"], "|", x["comparaison"])
    print("écrit :", commun.ICI / "resultats.json")


def p_valeurs(res):
    """Toutes les p-valeurs rapportées dans RESULTATS.md (analyse complète), avec une correction de Holm
    sur l'ensemble, donnée à titre indicatif : les tests sont exploratoires et non indépendants."""
    inv, ree, sp, ent, rv = (res["t_inversion"], res["t_reemploi"], res["t_sources_par_piece"],
                             res["t_entier"], res["t_revers"])
    L = []

    def aj(test, comp, p, note=""):
        L.append({"test": test, "comparaison": comp, "p": p, "note": note})

    aj("T-inversion", "<=1530 vs 1536-1542, toutes dates", inv["test_tendance_<=1530_vs_1536-1542"]["p_permutation_bilateral"])
    aj("T-inversion", "1531-1535 vs 1536-1542, toutes dates", inv["test_1531-1535_vs_1536-1542"]["p_permutation_bilateral"])
    aj("T-inversion", "<=1530 vs 1536-1542, dates inscrites",
       inv["test_tendance_dates_inscrites_<=1530_vs_1536-1542"]["p_permutation_bilateral"], "résultat principal")
    aj("T-inversion", "1531-1535 vs 1536-1542, dates inscrites",
       inv["test_dates_inscrites_1531-1535_vs_1536-1542"]["p_permutation_bilateral"], "résultat principal")
    for v, lab in (("variante_toutes", "toutes dates"), ("variante_inscrites", "dates inscrites")):
        cp = ree[v]["controle_permutation"]
        aj("T-reuse", "estampes introduites dès 1536 (moins que le hasard ?), " + lab,
           cp["estampes_introduites_des_1536"]["p_inferieur_ou_egal"], "unilatéral")
        aj("T-reuse", "part des références tardives vers des estampes nouvelles, " + lab,
           cp["part_refs_tardives_vers_estampes_nouvelles"]["p_superieur_ou_egal"], "unilatéral")
        aj("T-reuse", "combinaisons déjà vues (pièces tardives), " + lab,
           cp["part_pieces_tardives_a_combinaison_deja_vue"]["p_superieur_ou_egal"], "unilatéral")
    aj("T-sources", "estampes par pièce, 1531-1535 vs 1536-1542",
       sp["test_1531-1535_vs_1536-1542_moyenne_si_source"]["p_permutation_bilateral"])
    for k, lab in (("test_caraglio_vs_marcantonio", "entière, par référence (grappes = pièces)"),
                   ("test_groupe_ou_entier_caraglio_vs_marcantonio", "entière ou groupe, par référence (grappes = pièces)"),
                   ("test_caraglio_vs_marcantonio_grappes_estampes", "entière, par référence (grappes = estampes)"),
                   ("test_groupe_ou_entier_grappes_estampes", "entière ou groupe, par référence (grappes = estampes)")):
        aj("T-whole (Briend)", lab, ent[k]["p_bootstrap_bilateral"], "bootstrap")
    for k, lab in (("test_caraglio_vs_marcantonio_par_estampe_3_refs_ou_plus", "entière, par estampe (>= 3 réf.)"),
                   ("test_groupe_ou_entier_par_estampe_3_refs_ou_plus", "entière ou groupe, par estampe (>= 3 réf.)")):
        aj("T-whole (Briend)", lab, ent[k]["p_permutation_bilateral"], "permutation entre estampes")
    for k, v in rv["modi_et_sujets_politiques"].items():
        aj("T-revers (Modi × politique)", "définition « %s »" % k, v["p_hypergeometrique_unilateral"],
           "Holm sur les 3 définitions : %s" % v["p_holm_3_definitions"])
    aj("T-revers (Modi × politique)", "définition combinée, stratifiée par période",
       rv["modi_et_sujets_politiques_stratifie_par_periode"]["p_permutation_dans_les_periodes_unilateral"], "unilatéral")
    corr = commun.holm({i: x["p"] for i, x in enumerate(L)})
    for i, x in enumerate(L):
        x["p_holm_toutes"] = corr[i]
    return {"note": "Tests exploratoires sur les mêmes 374 fiches. Aucune correction pour tests multiples "
                    "n'est appliquée dans les verdicts, sauf la correction de Holm sur les trois définitions de "
                    "« politique » (T-revers). La colonne p_holm_toutes corrige sur toute la liste, à titre indicatif.",
            "liste": L}


if __name__ == "__main__":
    main()
