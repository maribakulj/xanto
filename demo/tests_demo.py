#!/usr/bin/env python3
"""Met en forme analyses/resultats.json pour la démo (onglet « Autres tests ») : demo/data/tests_demo.json.
Les verdicts reprennent analyses/RESULTATS.md ; les graphiques sont tirés des résultats chiffrés."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "analyses/resultats.json"))
pct = lambda x: round(100 * x, 1)
PER = ["<=1530", "1531-1535", "1536-1542"]


def barres(titre, labels, valeurs):
    return {"titre": titre, "labels": labels, "valeurs": valeurs}


def table(titre, colonnes, lignes):
    return {"titre": titre, "colonnes": colonnes, "lignes": lignes}


tests = []
inv = R["t_inversion"]
tests.append({
    "titre": "Inversion des figures : indice ou choix ?",
    "these": "Hess 1999 (n. 44) : le sens de la figure n'a pas d'importance, un carton se ponce des deux côtés. Rondot 1994 et Gallian : Xanto inverse exprès pour varier.",
    "resultat": f"{inv['global']['n_inversees']} références sur {inv['global']['n_references']} ({pct(inv['global']['part'])} %) sont dites « in controparte » par les fiches. Un carton posé au hasard donnerait environ 50 %. La part monte de 7 % à 15 % entre les premières et les dernières années (différence non significative).",
    "verdict": "Indécis",
    "graphiques": [
        barres("Part des références inversées par période (%)", PER, [pct(inv["par_periode"][p]["part"]) for p in PER]),
        barres("Part des références inversées par graveur (%)", [g for g in inv["par_graveur"] if inv["par_graveur"][g]["n_references"] >= 20],
               [pct(v["part"]) for g, v in inv["par_graveur"].items() if v["n_references"] >= 20]),
    ],
    "limites": "Une fiche muette ne prouve pas que la figure garde son sens : seules les inversions signalées sont comptées. Vérification sur les images à faire.",
})
re = R["t_reemploi"]
vt = re["variante_toutes"]["par_periode"]
tests.append({
    "titre": "Réemploi : négligence, répétition ou méthode ?",
    "these": "Liverani 1962 : le réemploi trahit la hâte. Poole 1995 et Mallet 2007 : une fin de carrière répétitive. Mallet 2007 : une méthode délibérée de couper-coller.",
    "resultat": "Trois estampes (le Parnasse, le Concours des Muses, le Martyre de saint Laurent) servent pendant toute la carrière, de 1528 à 1542. Les estampes nouvelles se raréfient après 1536, mais pas plus que le hasard ne le prévoit : c'est un effet d'accumulation. Les plats tardifs sont plus simples (moins d'estampes par plat) et répètent un peu plus souvent les mêmes assemblages.",
    "verdict": "Mitigé : pas de répétitivité tardive au sens fort ; collages plus simples",
    "graphiques": [
        barres("Estampes utilisées pour la première fois, par période", PER, [vt[p]["estampes_nouvelles"] for p in PER]),
        table("Estampes les plus réemployées (nombre de plats, première et dernière année)", ["Estampe", "Graveur", "Plats", "De", "À"],
              [[e["titre"], e["graveur"], e["n_pieces"], e["premiere_annee"], e["derniere_annee"]] for e in re["par_estampe"][:15]]),
    ],
    "limites": "La hâte ne se lit pas dans les fiches. Les dates d'avant 1531 sont surtout des estimations, celles d'après surtout inscrites.",
})
sp = R["t_sources_par_piece"]
tests.append({
    "titre": "Combien d'estampes par plat ?",
    "these": "Mallet 2007 : le collage de figures prises à plusieurs estampes est la méthode de Xanto.",
    "resultat": f"{pct(sp['global_avec_modi']['part_avec_source'])} % des plats ont au moins une source identifiée ; en moyenne {sp['global_avec_modi']['moyenne_si_source']} estampes par plat (au plus {sp['global_avec_modi']['max']}).",
    "verdict": "Soutenu (description)",
    "graphiques": [barres("Nombre moyen d'estampes par plat (plats à source identifiée), par année",
                          [a["annee"] for a in sp["par_annee"] if a["pieces_avec_source"] >= 3],
                          [a["moyenne_si_source"] for a in sp["par_annee"] if a["pieces_avec_source"] >= 3])],
    "limites": "Une source non identifiée par le catalogue n'est pas une absence de source.",
})
ent = R["t_entier"]
gr = [g for g in ["Marcantonio", "Caraglio", "Marco Dente", "Agostino Veneziano"] if g in ent["par_graveur"]]
tests.append({
    "titre": "Copie entière ou découpée ?",
    "these": "Briend 1992 : Caraglio est copié en entier, Marcantonio découpé en motifs, à cause de l'échelle des figures.",
    "resultat": "Copier une composition entière est rare (moins de 5 % des références classées). Certaines estampes narratives de Caraglio sont reprises en entier (Énée et Anchise, Alexandre et Roxane), mais son Concours des Muses est découpé comme un Marcantonio.",
    "verdict": "Indécis, avec nuance",
    "graphiques": [table("Type d'emprunt par graveur (nombre de références)", ["Graveur", "Composition entière", "Groupe", "Figure isolée", "Non classé"],
                         [[g, ent["par_graveur"][g]["composition entière"], ent["par_graveur"][g]["groupe"], ent["par_graveur"][g]["figure isolée"], ent["par_graveur"][g]["non classé"]] for g in gr])],
    "limites": "Classement par règles simples sur les phrases du catalogue ; une partie des références reste non classée.",
})
rb = R["t_rebapteme"]
cl = rb["classes"]
tests.append({
    "titre": "La figure empruntée change-t-elle d'identité ?",
    "these": "Boutin Vitela 2014 : l'inscription au revers réoriente la lecture de l'image empruntée. Wilson 1990, Holcroft 1988, Lessmann 1990 : indifférence au sens d'origine.",
    "resultat": f"Hors Cupidon, la figure change d'identité dans {rb['sans_cupido']['changees']} cas sur {rb['sans_cupido']['n']} ({pct(rb['sans_cupido']['part_changees'])} %) : une Muse devient Circé, Didon devient Omphale. Renommer est la règle.",
    "verdict": "Soutenu comme condition préalable",
    "graphiques": [barres("Identité de la figure empruntée (références à cible nommée)", ["changée", "anonyme → nommée", "conservée"],
                          [cl["changée (présumée)"] + cl["changée (explicite)"], cl["anonyme → nommée (présumée)"], cl["conservée (présumée)"] + cl["conservée (explicite)"]])],
    "limites": "La « réorientation de la lecture » elle-même n'est pas mesurable ainsi ; les 36 conservations sont surtout des putti devenus Cupidon.",
})
rv = R["t_revers"]
g = rv["genres_comptes"]
tests.append({
    "titre": "Les mots du revers : recueils de modèles ou genres du récit ?",
    "these": "Jestaz 1976 : fabula, historia, sporcitia renverraient à des recueils de modèles classés par genre. Talvacchia 1994 : les emprunts aux Modi comme messages codés.",
    "resultat": "Les mots de genre (61 plats, presque tous de 1528-1531) suivent le genre du récit (fabula pour Ovide, nota pour l'actualité politique), pas le type d'estampe utilisée. Le seul plat « sporcitia » n'a aucune estampe connue, et aucun des 40 plats aux Modi ne porte ce mot. En revanche, les figures des Modi apparaissent plus souvent que par hasard sur des sujets politiques (7 plats pour 2,7 attendus).",
    "verdict": "Jestaz affaibli ; Talvacchia (volet politique) plutôt soutenu, sur un petit effectif",
    "graphiques": [
        barres("Mots de genre au revers (nombre de plats)", ["historia", "fabula", "nota", "sporcitia", "plusieurs"], [g["historia"], g["fabula"], g["nota"], g["sporcitia"], g["plusieurs"]]),
        table("Mot de genre et source littéraire (d'après les fiches)", ["Mot", "Plats", "Ovide", "Virgile", "Pétrarque", "Actualité politique"],
              [[x["genre"], x["pieces"], x.get("Ovidio", 0), x.get("Virgilio", 0), x.get("Petrarca", 0), x.get("attualità/allegoria politica", 0)] for x in rv["contingence_genre_x_source_selon_commentaire"]]),
    ],
    "limites": "Petits effectifs ; mots relevés par expressions régulières dans les transcriptions des inscriptions.",
})
dt = R["t_dates"]
tests.insert(0, {
    "titre": "D'où viennent les dates ?",
    "these": "Préalable à tous les tests chronologiques.",
    "resultat": "244 plats ont une année inscrite, 115 sont datés par le catalogue (dont 62 au milieu d'un intervalle), 13 n'ont pas de date. Avant 1531 les dates sont surtout des estimations, après surtout inscrites : comparer les périodes, c'est aussi comparer la qualité des dates.",
    "verdict": "Précaution",
    "graphiques": [barres("Plats par année (toutes dates)", [a["annee"] for a in dt["par_annee"]], [a["toutes"] for a in dt["par_annee"]]),
                   barres("Plats par année (dates inscrites seulement)", [a["annee"] for a in dt["par_annee"]], [a["inscrites"] for a in dt["par_annee"]])],
    "limites": "Les dates de lustre de Gubbio et les désaccords entre inscription et catalogue sont signalés à part.",
})
out = ROOT / "demo/data/tests_demo.json"
json.dump({"source": R["meta"]["source"], "statut": R["meta"]["statut"], "tests": tests}, open(out, "w"), ensure_ascii=False, indent=1)
print(f"{len(tests)} tests écrits dans {out.relative_to(ROOT)}")
