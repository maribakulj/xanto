#!/usr/bin/env python3
"""T-reuse (C1) : réemploi des estampes dans le temps.

Pour chaque estampe (clé Bartsch « B<vol>.<n> ») : pièces et années ; première / dernière année.
Par année : nombre d'estampes distinctes utilisées, nombre et part d'estampes « nouvelles »
(première apparition datée cette année-là). Par période : concentration (part des 5 estampes les
plus citées, indice de Herfindahl, estampes distinctes / références), références par pièce,
combinaisons d'estampes identiques à celle d'une pièce antérieure.

Contrôle : une baisse des estampes « nouvelles » en fin de carrière est attendue même sans
changement de méthode (on a déjà vu la plupart des estampes). On compare donc la valeur observée
à celle obtenue en permutant les années entre pièces (10 000 tirages).

Deux variantes : « toutes » (année retenue, y compris « ca. » et milieux d'intervalle) et
« inscrites » (seulement les années lues sur la pièce).
Sorties dans analyses/t-reemploi/.
"""
import random
from collections import Counter, defaultdict

import commun

OUT = commun.ICI / "t-reemploi"
TARDIF = 1536


def periode(a):
    for nom, lo, hi in commun.PERIODES:
        if lo <= a <= hi:
            return nom


def nouveautes(pieces):
    """pieces : liste (id, annee, set(estampes)). Renvoie stats par année."""
    premiere = {}
    for _, a, es in sorted(pieces, key=lambda x: x[1]):
        for e in es:
            premiere.setdefault(e, a)
    par = defaultdict(lambda: {"pieces": 0, "pieces_avec_ref": 0, "references": 0, "estampes": set()})
    for i, a, es in pieces:
        d = par[a]
        d["pieces"] += 1
        d["pieces_avec_ref"] += bool(es)
        d["references"] += len(es)
        d["estampes"] |= es
    out = []
    for a in sorted(par):
        d = par[a]
        nv = sorted(e for e in d["estampes"] if premiere[e] == a)
        out.append({"annee": a, "pieces": d["pieces"], "pieces_avec_ref": d["pieces_avec_ref"],
                    "references": d["references"], "estampes_distinctes": len(d["estampes"]),
                    "estampes_nouvelles": len(nv), "part_nouvelles": round(len(nv) / len(d["estampes"]), 3)
                    if d["estampes"] else None, "liste_nouvelles": " ".join(nv)})
    return out, premiere


def stat_tardive_base(pieces):
    """Nombre d'estampes introduites à partir de 1536 et part des références tardives qui vont à ces
    estampes nouvelles."""
    premiere = {}
    for _, a, es in sorted(pieces, key=lambda x: x[1]):
        for e in es:
            premiere.setdefault(e, a)
    nouv = {e for e, a in premiere.items() if a >= TARDIF}
    refs_t = [e for _, a, es in pieces if a >= TARDIF for e in es]
    return len(nouv), (sum(e in nouv for e in refs_t) / len(refs_t) if refs_t else 0)


def stat_combinaisons(pieces):
    """Part des pièces tardives (>= 1536) à 2 estampes ou plus dont la combinaison exacte
    d'estampes a déjà été vue sur une pièce antérieure (ex aequo d'année : ordre des ids)."""
    vus, rep, tot = set(), 0, 0
    for i, a, es in sorted(pieces, key=lambda x: (x[1], x[0])):
        if len(es) >= 2:
            if a >= TARDIF:
                tot += 1
                rep += frozenset(es) in vus
            vus.add(frozenset(es))
    return rep / tot if tot else 0


def stat_tardive(pieces):
    return stat_tardive_base(pieces) + (stat_combinaisons(pieces),)


def null_permutation(pieces, n=10000, graine=7):
    rnd = random.Random(graine)
    obs = stat_tardive(pieces)
    annees = [a for _, a, _ in pieces]
    sims = []
    for _ in range(n):
        rnd.shuffle(annees)
        sims.append(stat_tardive([(i, a, es) for (i, _, es), a in zip(pieces, annees)]))
    out = {}
    for j, nom in enumerate(("estampes_introduites_des_1536", "part_refs_tardives_vers_estampes_nouvelles",
                              "part_pieces_tardives_a_combinaison_deja_vue")):
        vals = sorted(s[j] for s in sims)
        out[nom] = {"observe": round(obs[j], 3), "moyenne_permutations": round(sum(vals) / n, 3),
                    "intervalle_95": [round(vals[int(.025 * n)], 3), round(vals[int(.975 * n)], 3)],
                    "p_inferieur_ou_egal": round((sum(v <= obs[j] for v in vals) + 1) / (n + 1), 4),
                    "p_superieur_ou_egal": round((sum(v >= obs[j] for v in vals) + 1) / (n + 1), 4)}
    return out


def concentration(refs):
    c = Counter(refs)
    n = sum(c.values())
    if not n:
        return {}
    return {"references": n, "estampes_distinctes": len(c),
            "distinctes_par_reference": round(len(c) / n, 3),
            "part_top5": round(sum(v for _, v in c.most_common(5)) / n, 3),
            "herfindahl": round(sum((v / n) ** 2 for v in c.values()), 4),
            "top5": [k for k, _ in c.most_common(5)]}


def main():
    fiches, cits, _ = commun.charger()
    F = commun.par_id(fiches)
    est_par_piece = defaultdict(set)
    for c in cits:
        est_par_piece[c["id"]].add(c["estampe"])

    variantes = {
        "toutes": [(f["id"], f["annee"], est_par_piece.get(f["id"], set())) for f in fiches if f["annee"]],
        "inscrites": [(f["id"], f["annee"], est_par_piece.get(f["id"], set())) for f in fiches
                      if f["source_date"] == "inscription"],
    }
    res = {"note": "references = estampes distinctes par pièce (une estampe citée deux fois dans une fiche compte une fois)"}

    # réemploi par estampe (toutes les fiches, datées ou non)
    par_estampe = []
    for e in sorted({c["estampe"] for c in cits}):
        ids = sorted(i for i, es in est_par_piece.items() if e in es)
        ans = sorted(F[i]["annee"] for i in ids if F[i]["annee"])
        info = commun.ESTAMPES.get(e, ("", "", ""))
        par_estampe.append({"estampe": e, "titre": info[0], "graveur": info[1], "type": info[2],
                            "n_pieces": len(ids), "premiere_annee": ans[0] if ans else None,
                            "derniere_annee": ans[-1] if ans else None,
                            "pieces": [{"id": i, "annee": F[i]["annee"], "source_date": F[i]["source_date"],
                                        "link": F[i]["link"]} for i in ids]})
    par_estampe.sort(key=lambda r: -r["n_pieces"])
    res["par_estampe"] = par_estampe
    combos = defaultdict(list)
    for f in fiches:
        es = est_par_piece.get(f["id"], set())
        if len(es) >= 2:
            combos[frozenset(es)].append((f["annee"], f["id"]))
    res["combinaisons_repetees"] = [{"estampes": sorted(k), "pieces": [{"id": i, "annee": a} for a, i in
                                     sorted(v, key=lambda x: (x[0] or 9999, x[1]))]}
                                    for k, v in sorted(combos.items(), key=lambda kv: -len(kv[1])) if len(v) > 1]
    commun.ecrire_csv(OUT / "combinaisons_repetees.csv",
                      [{"estampes": " + ".join(c["estampes"]), "n_pieces": len(c["pieces"]),
                        "pieces": " ".join(f"{p['id']}:{p['annee']}" for p in c["pieces"])}
                       for c in res["combinaisons_repetees"]])
    commun.ecrire_csv(OUT / "reemploi_par_estampe.csv",
                      [dict(r, pieces=" ".join(f"{p['id']}:{p['annee']}" for p in r["pieces"])) for r in par_estampe])

    for nom, pieces in variantes.items():
        par_an, premiere = nouveautes(pieces)
        commun.ecrire_csv(OUT / f"par_annee_{nom}.csv", par_an)
        per = {}
        for p, lo, hi in commun.PERIODES:
            sub = [x for x in pieces if lo <= x[1] <= hi]
            refs = [e for _, _, es in sub for e in es]
            avec = [x for x in sub if x[2]]
            nv = {e for e, a in premiere.items() if lo <= a <= hi}
            # combinaisons (>= 2 estampes) identiques à celle d'une pièce antérieure
            vus, rep = set(), 0
            for i, a, es in sorted(pieces, key=lambda x: x[1]):
                if len(es) >= 2:
                    if lo <= a <= hi and frozenset(es) in vus:
                        rep += 1
                    vus.add(frozenset(es))
            multi = sum(1 for x in sub if len(x[2]) >= 2)
            per[p] = dict(concentration(refs), pieces=len(sub), pieces_avec_ref=len(avec),
                          part_pieces_avec_ref=round(len(avec) / len(sub), 3) if sub else None,
                          refs_par_piece_avec_ref=round(len(refs) / len(avec), 2) if avec else None,
                          estampes_nouvelles=len(nv),
                          part_estampes_nouvelles=round(len(nv) / len(set(refs)), 3) if refs else None,
                          pieces_a_2_estampes_ou_plus=multi,
                          combinaisons_deja_vues=rep)
        res[f"variante_{nom}"] = {"par_annee": par_an, "par_periode": per,
                                  "controle_permutation": null_permutation(pieces)}
        print("T-reuse", nom, {p: (v.get("estampes_nouvelles"), v.get("part_estampes_nouvelles"),
                                   v.get("part_top5"), v.get("refs_par_piece_avec_ref"),
                                   v.get("combinaisons_deja_vues")) for p, v in per.items()})
        print("   permutation", res[f"variante_{nom}"]["controle_permutation"])
    commun.ecrire_json(OUT / "resultats.json", res)
    return res


if __name__ == "__main__":
    main()
