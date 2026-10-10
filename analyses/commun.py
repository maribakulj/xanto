#!/usr/bin/env python3
"""Fonctions communes aux tests descriptifs sur le catalogue « Xanto nel mondo » (Rovigo, 374 fiches).

Entrées (privées, hors dépôt) : le JSON complet des fiches (HTML) ; data/pieces.csv du dépôt.
Rien de ce module n'écrit le texte des commentaires : les scripts de test n'exportent que des
identifiants, des comptes, des étiquettes de classement et des liens.

Tout est extrait par expressions régulières : chaque ligne est À VÉRIFIER sur la fiche.
"""
import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
DEPOT = ICI.parent
PRIVE = Path("/Users/marcel/Documents/Codex/2026-10-08-continuation-claude/sources-libres")
JSON_FICHES = PRIVE / "Rovigo_Xanto_catalogo_374_schede.json"
PIECES = DEPOT / "data" / "pieces.csv"

PERIODES = [("<=1530", 1400, 1530), ("1531-1535", 1531, 1535), ("1536-1542", 1536, 1545)]
DEBUT_URBINO = 1528  # première date sûre de Xanto à Urbino ; avant : groupe de Gubbio d'attribution débattue

# Filtre facultatif pour les analyses de sensibilité (t_sensibilite.py) : fonction fiche -> bool
# (True = on garde). None = toutes les fiches.
FILTRE = None

# --------------------------------------------------------------------------- texte


def texte(h):
    h = re.sub(r"<figure.*?</figure>", "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", h)
    return re.sub(r"[ \t\xa0]+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()


def _section(t, debut, fins=("Note", "Provenienza", "Esposizioni", "Bibliografia", "Commento")):
    m = re.search(debut + r"\s*:?(.*?)(?:\n\s*(?:" + "|".join(fins) + r")\b|$)", t, re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


# --------------------------------------------------------------------------- dates

ROMAINS = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}


def _romain(s):
    s = s.replace(".", "").upper()
    tot, prev = 0, 0
    for ch in reversed(s):
        v = ROMAINS.get(ch, 0)
        tot = tot - v if v < prev else tot + v
        prev = max(prev, v)
    return tot


def annee_inscrite(ins):
    """Année(s) lisible(s) dans l'inscription (arabe ou romaine). Renvoie (année, note)."""
    ans = [int(a) for a in re.findall(r"(?<!\d)(15[0-4]\d)(?!\d)", ins)]
    for m in re.finditer(r"\bM\.?\s*D\.?\s*(?:[XLVI]\.?\s*){1,8}", ins):
        v = _romain(re.sub(r"\s", "", m.group(0)))
        if 1500 <= v <= 1545:
            ans.append(v)
    ans = sorted(set(ans))
    if not ans:
        return None, ""
    note = "plusieurs années" if len(ans) > 1 else ""
    if re.search(r"M[°o]\s*G|Giorgio|Ugubio|Gubbio", ins):
        note = (note + "; date de lustre (Gubbio)").strip("; ")
    if dans_la_scene(ins):
        note = (note + "; date peinte dans la scène (droit seul)").strip("; ")
    return ans[-1] if len(ans) == 1 else ans[0], note


def dans_la_scene(ins):
    """Date lue seulement sur le droit (tablette, cartouche peints dans la scène), sans inscription au
    revers. Ce peut être une date figurée et non la date d'exécution (pièce 194 : « OMNIA VINCIT AMOR 1522 »)."""
    return bool(re.search(r"Sul verso|Sul davanti|in primo piano|tavol[ae]|tavolett|targhett|cartigli", ins, re.I)
                and not re.search(r"\bretro\b|sotto il piede|nel piede", ins, re.I))


def date_piece(champ_data, ins):
    """Année retenue + source. Priorité : inscription > catalogue année simple > catalogue « ca. » >
    intervalle (milieu). Renvoie dict(annee, amin, amax, source, precis, periode)."""
    a, note = annee_inscrite(ins)
    d = champ_data if len(champ_data) < 40 else ""
    ca = bool(re.search(r"\bca\b|circa", d))
    ys = [int(x) for x in re.findall(r"(?<!\d)(1[45]\d\d)(?!\d)", d)]
    if a and "dans la scène" in note and a < DEBUT_URBINO:
        # date figurée sur le droit, antérieure à 1528 : ne compte pas comme date inscrite d'exécution
        if len(ys) >= 1:
            lo, hi = min(ys), max(ys)
            return _fin(round((lo + hi) / 2), lo, hi, "catalogue (date peinte dans la scène, %d, non retenue)" % a,
                        False, note)
        return _fin(a, a, a, "date peinte dans la scène (à vérifier)", False, note)
    if a and "plusieurs" not in note:
        if len(ys) == 1 and ys[0] != a:  # désaccord : on garde l'année du catalogue, signalée
            return _fin(ys[0], ys[0], ys[0], "catalogue (désaccord avec l'inscription %d)" % a, False, note)
        return _fin(a, a, a, "inscription", True, note)
    if len(ys) == 1:
        return _fin(ys[0], ys[0], ys[0], "catalogue ca." if ca else "catalogue", not ca, note)
    if len(ys) >= 2:
        lo, hi = min(ys), max(ys)
        return _fin(round((lo + hi) / 2), lo, hi, "catalogue intervalle", False, note)
    if a:  # plusieurs années inscrites, rien d'autre
        return _fin(a, a, a, "inscription (ambiguë)", False, note)
    return _fin(None, None, None, "aucune", False, note)


def periode_de(amin, amax):
    if amin is None:
        return None
    for nom, lo, hi in PERIODES:
        if lo <= amin and amax <= hi:
            return nom
    return None  # intervalle à cheval sur deux périodes


def _fin(a, lo, hi, src, precis, note):
    return {"annee": a, "amin": lo, "amax": hi, "source_date": src, "precis": precis,
            "note_date": note, "periode": periode_de(lo, hi)}


# --------------------------------------------------------------------------- estampes

# Catalogue des estampes citées (titre court tel que dans les fiches ; graveur selon la majorité
# des fiches ; type de sujet ; figures nommées de l'estampe, pour le test de « rebaptême »).
# Les figures listées sont celles que les fiches nomment ou que le titre impose ; liste incomplète.
ESTAMPES = {
    "B26.247": ("Parnaso", "Marcantonio", "mythologique",
                "Apollo Muse Musa Calliope Saffo Omero Dante Petrarca Virgilio Ariosto Cupido Amore putto amorino"),
    "B28.53": ("Contesa tra le Muse e le Pieridi", "Caraglio", "mythologique", "Muse Musa Pieridi Pieride ninfa"),
    "B26.104": ("Martirio di San Lorenzo", "Marcantonio", "religieux", "Lorenzo Valeriano"),
    "B27.420": ("Battaglia tra Romani e Cartaginesi (Scena di battaglia)", "Marco Dente", "bataille", ""),
    "B27.352": ("Quos Ego", "Marcantonio", "mythologique",
                "Nettuno Eolo Enea Didone Venere Giove Giunone Mercurio Acate Cupido Amore Iride Ascanio"),
    "B28.62": ("Matrimonio di Alessandro e Rossana", "Caraglio", "historique", "Alessandro Rossana Efestione Imeneo Cupido Amore putto amorino"),
    "B26.209": ("Ratto di Elena", "Marcantonio", "mythologique", "Elena Paride"),
    "B26.21": ("Strage degli Innocenti", "Marco Dente", "religieux", "Erode"),
    "B26.211": ("Battaglia col coltellaccio / con la sciabola", "Marco Dente", "bataille", ""),
    "B26.217": ("Danza di Cupidi", "Marcantonio", "mythologique", "Cupido Amore putto amorino"),
    "B26.198": ("Cleopatra", "Agostino Veneziano", "historique", "Cleopatra Cupido Amore putto amorino"),
    "B26.6": ("Isacco che benedice Giacobbe", "Marcantonio", "religieux", "Isacco Giacobbe Rebecca Esaù"),
    "B26.10": ("Davide e Golia", "Marcantonio", "religieux", "Davide Golia"),
    "B26.23": ("Cristo in casa di Simone il Fariseo", "Marcantonio", "religieux", "Cristo Maddalena Simone"),
    "B16.14": ("Sol", "Maestro I.B.", "mythologique", "Sol Apollo"),
    "B26.117": ("Martirio di Santa Cecilia", "Marcantonio", "religieux", "Cecilia"),
    "B26.226": ("Uomo nudo che rincorre una ninfa", "Marcantonio", "mythologique", "ninfa Naiade"),
    "B26.245": ("Giudizio di Paride", "Marcantonio", "mythologique",
                "Paride Mercurio Venere Minerva Giunone Cupido Amore Apollo Diana Giove"),
    "B28.44": ("Ercole e Cerbero", "Caraglio", "mythologique", "Ercole Cerbero"),
    "B28.60": ("Enea che salva Anchise (Fuga di Enea)", "Caraglio", "mythologique", "Enea Anchise Ascanio Creusa"),
    "B26.232": ("Leda", "Agostino Veneziano", "mythologique", "Leda Giove cigno"),
    "B26.242": ("Trono di Saturno", "Marco Dente", "mythologique", "Saturno putto amorino"),
    "B27.373": ("Donna con due spugne", "Marcantonio", "autre", ""),
    "B28.49": ("Ercole e Caco", "Caraglio", "mythologique", "Ercole Caco"),
    "B27.442": ("Imperatore seduto", "Marcantonio", "autre", ""),
    "B27.323": ("Nascita di Venere", "Marco Dente", "mythologique", "Venere Nettuno fiume"),
    "B26.294": ("Giovane e sacerdote di Bacco", "Marcantonio", "mythologique", "Bacco Dioniso"),
    "B28.48": ("Ercole e Acheloo", "Caraglio", "mythologique", "Ercole Acheloo"),
    "B26.243": ("Laocoonte", "Marco Dente", "mythologique", "Laocoonte"),
    "B28.57": ("Scuola di un filosofo antico", "Caraglio", "autre", ""),
    "B28.4": ("Adorazione dei pastori", "Caraglio", "religieux", "Cristo Maria Giuseppe"),
    "B28.50": ("Mercurio porta Psiche sull'Olimpo", "Caraglio", "mythologique", "Mercurio Psiche"),
    "B27.464": ("Due uomini nudi", "Marcantonio", "autre", ""),
    "B26.313": ("Venere accovacciata", "Marcantonio", "mythologique", "Venere Cupido Amore putto amorino"),
    "B26.8": ("Israeliti che raccolgono la manna", "Agostino Veneziano", "religieux", "Mosè"),
    "B26.103": ("San Girolamo e il leone", "Agostino Veneziano", "religieux", "Girolamo"),
    "B16.16": ("Mercurio", "Maestro I.B.", "mythologique", "Mercurio"),
    "B16.12": ("Giove", "Maestro I.B. / Pencz", "mythologique", "Giove"),
    "B26.4": ("Sacrificio di Noè", "Marco Dente", "religieux", "Noè"),
    "B25.1": ("(stampa di Mantegna)", "Mantegna", "autre", ""),
    "B27.340": ("Tre Grazie", "Marcantonio", "mythologique", "Grazie Grazia"),
    "B27.193": ("Suicidio di Cleopatra", "Agostino Veneziano", "historique", "Cleopatra"),
    "B27.384": ("Giovane con la lanterna", "Marcantonio", "autre", ""),
    "B27.386": ("Carità", "Marcantonio", "allégorique", "Carità"),
    "B26.185": ("Tarpeia uccisa dai Sabini", "Marcantonio", "historique", "Tarpeia"),
    "B27.227": ("Venere e Vulcano", "Marco Dente", "mythologique", "Venere Vulcano putto amorino"),
    "B16.91": ("Diana e Atteone", "Maestro I.B.", "mythologique", "Diana Atteone"),
    "B27.405": ("Tre animali in un ovale", "Marco Dente", "autre", ""),
    "B26.28": ("Cristo porta la Croce", "Marcantonio", "religieux", "Cristo"),
    "B26.227": ("(rilievo antico)", "Marcantonio", "mythologique", ""),
    "B29.43": ("Sacrificio di Ifigenia", "Beatrizet", "mythologique", "Ifigenia Agamennone"),
    "B28.46": ("Ercole e l'Idra", "Caraglio", "mythologique", "Ercole Idra"),
    "B26.47": ("Madonna di Foligno", "Marcantonio", "religieux", "Maria Cristo"),
    "B27.32": ("Venere ferita da una spina", "Marco Dente", "mythologique", "Venere"),
}
ESTAMPES["MODI"] = ("I Modi (série, sans numéro Bartsch dans les fiches)", "Marcantonio", "érotique", "")
CORRECTIONS_NUMERO = {("26", "11726"): ("26", "117")}  # coquille manifeste dans une fiche

GRAVEURS = [("Marcantonio", r"Marcantonio|Raimondi"), ("Marco Dente", r"Marco Dente|Dente di Ravenna"),
            ("Agostino Veneziano", r"Agostino"), ("Caraglio", r"Caraglio"),
            ("Maestro I.B.", r"Maestro I\.?\s?B|Monogrammista I\.?\s?B"), ("Pencz", r"Pencz"),
            ("Bonasone", r"Bonasone"), ("Beatrizet", r"Beatrizet"), ("Mantegna", r"Mantegna"),
            ("Robetta", r"Robetta")]

MODI = re.compile(r"\b(?:I|i|dei|dai|de|da|serie de)\s+(?:celebri\s+|famosi\s+)?Modi\b|\bModi di Marcantonio")
CIT = re.compile(r"Bartsch\s*(\d+)\s*(?:,\s*p\.\s*(\d+))?\s*(?:,\s*n\.\s*(\d+))?")


def cle(vol, n):
    vol, n = CORRECTIONS_NUMERO.get((vol, n), (vol, n))
    return f"B{int(vol)}.{int(n)}" if n else f"B{int(vol)}.?"


def _proteger(s):
    return re.sub(r"\b(pp?|nn?|fig|figg|cfr|ca|vol|tav|inv|cat|ibid|op|cit|S|St)\.",
                  lambda m: m.group(1) + "§", s, flags=re.I)


def _clauses(comm):
    """Découpe le commentaire en propositions (; et : toujours ; . suivi d'une majuscule)."""
    p = _proteger(comm)
    out, pos = [], 0
    for m in re.finditer(r";|:(?=\s)|\.(?=\s+[A-ZÈÉÀ“\"(])", p):
        out.append((pos, m.end()))
        pos = m.end()
    out.append((pos, len(p)))
    return [(a, b) for a, b in out if b > a]


# --------------------------------------------------------------------------- chargement


def charger(avec_modi=False):
    """Renvoie (fiches, citations, votes). avec_modi : ajoute une pseudo-référence « MODI » pour chaque
    mention des Modi (jamais numérotés Bartsch dans les fiches). Les champs '_*' contiennent du texte privé : ne jamais les écrire."""
    pieces = {int(r["id"]): r for r in csv.DictReader(open(PIECES))}
    fiches, citations = [], []
    for e in json.load(open(JSON_FICHES)):
        t = texte(e["html"])
        ins = _section(t, r"Iscrizion[ei]")
        comm = re.sub(r"\s+", " ", t.split("Commento dell", 1)[-1])
        comm = re.sub(r"^’opera\s*:?\s*", "", comm)
        p = pieces.get(e["id"], {})
        f = {"id": e["id"], "titolo": html.unescape(e["title"]), "link": e["link"],
             "forma": p.get("forma", ""), "diametro_cm": p.get("diametro_cm", ""),
             "data_catalogue": p.get("data", ""), "_ins": ins, "_comm": comm}
        f.update(date_piece(p.get("data", ""), ins))
        f.update(attribution(f))
        if FILTRE is not None and not FILTRE(f):
            continue
        fiches.append(f)
        for a, b in _clauses(comm):
            seg = comm[a:b]
            ms = sorted(list(CIT.finditer(seg)) + list(MODI.finditer(seg)), key=lambda m: m.start())
            for i, m in enumerate(ms):
                gauche = seg[(ms[i - 1].end() if i else 0):m.start()]
                droite = seg[m.end():(ms[i + 1].start() if i + 1 < len(ms) else len(seg))]
                if m.re is MODI:
                    if not avec_modi:
                        continue
                    k = "MODI"
                else:
                    k = cle(m.group(1), m.group(3) or "")
                citations.append({"id": e["id"], "estampe": k, "_gauche": gauche, "_droite": droite,
                                  "_clause": seg, "graveur_phrase": graveur_dans(gauche)})
    # graveur par estampe : table ESTAMPES, sinon vote majoritaire des fiches
    votes = defaultdict(Counter)
    for c in citations:
        if c["graveur_phrase"]:
            votes[c["estampe"]][c["graveur_phrase"]] += 1
    for c in citations:
        info = ESTAMPES.get(c["estampe"])
        c["graveur"] = info[1] if info else (votes[c["estampe"]].most_common(1)[0][0]
                                             if votes[c["estampe"]] else "inconnu")
        c["titre_estampe"] = info[0] if info else ""
        c["type_estampe"] = info[2] if info else "inconnu"
    return fiches, citations, votes


Y_SLASH = re.compile(r"\by\s*/\s*[Øø0φΦ]|\by\b\s*[”\"]")


def attribution(f):
    """Indicateurs d'attribution débattue (Mallet donne au jeune Xanto le groupe de Gubbio de 1522-1527,
    Wilson le lui refuse ; les initiales F.R. et la marque y/Ø sont discutées de même)."""
    ins = f["_ins"]
    cite = " ".join(re.findall(r"[“\"]([^”\"]*)[”\"]?", ins)) or ins
    avant = f["annee"] is not None and f["annee"] < DEBUT_URBINO
    fr = bool(re.search(r"F\.\s?R\.", ins))
    ys = bool(Y_SLASH.search(cite))
    return {"avant_1528": avant, "initiales_FR": fr, "marque_y_slash": ys,
            "attribution_debattue": avant or fr,
            "attribution_debattue_large": avant or fr or ys}


def graveur_dans(s):
    best, pos = "", -1
    for nom, rx in GRAVEURS:
        for m in re.finditer(rx, s):
            if m.start() > pos:
                best, pos = nom, m.start()
    return best


def par_id(fiches):
    return {f["id"]: f for f in fiches}


def ecrire_csv(chemin, lignes, champs=None):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if not lignes:
        chemin.write_text("")
        return
    champs = champs or [k for k in lignes[0] if not k.startswith("_")]
    with open(chemin, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=champs, extrasaction="ignore")
        w.writeheader()
        for r in lignes:
            w.writerow({k: v for k, v in r.items() if not k.startswith("_")})


def ecrire_json(chemin, obj):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str))


def lien(f):
    return f["link"]


# --------------------------------------------------------------------------- tests par permutation


def permutation_par_piece(lignes, cle_groupe, est_positif, g1, g2, n=10000, graine=1):
    """Différence de proportion (g2 - g1) entre deux groupes de lignes, avec p bilatéral obtenu en
    permutant les groupes entre PIÈCES (les références d'une même pièce restent ensemble, car elles
    ne sont pas indépendantes). Sans scipy."""
    import random
    rnd = random.Random(graine)
    paquets = defaultdict(list)
    for r in lignes:
        if r[cle_groupe] in (g1, g2):
            paquets[r["id"]].append(r)
    ids = list(paquets)
    grp = [paquets[i][0][cle_groupe] for i in ids]
    pos = [sum(1 for r in paquets[i] if est_positif(r)) for i in ids]
    tot = [len(paquets[i]) for i in ids]

    def diff(g):
        a = [sum(p for p, x in zip(pos, g) if x == k) / max(1, sum(t for t, x in zip(tot, g) if x == k))
             for k in (g1, g2)]
        return a[1] - a[0]

    obs = diff(grp)
    extr = 0
    for _ in range(n):
        g = grp[:]
        rnd.shuffle(g)
        if abs(diff(g)) >= abs(obs) - 1e-12:
            extr += 1
    return {"groupe_1": g1, "groupe_2": g2, "difference_g2_moins_g1": round(obs, 4),
            "p_permutation_bilateral": round((extr + 1) / (n + 1), 4), "n_permutations": n,
            "n_pieces": len(ids)}
