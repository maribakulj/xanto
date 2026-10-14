#!/usr/bin/env python3
"""Compare des variantes à une base, requête par requête, sur le rang final de la vraie estampe (règles des préinscriptions).
Test du signe exact (égalités exclues) ; contrôle agrégé par estampe (PREINSCRIPTION_PAIRES.md) : une voix par estampe,
signe de la somme des log(rang base / rang variante).
Usage : comparer.py <base.csv> <variante.csv> [...]"""
import csv, sys
from math import comb, log
from collections import defaultdict
def ld(f): return {r["requete"]: r for r in csv.DictReader(open(f))}
def signe(up, dn):
    n = up + dn
    return min(1, 2 * sum(comb(n, k) for k in range(max(up, dn), n + 1)) / 2 ** n) if n else 1
b = ld(sys.argv[1])
for f in sys.argv[2:]:
    v = ld(f); qs = [q for q in v if q in b]; R = lambda d, q: int(d[q]["rang_aikon"])
    up = sum(R(v, q) < R(b, q) for q in qs); dn = sum(R(v, q) > R(b, q) for q in qs)
    c = lambda d, k: sum(R(d, q) <= k for q in qs); r = sorted(R(v, q) for q in qs)
    est = defaultdict(float)
    for q in qs: est[v[q]["bartsch"]] += log(R(b, q) / R(v, q))
    eu = sum(x > 0 for x in est.values()); ed = sum(x < 0 for x in est.values())
    sa = [float(v[q]["score_absente"]) for q in qs]; sv = [float(v[q]["score_vraie"]) for q in qs if v[q]["score_vraie"]]
    print(f"{f.split('/')[-1]} : {len(qs)} requêtes | base @1 {c(b,1)} @10 {c(b,10)} @50 {c(b,50)} | variante @1 {c(v,1)} @10 {c(v,10)} @50 {c(v,50)}"
          f" méd {r[len(r)//2]} | monte {up} descend {dn} net {up-dn} p={signe(up, dn):.3f} | par estampe ({len(est)}) {eu}/{ed} p={signe(eu, ed):.3f}"
          f" | vraies {min(sv, default='-')}-{max(sv, default='-')} absentes {min(sa)}-{max(sa)}")
