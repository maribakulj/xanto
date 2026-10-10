#!/usr/bin/env python3
"""T-rebaptism (D2) : la figure empruntée garde-t-elle son identité (Apollon reste Apollon) ou
en change-t-elle (une Muse devient Circé) ?

Pour chaque référence (Bartsch + I Modi), on lit la proposition de la fiche :
  « [cible] è ripresa/tratta/desunta/citata… [source] (Bartsch …) »
- cible = nom propre de la figure peinte (avant le verbe) ; sinon « générique » (la fanciulla…) ;
- source explicite = « dalla figura di X », « dal personaggio di X », « dalle Muse … » après le verbe ;
- sinon, figures connues de l'estampe (liste ESTAMPES de commun.py).
Classes : conservée (explicite) / changée (explicite) / conservée (présumée : le nom figure dans la
liste de l'estampe) / changée (présumée : l'estampe a des figures nommées, le nom n'y est pas) /
anonyme → nommée (estampe sans figure nommée : bataille, Modi, nu…) / cible générique / non classé.
Ces classes sont des approximations ; voir les limites dans le README.
Sorties dans analyses/t-rebapteme/.
"""
import re
from collections import Counter

import commun

OUT = commun.ICI / "t-rebapteme"
VERBE = re.compile(r"\b(?:ripres[oaie]|tratt[oaie]|desunt[oaie]|citat[oaie]|mutuat[oaie]|derivat[oaie]|"
                   r"pres[oaie]|copiat[oaie]|ispirat[oaie]|è citazione|citazione|deriva(?:no)?|provien[ei]|"
                   r"richiamo|riferimento|rifà|rifa)\b", re.I)
# estampes dont la plupart des figures sont anonymes (foule, soldats, spectateurs, amants) : une cible
# nommée absente de la liste des protagonistes vient très probablement d'une figure anonyme
FOULE = {"B26.104", "B26.21", "B26.117", "B26.23", "B26.8", "B27.420", "B26.211", "MODI", "B26.226",
         "B27.464", "B27.442", "B28.57", "B27.384", "B27.373", "B26.185"}
EXPLICITE = re.compile(r"(?:figura|personaggio|figure)\s+(?:di|del|della|dell’|dell'|dello|dei|delle)\s*"
                       r"([A-ZÈ][\w’']+)|\bdall[ae’']\s*(Muse|Musa)\b")
MOTS_VIDES = set("""La Il Lo Le Gli I L Per In Nel Nella Questa Questo Xanto Avelli Francesco Mentre Infine
Inoltre Anche Come Ma E Ed Si Sulla Sul Al Alla Da Dal Dalla Di Del Della Una Un Uno Tale Tali Qui Ancora Ciò
Fino Già Bartsch Marcantonio Raimondi Raffaello Caraglio Rosso Giulio Romano Baccio Bandinelli Marco Dente
Ravenna Agostino Veneziano Gian Giacomo Maestro Monogrammista Parmigianino Lawner Scheda Oltre Invece Tutte
Tutti Sono Nello Negli Nei Ogni Altre Altri Altro Altra Entrambe Entrambi Così Tra Fra Sempre Poi Quanto
Questi Queste Sebbene Forse Probabilmente Possibile Evidente Interessante Va Vi Ci Le Più Meno Quindi Dunque
Sopra Sotto Dietro Davanti Accanto Allo Alle Agli Ai Lungo Con Senza Pur Pure Anzi Ovvero Oppure O""".split())
GENERIQUES = re.compile(r"\b(?:fanciull[ae]|uom[oi]|donn[ae]|soldat[oi]|guerrier[oi]|vecchi[oa]|anzian[oa]|"
                        r"giovan[ei]|ragazz[oa]|figur[ae]|personagg[io]+|cavalier[ei]|nudo|nudi|gruppo|coppia|"
                        r"bambin[oi]|madr[ei]|ancell[ae]|marinai?o|spettator[ei]|inserviente|pastor[ei]|"
                        r"ninf[ae]|divinità|dio del fiume|fiume|cavallo|testa|gambe|corpo|parte)\b", re.I)
SYN = {"amore": "cupido", "amorino": "cupido", "putto": "cupido", "putti": "cupido", "cupidi": "cupido",
       "dioniso": "bacco", "musa": "muse", "calliope": "muse", "erato": "muse", "pieride": "pieridi",
       "sol": "apollo", "sole": "apollo", "grazia": "grazie", "naiade": "ninfa", "venere": "venere",
       "mercurio": "mercurio", "giove": "giove", "ercole": "ercole", "hercole": "ercole"}


def norm(n):
    n = n.lower().strip("’'")
    return SYN.get(n, n)


def cible(seg):
    """Nom propre le plus proche du verbe ; '' si le sujet le plus proche est un nom commun."""
    ms = list(re.finditer(r"(?:figura|personaggio)\s+(?:di|del|della|dell’|dell'|dello)\s*([A-ZÈ][\w’']+)", seg))
    if ms and len(seg) - ms[-1].end() < 60:
        return ms[-1].group(1)
    fen = seg[-70:]
    toks = [m for m in re.finditer(r"(?<![’'\w])([A-ZÈ][a-zàèéìòù]{2,})\b(?![’'])", fen) if m.group(1) not in MOTS_VIDES]
    if not toks:
        return ""
    if GENERIQUES.search(fen[toks[-1].end():]):
        return ""
    return toks[-1].group(1)


def classer(c):
    g = c["_gauche"]
    vs = list(VERBE.finditer(g))
    if not vs:
        return {"classe": "non classé (liste ou phrase sans verbe d'emprunt)", "cible": "", "source": ""}
    # verbe d'emprunt : le premier suivi d'une préposition « da… » (hors « a sua volta »), sinon le dernier
    bons = [m for m in vs if re.match(r"[^;]{0,40}?\b(?:da|dal|dalla|dallo|dall’|dall'|dai|dagli|dalle)\b", g[m.end():])
            and not re.match(r"\s*a sua volta", g[m.end():])]
    v = bons[0] if bons else vs[-1]
    avant, apres = g[:v.start()], g[v.end():]
    t = cible(avant)
    fig = {norm(x) for x in commun.ESTAMPES.get(c["estampe"], ("", "", "", ""))[3].split()} - {""}
    m = EXPLICITE.search(apres)
    if not t:
        return {"classe": "cible générique" if GENERIQUES.search(avant) else "non classé (cible introuvable)",
                "cible": "", "source": m.group(1) or m.group(2) if m else ""}
    if m:
        s = m.group(1) or m.group(2)
        return {"classe": "conservée (explicite)" if norm(s) == norm(t) else "changée (explicite)",
                "cible": t, "source": s}
    if norm(t) in fig:
        return {"classe": "conservée (présumée)", "cible": t, "source": ""}
    if not fig or c["estampe"] in FOULE:
        return {"classe": "anonyme → nommée (présumée)", "cible": t, "source": ""}
    return {"classe": "changée (présumée)", "cible": t, "source": ""}


def main():
    fiches, cits, _ = commun.charger(avec_modi=True)
    F = commun.par_id(fiches)
    lignes = []
    for c in cits:
        r = classer(c)
        f = F[c["id"]]
        lignes.append({"id": c["id"], "estampe": c["estampe"], "titre_estampe": c["titre_estampe"],
                       "classe": r["classe"], "cible": r["cible"], "figure_source": r["source"],
                       "annee": f["annee"], "periode": f["periode"], "link": f["link"]})
    commun.ecrire_csv(OUT / "rebapteme_par_reference.csv", lignes)
    cpt = Counter(r["classe"] for r in lignes)
    nommees = [r for r in lignes if r["classe"].startswith(("conservée", "changée", "anonyme"))]
    ident = [r for r in lignes if r["classe"].startswith(("conservée", "changée"))]
    chg = [r for r in ident if r["classe"].startswith("changée")]
    expl = [r for r in ident if "explicite" in r["classe"]]
    par_periode = {}
    for p, _, _ in commun.PERIODES:
        sub = [r for r in ident if r["periode"] == p]
        par_periode[p] = {"n": len(sub), "changees": sum(r["classe"].startswith("changée") for r in sub),
                          "part_changees": round(sum(r["classe"].startswith("changée") for r in sub) / len(sub), 3)
                          if sub else None}
    par_estampe = []
    for k, _ in Counter(r["estampe"] for r in ident).most_common(15):
        sub = [r for r in ident if r["estampe"] == k]
        par_estampe.append({"estampe": k, "titre": sub[0]["titre_estampe"], "n": len(sub),
                            "changees": sum(r["classe"].startswith("changée") for r in sub),
                            "cibles": dict(Counter(r["cible"] for r in sub).most_common(8))})
    exemples = {cl: [{"id": r["id"], "cible": r["cible"], "figure_source": r["figure_source"],
                      "estampe": r["estampe"], "link": r["link"]} for r in lignes if r["classe"] == cl][:25]
                for cl in cpt}
    res = {"n_references": len(lignes), "classes": dict(cpt),
           "references_a_cible_nommee": len(nommees),
           "part_identite_changee_parmi_conservee_ou_changee": round(len(chg) / len(ident), 3) if ident else None,
           "part_identite_changee_explicite_seulement": round(sum(r["classe"] == "changée (explicite)" for r in expl)
                                                             / len(expl), 3) if expl else None,
           "part_changee_ou_anonyme_vers_nommee_parmi_cibles_nommees":
               round(sum(not r["classe"].startswith("conservée") for r in nommees) / len(nommees), 3) if nommees else None,
           "sans_cupido": (lambda sub: {"n": len(sub), "changees": sum(r["classe"].startswith("changée") for r in sub),
                                        "part_changees": round(sum(r["classe"].startswith("changée") for r in sub)
                                                               / len(sub), 3) if sub else None})(
               [r for r in ident if norm(r["cible"]) != "cupido"]),
           "cibles_cupido": sum(1 for r in nommees if norm(r["cible"]) == "cupido"),
           "par_periode": par_periode, "par_estampe": par_estampe, "exemples": exemples}
    commun.ecrire_json(OUT / "resultats.json", res)
    print("T-rebaptism", res["classes"], res["part_identite_changee_parmi_conservee_ou_changee"],
          res["part_identite_changee_explicite_seulement"], res["part_changee_ou_anonyme_vers_nommee_parmi_cibles_nommees"])
    return res


if __name__ == "__main__":
    main()
