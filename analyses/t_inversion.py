#!/usr/bin/env python3
"""T-inversion (B1) : part des références à une estampe que la fiche dit reprises « in controparte ».

Unité : une référence Bartsch dans une fiche (576). Le mot-clé est cherché dans la proposition
qui contient la référence : à gauche (entre la référence précédente, ou le début de la proposition,
et la référence) ; à droite seulement si aucune autre source n'est introduite après le mot-clé.
Négations cherchées (« non in controparte », « senza inversione », « non invertita ») : aucune trouvée.
Sorties dans analyses/t-inversion/.
"""
import re
from collections import Counter, defaultdict

import commun

OUT = commun.ICI / "t-inversion"
INV = re.compile(r"controparte|invertit[oaie]|inversione|in senso inverso|specular[ei]|specularmente|"
                 r"rovesciat[oaie] (?:rispetto|specular)|a specchio(?! basculante)", re.I)
NEG = re.compile(r"(?:non|senza|né)\W+(?:\w+\W+){0,3}(?:controparte|invert|invers|specular)", re.I)
APRES = re.compile(r"^\W*(?:,\s*)?\b(?:da|dal|dalla|dallo|dall’|dall'|dai|dagli|dalle)\b", re.I)
AUTRE_SOURCE = re.compile(r"\b(?:dal|dalla|dallo|dall’|dall'|dai|dagli|dalle|stampa|incisione|Modi)\b", re.I)


def classer(c):
    g, d = c["_gauche"], c["_droite"]
    if NEG.search(g) or NEG.search(d):
        return "negation"
    if INV.search(g):
        return "gauche"
    m = INV.search(d)
    if m and not AUTRE_SOURCE.search(d[:m.start()]) and not APRES.search(d[m.end():m.end() + 30]):
        return "droite"
    return ""


def taux(rs):
    n = len(rs)
    k = sum(1 for r in rs if r["inversion"] in ("gauche", "droite"))
    return {"n_references": n, "n_inversees": k, "part": round(k / n, 3) if n else None}


def main():
    fiches, cits, _ = commun.charger()
    F = commun.par_id(fiches)
    lignes = []
    for c in cits:
        f = F[c["id"]]
        lignes.append({"id": c["id"], "estampe": c["estampe"], "titre_estampe": c["titre_estampe"],
                       "graveur": c["graveur"], "inversion": classer(c), "annee": f["annee"],
                       "periode": f["periode"], "source_date": f["source_date"], "link": f["link"]})
    commun.ecrire_csv(OUT / "inversion_par_reference.csv", lignes)

    # mentions d'inversion dans les commentaires hors références Bartsch (ex. I Modi, sans numéro)
    hors = []
    for f in fiches:
        n_tot = len(INV.findall(f["_comm"]))
        n_ref = sum(1 for r in lignes if r["id"] == f["id"] and r["inversion"])
        if n_tot > n_ref:
            hors.append({"id": f["id"], "mentions_texte": n_tot, "rattachees_a_une_ref": n_ref, "link": f["link"]})
    commun.ecrire_csv(OUT / "mentions_non_rattachees.csv", hors)

    par_graveur = {g: taux([r for r in lignes if r["graveur"] == g])
                   for g, _ in Counter(r["graveur"] for r in lignes).most_common()}
    par_estampe = []
    for k, n in Counter(r["estampe"] for r in lignes).most_common():
        rs = [r for r in lignes if r["estampe"] == k]
        t = taux(rs)
        t.update({"estampe": k, "titre": rs[0]["titre_estampe"], "graveur": rs[0]["graveur"],
                  "ids_inversees": sorted(r["id"] for r in rs if r["inversion"])})
        par_estampe.append(t)
    par_periode = {p: taux([r for r in lignes if r["periode"] == p]) for p, _, _ in commun.PERIODES}
    par_periode["sans période"] = taux([r for r in lignes if r["periode"] is None])
    # même chose en ne gardant que les dates inscrites
    par_periode_inscrites = {p: taux([r for r in lignes if r["periode"] == p and r["source_date"] == "inscription"])
                             for p, _, _ in commun.PERIODES}
    # fiches : au moins une inversion signalée
    par_fiche = defaultdict(list)
    for r in lignes:
        par_fiche[r["id"]].append(r)
    fiches_inv = sum(1 for rs in par_fiche.values() if any(r["inversion"] for r in rs))
    res = {"global": taux(lignes),
           "repartition_position": dict(Counter(r["inversion"] or "aucune" for r in lignes)),
           "negations_trouvees": sum(r["inversion"] == "negation" for r in lignes),
           "fiches_avec_reference": len(par_fiche), "fiches_avec_au_moins_une_inversion": fiches_inv,
           "par_graveur": par_graveur, "par_periode": par_periode,
           "par_periode_dates_inscrites": par_periode_inscrites,
           "test_tendance_<=1530_vs_1536-1542": commun.permutation_par_piece(
               lignes, "periode", lambda r: r["inversion"] in ("gauche", "droite"), "<=1530", "1536-1542"),
           "test_1531-1535_vs_1536-1542": commun.permutation_par_piece(
               lignes, "periode", lambda r: r["inversion"] in ("gauche", "droite"), "1531-1535", "1536-1542"),
           "par_estampe": par_estampe,
           "fiches_mentions_non_rattachees": [h["id"] for h in hors]}
    commun.ecrire_json(OUT / "resultats.json", res)
    commun.ecrire_csv(OUT / "inversion_par_estampe.csv", par_estampe,
                      ["estampe", "titre", "graveur", "n_references", "n_inversees", "part", "ids_inversees"])
    print("T-inversion", res["global"], res["repartition_position"], res["test_tendance_<=1530_vs_1536-1542"],
          res["test_1531-1535_vs_1536-1542"], res["par_periode_dates_inscrites"])
    for p, v in par_periode.items():
        print("  ", p, v)
    for g, v in par_graveur.items():
        print("  ", g, v)
    return res


if __name__ == "__main__":
    main()
