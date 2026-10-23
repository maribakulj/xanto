#!/usr/bin/env python3
"""Accord entre deux annotateurs, et accord de chacun avec les boîtes de l'IA.

Usage : python3 annotation/comparer.py export_A.json export_B.json [--csv detail.csv]

Lit deux exports JSON de la page d'annotation. Pour chaque tâche, ne compte que les éléments répondus par les deux.
  - Paires connues : accord sur trouvée / incertaine / introuvable (pourcentage, kappa de Cohen), accord sur « inversée »,
    IoU des rectangles sur le plat, IoU des rectangles sur l'estampe (même épreuve seulement),
    IoU de chaque annotateur avec la boîte de l'IA et accord avec le « trouvé » de l'IA.
  - Sources proposées : accord oui / peut-être / non, et oui contre le reste.
  - Absences : accord sur le verdict.
Les rectangles sont en pixels de l'image originale. Python 3 seul, sans dépendance."""
import csv, json, statistics, sys
from collections import Counter


def charger(p):
    o = json.load(open(p, encoding="utf-8"))
    if o.get("format") != "xanto-annotation":
        sys.exit(f"{p} : pas un export de la page d'annotation")
    return o


def iou(a, b):
    if not a or not b or len(a) != 4 or len(b) != 4:
        return None
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = ix * iy; u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i
    return i / u if u > 0 else None


def kappa(x, y):
    """Kappa de Cohen entre deux listes d'étiquettes (None si non défini)."""
    n = len(x)
    if n == 0:
        return None
    po = sum(a == b for a, b in zip(x, y)) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum(cx[c] * cy[c] for c in set(x) | set(y)) / n ** 2
    return None if pe >= 1 else (po - pe) / (1 - pe)


def f(v, d=2):
    return "n/a" if v is None else f"{v:.{d}f}"


def resume_iou(v):
    v = [x for x in v if x is not None]
    if not v:
        return "aucune paire de boîtes"
    return f"n={len(v)}, IoU moyen {statistics.mean(v):.2f}, médian {statistics.median(v):.2f}, ≥ 0,5 : {100 * sum(x >= .5 for x in v) / len(v):.0f} %"


def accord(ra, rb, champ, titre, lignes, tache):
    ks = sorted(k for k in ra if k in rb and ra[k].get(champ) and rb[k].get(champ) and k[0] == tache)
    x = [ra[k][champ] for k in ks]; y = [rb[k][champ] for k in ks]
    if not ks:
        print(f"{titre} : aucun élément répondu par les deux"); return ks
    print(f"{titre} : n={len(ks)}, accord {100 * sum(a == b for a, b in zip(x, y)) / len(ks):.0f} %, kappa {f(kappa(x, y))}")
    for k, a, b in zip(ks, x, y):
        lignes.append({"tache": titre, "cle": k, "A": a, "B": b})
    return ks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    A, B = charger(args[0]), charger(args[1]); ra, rb = A["reponses"], B["reponses"]
    na, nb = A.get("annotateur", "A"), B.get("annotateur", "B")
    lignes = []
    print(f"A = {na} ({len(ra)} réponses) ; B = {nb} ({len(rb)} réponses)\n")

    print("== 1. Paires connues")
    ks = accord(ra, rb, "statut", "statut trouvée/incertaine/introuvable", lignes, "P")
    accord(ra, rb, "inverse", "inversée oui/non", lignes, "P")
    comm = [k for k in ks]
    print("IoU des boîtes sur le plat :", resume_iou([iou(ra[k].get("box_plat"), rb[k].get("box_plat")) for k in comm]))
    memes = [k for k in comm if ra[k].get("epreuve") and ra[k].get("epreuve") == rb[k].get("epreuve")]
    print(f"IoU des boîtes sur l'estampe (même épreuve : {len(memes)}/{len(comm)}) :", resume_iou([iou(ra[k].get("box_estampe"), rb[k].get("box_estampe")) for k in memes]))
    for k in comm:
        lignes.append({"tache": "iou_plat", "cle": k, "A": iou(ra[k].get("box_plat"), rb[k].get("box_plat")), "B": ""})

    print("\n   Accord avec l'IA (tous les éléments de chaque annotateur)")
    for nom, r in ((na, ra), (nb, rb)):
        P = {k: v for k, v in r.items() if k[0] == "P"}
        vus = sum(1 for v in P.values() if v.get("ia_vue"))
        print(f"  {nom} : boîte de l'IA vue sur {vus}/{len(P)} éléments ;", "plat :", resume_iou([iou(v.get("box_plat"), v.get("ia_plat")) for v in P.values()]))
        sans = {k: v for k, v in P.items() if not v.get("ia_vue")}
        if sans and len(sans) != len(P):
            print(f"      dont annotation indépendante ({len(sans)}) :", resume_iou([iou(v.get("box_plat"), v.get("ia_plat")) for v in sans.values()]))
        paires = [(v["statut"], {"oui": "trouve"}.get(v.get("ia_trouve"), v.get("ia_trouve"))) for v in P.values() if v.get("statut") and v.get("ia_trouve")]
        if paires:
            print(f"      statut vs « trouvé » de l'IA : n={len(paires)}, accord {100 * sum(a == b for a, b in paires) / len(paires):.0f} %, kappa {f(kappa([a for a, _ in paires], [b for _, b in paires]))}")

    print("\n== 2. Sources proposées")
    ks = accord(ra, rb, "jugement", "oui/peut-être/non", lignes, "S")
    if ks:
        x = ["oui" if ra[k]["jugement"] == "oui" else "autre" for k in ks]; y = ["oui" if rb[k]["jugement"] == "oui" else "autre" for k in ks]
        print(f"oui contre le reste : accord {100 * sum(a == b for a, b in zip(x, y)) / len(ks):.0f} %, kappa {f(kappa(x, y))}")

    print("\n== 3. Absences")
    accord(ra, rb, "verdict", "absence/ailleurs/incertain", lignes, "A")

    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["tache", "cle", "A", "B"]); w.writeheader(); w.writerows(lignes)
        print(f"\nDétail écrit dans {out}")


if __name__ == "__main__":
    main()
