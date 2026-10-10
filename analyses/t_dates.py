#!/usr/bin/env python3
"""T-dates : une année (ou un intervalle) par pièce, avec la source de la date.

Priorité : année inscrite au revers ou au droit (lue par regex, chiffres arabes ou romains) ;
sinon l'année donnée par la fiche (« 1532 », « 1531 ca. ») ; sinon le milieu d'un intervalle
(« 1527-1530 ca. »). Les pièces dont l'intervalle chevauche deux périodes n'ont pas de période.
Sorties dans analyses/t-dates/.
"""
from collections import Counter

import commun

OUT = commun.ICI / "t-dates"


def main():
    fiches, _, _ = commun.charger()
    lignes = [{k: f[k] for k in ("id", "titolo", "annee", "amin", "amax", "source_date", "precis",
                                 "periode", "note_date", "data_catalogue", "link")} for f in fiches]
    for r in lignes:  # quelques champs « data » de pieces.csv contiennent l'inscription (colonnes décalées)
        if len(r["data_catalogue"]) > 40:
            r["data_catalogue"] = "(champ décalé dans pieces.csv)"
    lignes.sort(key=lambda r: (r["annee"] or 9999, r["id"]))
    commun.ecrire_csv(OUT / "dates_par_piece.csv", lignes)

    annees = sorted({r["annee"] for r in lignes if r["annee"]})
    par_annee = []
    for a in annees:
        rs = [r for r in lignes if r["annee"] == a]
        par_annee.append({"annee": a, "toutes": len(rs),
                          "inscrites": sum(r["source_date"] == "inscription" for r in rs),
                          "catalogue_annee": sum(r["source_date"] in ("catalogue", "catalogue ca.") or
                                                 r["source_date"].startswith("catalogue (") for r in rs),
                          "milieu_intervalle": sum(r["source_date"] == "catalogue intervalle" for r in rs)})
    commun.ecrire_csv(OUT / "pieces_par_annee.csv", par_annee)
    res = {
        "n_pieces": len(lignes),
        "par_source": dict(Counter(r["source_date"] for r in lignes)),
        "par_periode": dict(Counter(str(r["periode"]) for r in lignes)),
        "par_annee": par_annee,
        "desaccords_inscription_catalogue": [r["id"] for r in lignes if "désaccord" in r["source_date"]],
        "dates_de_lustre_gubbio": [r["id"] for r in lignes if "Gubbio" in r["note_date"]],
        "sans_date": [r["id"] for r in lignes if r["annee"] is None],
        "a_cheval_sur_deux_periodes": [r["id"] for r in lignes if r["annee"] and r["periode"] is None],
    }
    commun.ecrire_json(OUT / "resultats.json", res)
    print("T-dates", res["par_source"], res["par_periode"])
    return res


if __name__ == "__main__":
    main()
