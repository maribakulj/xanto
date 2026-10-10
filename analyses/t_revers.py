#!/usr/bin/env python3
"""T-revers (D1, Jestaz 1976) : mots de genre au revers (historia, fabula, nota, sporcitia…) et
sources littéraires nommées, croisés avec le type des estampes employées sur la pièce.

Hypothèse de Jestaz : ces mots renverraient à des recueils de modèles classés par genre
(sporcitia = pudenda). Si c'était le cas, on attend une association entre le mot et le type des
estampes : « sporcitia » ↔ I Modi, « historia » ↔ estampes historiques ou religieuses,
« fabula » ↔ estampes mythologiques.

Inscription = section « Iscrizioni » de la fiche (revers, parfois droit). I Modi = mention des
Modi dans le commentaire (sans numéro Bartsch). Type d'estampe : table ESTAMPES de commun.py
(classement à la main du sujet de l'estampe, à vérifier).
Sorties dans analyses/t-revers/.
"""
import re
from collections import Counter, defaultdict

import commun

OUT = commun.ICI / "t-revers"
GENRES = {
    "historia": r"\bh?istori(?:a|ae|e)\b|\bhist\b\.?",
    "fabula": r"\bfabul[ae]\b|\bfavol[ae]\b",
    "nota": r"\bnota\b",
    "sporcitia": r"\bsporci(?:tia|zia)\b",
    "imaginatione": r"\bim+agina(?:tione|zione)\b",
}
LITTERAIRES = {
    "Ovidio (Metamorfosi)": r"ovid|ouid|\bmeth?\b",
    "Virgilio (Eneide)": r"virgil|vergil|uirgil|vgilio|eneid|aeneid",
    "Ariosto": r"ariost|furios",
    "Petrarca": r"petrarc|triumph|triomph",
    "Giustino": r"iustin|giustin|justin",
    "Livio": r"\blivi[oy]",
    "Turpino": r"turpin",
    "Apuleio": r"apule",
    "Boccaccio": r"boccac",
}
# source littéraire nommée par le COMMENTAIRE de la fiche (pas par Xanto)
LITT_COMMENTAIRE = {
    "Ovidio": r"Ovidio|Metamorfosi(?! di Apuleio)",
    "Virgilio": r"Virgilio|Eneide",
    "Ariosto": r"Ariosto|Orlando Furioso",
    "Petrarca": r"Petrarca|Trionf[oi] d",
    "Giustino/Trogo": r"Giustino|Trogo",
    "Livio": r"\bLivio\b",
    "Bibbia": r"Bibbia|Genesi|Esodo|Vangel|Antico Testamento|Nuovo Testamento|Libro dei Re|Libro dei Giudici",
    "Apuleio": r"Apuleio",
    "Boccaccio": r"Boccaccio",
    "attualità/allegoria politica": r"Sacco di Roma|Carlo V|Clemente VII|allegori[ac] politic",
}
TYPES = ["érotique", "religieux", "mythologique", "bataille", "historique", "autre/allégorique"]


def type_norm(t):
    return t if t in TYPES else "autre/allégorique"


def main():
    fiches, cits, _ = commun.charger(avec_modi=True)
    types_piece = defaultdict(Counter)
    for c in cits:
        types_piece[c["id"]][type_norm(c["type_estampe"])] += 1
    lignes = []
    for f in fiches:
        # seulement le texte cité entre guillemets (évite « si nota » de la description du catalogue)
        cite = re.findall(r"[“\"]([^”\"]*)[”\"]?", f["_ins"])
        ins = " ".join(cite) if cite else f["_ins"]
        g = [k for k, rx in GENRES.items() if re.search(rx, ins, re.I)]
        lit = [k for k, rx in LITTERAIRES.items() if re.search(rx, ins, re.I)]
        tp = types_piece.get(f["id"], Counter())
        lignes.append({"id": f["id"], "annee": f["annee"], "periode": f["periode"],
                       "inscription_presente": bool(ins), "genres": " ".join(g) or "aucun",
                       "sources_litteraires": " ; ".join(lit),
                       "sources_commentaire": " ; ".join(k for k, rx in LITT_COMMENTAIRE.items()
                                                         if re.search(rx, f["_comm"])),
                       "marque_y_slash": bool(re.search(r"\by\s*/\s*[Øø0]|\by\b\s*[”\"]", ins)),
                       **{"n_" + t.split("/")[0]: tp.get(t, 0) for t in TYPES},
                       "a_une_source_identifiee": bool(tp), "link": f["link"]})
    commun.ecrire_csv(OUT / "revers_par_piece.csv", lignes)

    def groupe(r):
        g = r["genres"].split()
        return "plusieurs" if len(g) > 1 else g[0]

    groupes = ["historia", "fabula", "nota", "sporcitia", "plusieurs", "aucun"]
    # tableau de contingence : genre × présence d'au moins une estampe de chaque type
    conting = []
    for gname in groupes:
        rs = [r for r in lignes if groupe(r) == gname]
        avec = [r for r in rs if r["a_une_source_identifiee"]]
        ligne = {"genre": gname, "pieces": len(rs), "pieces_avec_source": len(avec),
                 "ids": [r["id"] for r in rs] if gname != "aucun" else "(voir CSV)"}
        for t in TYPES:
            k = "n_" + t.split("/")[0]
            ligne[t] = sum(1 for r in avec if r[k] > 0)
        conting.append(ligne)
    commun.ecrire_csv(OUT / "contingence_genre_x_type_estampe.csv",
                      [dict(c, ids=" ".join(map(str, c["ids"])) if isinstance(c["ids"], list) else c["ids"])
                       for c in conting])
    # genre × source littéraire
    lit_tab = []
    for gname in groupes:
        rs = [r for r in lignes if groupe(r) == gname]
        d = {"genre": gname, "pieces": len(rs)}
        for k in LITTERAIRES:
            d[k] = sum(1 for r in rs if k in r["sources_litteraires"])
        lit_tab.append(d)
    commun.ecrire_csv(OUT / "contingence_genre_x_source_litteraire.csv", lit_tab)
    com_tab = []
    for gname in groupes:
        rs = [r for r in lignes if groupe(r) == gname]
        d = {"genre": gname, "pieces": len(rs)}
        for k in LITT_COMMENTAIRE:
            d[k] = sum(1 for r in rs if k in r["sources_commentaire"])
        com_tab.append(d)
    commun.ecrire_csv(OUT / "contingence_genre_x_source_selon_commentaire.csv", com_tab)
    # genre × année
    par_annee = defaultdict(Counter)
    for r in lignes:
        par_annee[r["annee"]][groupe(r)] += 1
    genre_annee = [{"annee": a, **{g: par_annee[a].get(g, 0) for g in groupes}}
                   for a in sorted(par_annee, key=lambda x: x or 9999)]
    commun.ecrire_csv(OUT / "genre_par_annee.csv", genre_annee)
    # pièces aux Modi : quel mot au revers ?
    modi = [r for r in lignes if r["n_érotique"]]
    # Talvacchia : les Modi servent-ils plus souvent des sujets politiques ? (hypergéométrique unilatéral)
    from math import comb

    def hyper(N, K, n, k):
        return sum(comb(K, i) * comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / comb(N, n)

    politique = {}
    for lab, test in (("revers_nota", lambda r: "nota" in r["genres"]),
                      ("commentaire_actualite_politique", lambda r: "attualità" in r["sources_commentaire"]),
                      ("nota_ou_commentaire_politique", lambda r: "nota" in r["genres"] or "attualità" in r["sources_commentaire"])):
        n = sum(1 for r in lignes if test(r))
        k = sum(1 for r in modi if test(r))
        politique[lab] = {"pieces_total": len(lignes), "pieces_modi": len(modi), "pieces_categorie": n,
                          "modi_dans_categorie": k, "attendu_si_hasard": round(n * len(modi) / len(lignes), 2),
                          "p_hypergeometrique_unilateral": round(hyper(len(lignes), len(modi), n, k), 4),
                          "ids": [r["id"] for r in modi if test(r)]}
    # Trois définitions de « politique » ont été essayées (la combinée avait été retenue seule) :
    # correction de Holm sur les trois.
    corr = commun.holm({k: v["p_hypergeometrique_unilateral"] for k, v in politique.items()})
    for k in politique:
        politique[k]["p_holm_3_definitions"] = corr[k]
    # Stratification par période (la date est un facteur de confusion possible) : attendu par strate
    # et p par permutation du statut « Modi » à l'intérieur de chaque période (définition combinée).
    import random
    est_pol = lambda r: "nota" in r["genres"] or "attualità" in r["sources_commentaire"]
    strates = {}
    for r in lignes:
        strates.setdefault(r["periode"] or "sans période", []).append(r)
    detail_strates, obs, att = [], 0, 0.0
    for nom, rs in strates.items():
        nm = sum(1 for r in rs if r["n_érotique"])
        npol = sum(1 for r in rs if est_pol(r))
        k = sum(1 for r in rs if r["n_érotique"] and est_pol(r))
        detail_strates.append({"periode": nom, "pieces": len(rs), "pieces_modi": nm, "pieces_politiques": npol,
                               "modi_et_politiques": k, "attendu": round(nm * npol / len(rs), 2)})
        obs += k
        att += nm * npol / len(rs)
    rnd = random.Random(11)
    sup = 0
    N = 10000
    for _ in range(N):
        tot = 0
        for rs in strates.values():
            m = [bool(r["n_érotique"]) for r in rs]
            rnd.shuffle(m)
            tot += sum(1 for x, r in zip(m, rs) if x and est_pol(r))
        sup += tot >= obs
    stratifie = {"definition": "nota_ou_commentaire_politique", "observe": obs, "attendu": round(att, 2),
                 "p_permutation_dans_les_periodes_unilateral": round((sup + 1) / (N + 1), 4),
                 "strates": sorted(detail_strates, key=lambda d: d["periode"])}
    res = {
        "modi_et_sujets_politiques": politique,
        "modi_et_sujets_politiques_stratifie_par_periode": stratifie,
        "modi_et_sujets_politiques_note": (
            "Trois définitions essayées, p corrigés par Holm. Circularité : les Modi ont été cherchés "
            "surtout sur les plats du Sac et de Pavie (Talvacchia, Petruzzellis Scherer, Mallet). "
            "L'association s'accorde aussi avec Mallet (poses athlétiques, corps renversés utiles aux "
            "scènes violentes). Verdict : fragile, descriptif."),
        "pieces_avec_inscription": sum(r["inscription_presente"] for r in lignes),
        "genres_comptes": dict(Counter(groupe(r) for r in lignes)),
        "sources_litteraires_comptes": {k: sum(1 for r in lignes if k in r["sources_litteraires"]) for k in LITTERAIRES},
        "contingence_genre_x_type_estampe": conting,
        "contingence_genre_x_source_litteraire": lit_tab,
        "contingence_genre_x_source_selon_commentaire": com_tab,
        "genre_par_annee": genre_annee,
        "pieces_aux_modi": {"n": len(modi), "genres": dict(Counter(groupe(r) for r in modi)),
                            "ids": [r["id"] for r in modi]},
        "sporcitia": [{"id": r["id"], "types_estampes": {t: r["n_" + t.split("/")[0]] for t in TYPES}}
                      for r in lignes if "sporcitia" in r["genres"]],
        "marque_y_slash_et_genre": dict(Counter((r["marque_y_slash"], groupe(r) != "aucun") for r in lignes)),
    }
    res["marque_y_slash_et_genre"] = {f"y/Ø={k[0]}, mot de genre={k[1]}": v
                                      for k, v in res["marque_y_slash_et_genre"].items()}
    commun.ecrire_json(OUT / "resultats.json", res)
    print("T-revers", res["genres_comptes"], res["sources_litteraires_comptes"])
    for c in conting:
        print("  ", {k: v for k, v in c.items() if k != "ids"})
    print("  modi", res["pieces_aux_modi"]["genres"], res["sporcitia"], res["marque_y_slash_et_genre"])
    print("  modi x politique", {k: (v["modi_dans_categorie"], v["attendu_si_hasard"], v["p_hypergeometrique_unilateral"],
                                     v["p_holm_3_definitions"]) for k, v in politique.items()},
          {k: v for k, v in stratifie.items() if k != "strates"}, stratifie["strates"])
    return res


if __name__ == "__main__":
    main()
