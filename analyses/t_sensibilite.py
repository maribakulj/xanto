#!/usr/bin/env python3
"""T-sensibilité : les tests chronologiques (dates, inversion, réemploi, estampes par pièce) refaits
sans les pièces d'attribution débattue.

- « sans_gubbio_1522_1527 » : sans les pièces datées avant 1528 (groupe de Gubbio de 1522-1527, que
  Mallet donne au jeune Xanto et que Wilson lui refuse) ni celles qui portent les initiales F.R.
- « sans_gubbio_ni_y_slash » : en plus, sans les pièces marquées y/Ø (marque discutée de même).

Chaque variante relance les scripts de test avec commun.FILTRE et écrit leurs sorties complètes dans
analyses/t-sensibilite/<variante>/<test>/. Le résumé compare les chiffres clés à ceux de l'analyse
complète. Sorties : analyses/t-sensibilite/resultats.json.
"""
import commun
import t_dates
import t_inversion
import t_reemploi
import t_sources_par_piece

OUT = commun.ICI / "t-sensibilite"
VARIANTES = {
    "complet": None,
    "sans_gubbio_1522_1527": lambda f: not f["attribution_debattue"],
    "sans_gubbio_ni_y_slash": lambda f: not f["attribution_debattue_large"],
}
MODULES = {"t_dates": t_dates, "t_inversion": t_inversion, "t_reemploi": t_reemploi,
           "t_sources_par_piece": t_sources_par_piece}


def cles(r):
    """Chiffres clés comparés entre variantes."""
    inv, ree, sp, dt = r["t_inversion"], r["t_reemploi"], r["t_sources_par_piece"], r["t_dates"]
    perm_t = ree["variante_toutes"]["controle_permutation"]
    perm_i = ree["variante_inscrites"]["controle_permutation"]
    return {
        "pieces": dt["n_pieces"],
        "pieces_par_periode": dt["par_periode"],
        "inversion_par_periode_toutes_dates": {p: [v["n_inversees"], v["n_references"], v["part"]]
                                               for p, v in inv["par_periode"].items()},
        "inversion_par_periode_dates_inscrites": {p: [v["n_inversees"], v["n_references"], v["part"]]
                                                  for p, v in inv["par_periode_dates_inscrites"].items()},
        "inversion_p_<=1530_vs_1536-1542_toutes": inv["test_tendance_<=1530_vs_1536-1542"]["p_permutation_bilateral"],
        "inversion_p_<=1530_vs_1536-1542_inscrites":
            inv["test_tendance_dates_inscrites_<=1530_vs_1536-1542"]["p_permutation_bilateral"],
        "reemploi_estampes_nouvelles_par_periode": {p: v.get("estampes_nouvelles")
                                                    for p, v in ree["variante_toutes"]["par_periode"].items()},
        "reemploi_part_refs_tardives_nouvelles_toutes": [perm_t["part_refs_tardives_vers_estampes_nouvelles"]["observe"],
                                                         perm_t["part_refs_tardives_vers_estampes_nouvelles"]["p_superieur_ou_egal"]],
        "reemploi_part_refs_tardives_nouvelles_inscrites": [perm_i["part_refs_tardives_vers_estampes_nouvelles"]["observe"],
                                                            perm_i["part_refs_tardives_vers_estampes_nouvelles"]["p_superieur_ou_egal"]],
        "reemploi_combinaisons_deja_vues_toutes": [perm_t["part_pieces_tardives_a_combinaison_deja_vue"]["observe"],
                                                   perm_t["part_pieces_tardives_a_combinaison_deja_vue"]["p_superieur_ou_egal"]],
        "reemploi_combinaisons_deja_vues_inscrites": [perm_i["part_pieces_tardives_a_combinaison_deja_vue"]["observe"],
                                                      perm_i["part_pieces_tardives_a_combinaison_deja_vue"]["p_superieur_ou_egal"]],
        "sources_par_periode_moyenne_si_source": {p: v["moyenne_si_source"] for p, v in sp["par_periode_avec_modi"].items()},
        "sources_par_periode_part_avec_source": {p: v["part_avec_source"] for p, v in sp["par_periode_avec_modi"].items()},
        "sources_p_1531-1535_vs_1536-1542": sp["test_1531-1535_vs_1536-1542_moyenne_si_source"]["p_permutation_bilateral"],
    }


def main():
    sorties = {m: mod.OUT for m, mod in MODULES.items()}
    res = {"note": __doc__.strip().splitlines()[0], "exclues": {}, "variantes": {}}
    fiches, _, _ = commun.charger()
    res["exclues"] = {
        "sans_gubbio_1522_1527": sorted(f["id"] for f in fiches if f["attribution_debattue"]),
        "sans_gubbio_ni_y_slash": sorted(f["id"] for f in fiches if f["attribution_debattue_large"]),
    }
    try:
        for nom, filtre in VARIANTES.items():
            commun.FILTRE = filtre
            r = {}
            for m, mod in MODULES.items():
                mod.OUT = OUT / nom / m.replace("_", "-")
                r[m] = mod.main()
            res["variantes"][nom] = cles(r)
    finally:
        commun.FILTRE = None
        for m, mod in MODULES.items():
            mod.OUT = sorties[m]
    commun.ecrire_json(OUT / "resultats.json", res)
    for nom, v in res["variantes"].items():
        print("T-sensibilité", nom, {k: v[k] for k in ("pieces", "inversion_par_periode_dates_inscrites",
                                                       "inversion_p_<=1530_vs_1536-1542_inscrites",
                                                       "reemploi_part_refs_tardives_nouvelles_toutes",
                                                       "reemploi_combinaisons_deja_vues_inscrites",
                                                       "sources_par_periode_moyenne_si_source",
                                                       "sources_p_1531-1535_vs_1536-1542")})
    return res


if __name__ == "__main__":
    main()
