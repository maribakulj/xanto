#!/usr/bin/env python3
"""Accord entre deux encadrements (PREINSCRIPTION_PAIRES.md) : IoU des boîtes et accord sur « trouve », requête par requête.
Usage : accord_boites.py <dossier_prive> <prefixeA> <prefixeB>   (ex. v2_ ctrl2 ; v2_ boites_)"""
import csv, sys
from pathlib import Path
D = Path(sys.argv[1])
def lire(pref): return {r["requete"]: r for p in sorted(D.glob(f"{pref}*boites.csv")) for r in csv.DictReader(open(p))}
A, B = lire(sys.argv[2]), lire(sys.argv[3])
def iou(a, b):
    try: a, b = [tuple(float(r[k]) for k in ("x0", "y0", "x1", "y1")) for r in (a, b)]
    except ValueError: return None
    if a[0] != a[0]: return None
    w = max(0, min(a[2], b[2]) - max(a[0], b[0])); h = max(0, min(a[3], b[3]) - max(a[1], b[1])); i = w * h
    u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else 0
qs = sorted(set(A) & set(B)); v = []
for q in qs:
    x = iou(A[q], B[q]) if A[q]["photo"] == B[q]["photo"] else 0.0
    v.append(x); print(q, A[q]["trouve"], B[q]["trouve"], "-" if x is None else round(x, 2))
ok = [x for x in v if x is not None]
print(f"{len(qs)} requêtes communes ; boîtes comparables {len(ok)} ; IoU médian {sorted(ok)[len(ok)//2]:.2f} ; IoU ≥ 0,5 : {sum(x >= .5 for x in ok)} ;"
      f" IoU < 0,1 (figure différente) : {sum(x < .1 for x in ok)} ; même « trouve » : {sum(A[q]['trouve'] == B[q]['trouve'] for q in qs)}")
