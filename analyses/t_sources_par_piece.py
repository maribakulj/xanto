#!/usr/bin/env python3
"""T-sources-per-plate : nombre d'estampes distinctes citées par pièce, dans le temps
(complexité du collage). Deux comptes : Bartsch seul ; Bartsch + I Modi.
Moyenne calculée sur les pièces qui ont au moins une source identifiée (une fiche muette ne dit pas
qu'il n'y a pas de source). Sorties dans analyses/t-sources-par-piece/.
"""
from collections import Counter, defaultdict

import commun

OUT = commun.ICI / "t-sources-par-piece"


def resume(vals):
    v = [x for x in vals if x > 0]
    return {"pieces": len(vals), "pieces_avec_source": len(v),
            "part_avec_source": round(len(v) / len(vals), 3) if vals else None,
            "moyenne_si_source": round(sum(v) / len(v), 2) if v else None,
            "mediane_si_source": sorted(v)[len(v) // 2] if v else None,
            "max": max(v) if v else 0,
            "distribution": dict(sorted(Counter(vals).items()))}


def test_moyenne(a, b, n=10000, graine=3):
    import random
    rnd = random.Random(graine)
    obs = sum(b) / len(b) - sum(a) / len(a)
    tout = a + b
    k = 0
    for _ in range(n):
        rnd.shuffle(tout)
        d = sum(tout[len(a):]) / len(b) - sum(tout[:len(a)]) / len(a)
        k += abs(d) >= abs(obs) - 1e-12
    return {"difference_moyennes": round(obs, 3), "p_permutation_bilateral": round((k + 1) / (n + 1), 4)}


def main():
    fiches, cits, _ = commun.charger(avec_modi=True)
    bart, tous = defaultdict(set), defaultdict(set)
    for c in cits:
        tous[c["id"]].add(c["estampe"])
        if c["estampe"] != "MODI":
            bart[c["id"]].add(c["estampe"])
    lignes = [{"id": f["id"], "annee": f["annee"], "periode": f["periode"], "source_date": f["source_date"],
               "n_estampes_bartsch": len(bart[f["id"]]), "n_estampes_avec_modi": len(tous[f["id"]]),
               "estampes": " ".join(sorted(tous[f["id"]])), "link": f["link"]} for f in fiches]
    commun.ecrire_csv(OUT / "sources_par_piece.csv", lignes)
    par_annee = []
    for a in sorted({r["annee"] for r in lignes if r["annee"]}):
        rs = [r for r in lignes if r["annee"] == a]
        par_annee.append({"annee": a, **{k: v for k, v in resume([r["n_estampes_avec_modi"] for r in rs]).items()
                                         if k != "distribution"}})
    commun.ecrire_csv(OUT / "par_annee.csv", par_annee)
    res = {"global_bartsch": resume([r["n_estampes_bartsch"] for r in lignes]),
           "global_avec_modi": resume([r["n_estampes_avec_modi"] for r in lignes]),
           "par_periode_avec_modi": {p: resume([r["n_estampes_avec_modi"] for r in lignes if r["periode"] == p])
                                     for p, _, _ in commun.PERIODES},
           "par_periode_dates_inscrites": {p: resume([r["n_estampes_avec_modi"] for r in lignes
                                                      if r["periode"] == p and r["source_date"] == "inscription"])
                                           for p, _, _ in commun.PERIODES},
           "test_1531-1535_vs_1536-1542_moyenne_si_source": test_moyenne(
               [r["n_estampes_avec_modi"] for r in lignes if r["periode"] == "1531-1535" and r["n_estampes_avec_modi"]],
               [r["n_estampes_avec_modi"] for r in lignes if r["periode"] == "1536-1542" and r["n_estampes_avec_modi"]]),
           "par_annee": par_annee,
           "pieces_a_4_estampes_ou_plus": [{"id": r["id"], "annee": r["annee"], "n": r["n_estampes_avec_modi"]}
                                           for r in lignes if r["n_estampes_avec_modi"] >= 4]}
    commun.ecrire_json(OUT / "resultats.json", res)
    print("T-sources", {p: (v["part_avec_source"], v["moyenne_si_source"]) for p, v in res["par_periode_avec_modi"].items()},
          {p: (v["part_avec_source"], v["moyenne_si_source"]) for p, v in res["par_periode_dates_inscrites"].items()})
    return res


if __name__ == "__main__":
    main()
