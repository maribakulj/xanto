#!/usr/bin/env python3
"""Lance les sept tests et rassemble leurs résultats dans analyses/resultats.json
(format lisible par une démo de visualisation). Usage : python3 analyses/tout.py"""
import datetime

import commun
import t_dates
import t_entier
import t_inversion
import t_rebapteme
import t_reemploi
import t_revers
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
    commun.ecrire_json(commun.ICI / "resultats.json", res)
    print("écrit :", commun.ICI / "resultats.json")


if __name__ == "__main__":
    main()
