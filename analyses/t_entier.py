#!/usr/bin/env python3
"""T-whole (E1, Briend 1992) : la fiche dit-elle que l'estampe est reprise en entier (composition)
ou qu'une figure (ou un groupe, ou une partie de figure) en est extraite ? Comparaison par graveur.

Briend : les estampes de Caraglio seraient copiées en entier, celles de Marcantonio découpées en
motifs, à cause de l'échelle des figures. Si c'est vrai, la part « composition entière » doit être
nettement plus forte pour Caraglio.

Lecture de la proposition qui contient la référence (à gauche de la référence). Ordre de décision :
composition entière > partie de figure > groupe > figure isolée > non classé (liste de sources).
Sorties dans analyses/t-entier/.
"""
import re
from collections import Counter

import commun
from t_rebapteme import VERBE

OUT = commun.ICI / "t-entier"
ENTIER = re.compile(
    r"intera composizione|l[’']intera scena|nel suo insieme|nella sua totalità|"
    r"(?<!della )(?<!nella )(?<!alla )(?<!dalla )\b(?:la|questa|tale)\s+(?:composizione|scena)\s+(?:creata da Xanto\s+)?"
    r"(?:è|e|sembra|appare)\s+(?:stata\s+)?(?:\w+\s+){0,2}?(?:ripres|tratt|desunt|derivat|citat|mutuat|basat|copiat)|"
    r"(?<!della )(?<!nella )\b(?:la|questa|tale)\s+(?:composizione|scena)\s+(?:è|e)\s+(?:una\s+)?citazione letterale|"
    r"(?:composizione|scena)\s+deriva\b|interamente\s+(?:ripres|tratt|desunt|derivat|citat|copiat|basat)|"
    r"soggetto\s+è\s+(?:tratt|ripres|citat|desunt)[oa]\s+(?:letteralmente|in modo letterale)|"
    r"utilizzato in modo letterale l[’']incisione", re.I)
PARTIE = re.compile(r"\b(?:le gambe|la parte (?:superiore|inferiore)|il resto del corpo|la testa|il busto|"
                    r"il braccio|le braccia|il torso|il panneggio|la posa)\b", re.I)
GROUPE = re.compile(r"\b(?:gruppo|coppia|le (?:due|tre|quattro|cinque) |i (?:due|tre|quattro) |le figure|"
                    r"i personaggi|le fanciulle|i soldati|i guerrieri|le ninfe|le muse|gli uomini|le donne|"
                    r"i putti|gli amorini|compagni)\b|\bsono\s+(?:stat[ie]\s+)?(?:ripres|tratt|desunt|citat|mutuat|"
                    r"pres|derivat)[ie]\b", re.I)
FIGURE = re.compile(r"\b(?:la figura|il personaggio|citazione di una figura|una figura|l[’']uomo|la donna|"
                    r"la fanciulla|il soldato|il guerriero)\b|\bè\s+(?:stat[oa]\s+)?(?:ripres|tratt|desunt|citat|"
                    r"mutuat|pres|derivat|copiat)[oa]\b|è citazione|deriva\b", re.I)


def classer(c):
    g = c["_gauche"]
    if ENTIER.search(g):
        return "composition entière"
    # sujet = ce qui précède le verbe d'emprunt (le titre de l'estampe, après le verbe, est ignoré)
    vs = list(VERBE.finditer(g))
    bons = [m for m in vs if re.match(r"[^;]{0,40}?\b(?:da|dal|dalla|dallo|dall’|dall'|dai|dagli|dalle)\b", g[m.end():])
            and not re.match(r"\s*a sua volta", g[m.end():])]
    if not vs:
        return "non classé"
    v = bons[0] if bons else vs[-1]
    sujet = g[max(0, v.start() - 120):v.end()]
    if PARTIE.search(sujet):
        return "partie de figure"
    if GROUPE.search(sujet):
        return "groupe"
    return "figure isolée"


CLASSES = ["composition entière", "groupe", "figure isolée", "partie de figure", "non classé"]


def tab(rs):
    c = Counter(r["classe"] for r in rs)
    n = len(rs)
    cl = n - c["non classé"]
    return {"n": n, **{k: c.get(k, 0) for k in CLASSES},
            "part_entiere_parmi_classees": round(c["composition entière"] / cl, 3) if cl else None,
            "part_groupe_ou_entiere_parmi_classees": round((c["composition entière"] + c["groupe"]) / cl, 3) if cl else None}


def main():
    fiches, cits, _ = commun.charger(avec_modi=True)
    F = commun.par_id(fiches)
    lignes = [{"id": c["id"], "estampe": c["estampe"], "titre_estampe": c["titre_estampe"],
               "graveur": c["graveur"], "classe": classer(c), "annee": F[c["id"]]["annee"],
               "periode": F[c["id"]]["periode"], "link": F[c["id"]]["link"]} for c in cits]
    commun.ecrire_csv(OUT / "entier_par_reference.csv", lignes)
    bart = [r for r in lignes if r["estampe"] != "MODI"]
    par_graveur = {g: tab([r for r in bart if r["graveur"] == g])
                   for g, _ in Counter(r["graveur"] for r in bart).most_common()}
    par_graveur["I Modi (Marcantonio, sans n° Bartsch)"] = tab([r for r in lignes if r["estampe"] == "MODI"])
    par_estampe = []
    for k, n in Counter(r["estampe"] for r in lignes).most_common(20):
        sub = [r for r in lignes if r["estampe"] == k]
        par_estampe.append({"estampe": k, "titre": sub[0]["titre_estampe"], "graveur": sub[0]["graveur"], **tab(sub),
                            "ids_entiere": [r["id"] for r in sub if r["classe"] == "composition entière"]})
    # pièces où une seule estampe est citée (copie d'une seule source), par graveur
    par_piece = {}
    for r in bart:
        par_piece.setdefault(r["id"], set()).add((r["estampe"], r["graveur"]))
    seule = Counter(next(iter(v))[1] for v in par_piece.values() if len(v) == 1)
    tot = Counter(g for v in par_piece.values() for _, g in v)
    res = {"global": tab(bart), "par_graveur": par_graveur, "par_estampe": par_estampe,
           "test_caraglio_vs_marcantonio": commun.permutation_par_piece(
               [dict(r, grp=r["graveur"]) for r in bart if r["classe"] != "non classé"], "grp",
               lambda r: r["classe"] == "composition entière", "Marcantonio", "Caraglio"),
           "test_groupe_ou_entier_caraglio_vs_marcantonio": commun.permutation_par_piece(
               [dict(r, grp=r["graveur"]) for r in bart if r["classe"] != "non classé"], "grp",
               lambda r: r["classe"] in ("composition entière", "groupe"), "Marcantonio", "Caraglio"),
           "caraglio_sans_contesa_B28.53": tab([r for r in bart if r["graveur"] == "Caraglio" and r["estampe"] != "B28.53"]),
           "pieces_a_source_unique_par_graveur": {g: {"pieces_source_unique": seule.get(g, 0),
                                                      "pieces_citant_le_graveur": tot[g]} for g in tot},
           "ids_composition_entiere": sorted({r["id"] for r in lignes if r["classe"] == "composition entière"})}
    commun.ecrire_json(OUT / "resultats.json", res)
    commun.ecrire_csv(OUT / "entier_par_graveur.csv", [{"graveur": g, **v} for g, v in par_graveur.items()])
    print("T-whole", res["global"])
    for g, v in par_graveur.items():
        print("  ", g, v)
    print("  ", res["test_caraglio_vs_marcantonio"], res["test_groupe_ou_entier_caraglio_vs_marcantonio"],
          res["caraglio_sans_contesa_B28.53"])
    return res


if __name__ == "__main__":
    main()
