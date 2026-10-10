# Tests descriptifs sur le catalogue de Rovigo (Xanto Avelli, 374 fiches) — synthèse

**À lire d'abord.** Tous les chiffres ci-dessous viennent d'une **extraction automatique** (expressions régulières) des fiches du catalogue *Xanto nel mondo* (Fondazione Banca del Monte di Rovigo). Ils décrivent ce que **disent les fiches**, pas ce que montrent les objets. Chaque ligne des fichiers CSV porte le lien vers sa fiche, et chaque ligne est **à vérifier**. Aucun passage des commentaires n'est recopié ici : seulement des identifiants, des comptes et des liens.

- Données : 374 fiches. 576 références Bartsch dans 278 fiches, plus 40 mentions des *Modi* (jamais numérotées Bartsch, donc absentes de `data/emprunts.csv`). 54 estampes distinctes.
- Périodes : ≤ 1530 (93 pièces), 1531-1535 (161), 1536-1542 (100). 20 pièces n'ont pas de période.
- Tests statistiques : permutations faites **entre pièces**, parce que les références d'une même fiche ne sont pas indépendantes. Le hasard sert de point de comparaison.

Pour relancer les calculs : `python3 analyses/tout.py`. Il faut les sources privées dans `~/Documents/Codex/2026-10-08-continuation-claude/sources-libres/`.

## Les thèses une à une

| Thèse | Test | Chiffre clé | Verdict |
|---|---|---|---|
| Hess 1999 : le sens de la figure n'a pas d'importance (carton posé d'un côté ou de l'autre) | T-inversion | 63 références sur 576 (10,9 %) dites « in controparte », aucune négation | **Indécis.** Un carton posé au hasard donnerait environ 50 % d'inversions. Les fiches n'en notent que 11 %, mais une fiche muette ne prouve pas que la figure garde son sens. |
| Rondot 1994, Gallian : inversion volontaire, pour varier | T-inversion | 7 % (≤ 1530), puis 10 %, puis 15 % (1536-1542). p = 0,14 | **Indécis**, légère tendance à la hausse. De 0 % (*Davide e Golia*) à 33 % (*Santa Cecilia*, *Cristo da Simone*) selon l'estampe. |
| Liverani 1962 : réemploi = négligence, hâte | T-reuse | 3 estampes (*Parnaso* 76 pièces, *Contesa* 71, *San Lorenzo* 52) servent de 1528 à 1542 | **Non testable** (la hâte ne se lit pas dans les fiches). Le réemploi constant d'un petit noyau d'estampes s'accorde mieux avec une méthode qu'avec un accident. |
| Poole 1995 : « repetitiousness » ; Mallet : fin de carrière « répétitive » | T-reuse, T-sources | 6 estampes nouvelles après 1536, pour 4,3 attendues par hasard ; combinaisons déjà vues : 37 % contre 30 % (p = 0,10 ; p = 0,02 avec les dates inscrites) ; 1,93 estampe par pièce contre 2,46 (p = 0,003) | **Mitigé.** Le recul des estampes nouvelles est un **effet d'accumulation**, pas un signe de répétition. On ne trouve qu'une répétition faible des mêmes assemblages. Les collages tardifs sont **plus simples**. |
| Mallet 2007 : méthode délibérée de couper-coller | T-whole, T-sources | 76 % des pièces ont une source identifiée ; 2,17 estampes par pièce ; composition entière dans 4,7 % des références seulement | **Soutenu** (description) : on emprunte surtout des figures et des groupes, venus de plusieurs estampes. |
| Jestaz 1976 : *fabula* / *historia* / *sporcitia* renverraient à des recueils de modèles classés par genre | T-revers | 61 mots de genre, presque tous de 1528-1531 ; 12 pièces *fabula* sur 20 empruntent à une estampe religieuse ; le seul *sporcitia* (354) n'a aucune estampe connue ; 0 *sporcitia* sur 40 pièces aux *Modi* | **Affaibli.** Le mot suit le **genre du récit** (*fabula* → Ovide 15/21 ; *nota* → actualité politique 6/13), pas le type des estampes. Il disparaît quand apparaît la référence « Nel … libro d'Ovidio » (jamais les deux sur la même pièce). |
| Boutin Vitela 2014 : l'inscription réoriente la lecture d'une image empruntée | T-rebaptism | 88 % des figures nommées changent d'identité (98/111, Cupidon à part) ; 79 figures anonymes reçoivent un nom ; 46 conservations sur 225, dont 36 putti devenus Cupidon | **Soutenu comme condition** : renommer est la règle (Muse → Circé, 644 ; Didon → Omphale, 194). La « réorientation de la lecture » elle-même n'est pas mesurable ainsi. |
| Briend 1992 : Caraglio copié en entier, Marcantonio découpé (échelle des figures) | T-whole | entière : Caraglio 7 %, Marcantonio 4 % (p = 0,22) ; entière ou groupe : 46 % contre 28 % (p = 0,06) ; Caraglio sans la *Contesa* : 15 % entière | **Indécis, avec nuance.** Certaines estampes narratives de Caraglio sont copiées en entier (*Fuga di Enea*, *Alessandro e Rossana*, *Adorazione*). Sa *Contesa* (71 références) est découpée comme un Marcantonio. |
| Talvacchia 1994 : les emprunts aux *Modi*, messages codés érotiques ou politiques | T-revers, T-rebaptism | 40 pièces aux *Modi*, toujours des figures isolées ou des groupes, renommées (Alcyone, Hespérie, Rome, Tarpéia…) ; 7 sur 40 ont un sujet politique (*nota* ou actualité selon le commentaire), pour 2,7 attendues (p = 0,011) | **Plutôt soutenu pour le volet politique**, sur un petit effectif (7 pièces : 973, 145, 1328, 428, 414, 889, 1122). Rien ne mesure ici le volet « codé érotique ». |

## Résultats par test

### T-dates (`t-dates/`)
244 dates sont inscrites sur la pièce, 53 viennent d'une année de la fiche (dont 25 « ca. »), 62 du milieu d'un intervalle, 2 d'un désaccord entre inscription et fiche, et 13 pièces n'ont pas de date. L'année la plus fournie est 1532 (54 pièces). **Attention** : avant 1531, les dates sont surtout des estimations du catalogue ; après, presque toutes sont inscrites. Les comparaisons entre périodes mélangent donc l'époque et la qualité de la date.

### T-inversion (`t-inversion/`)
10,9 % des références sont dites inversées (53 fiches sur 278). Par graveur : Marcantonio 11 %, Caraglio 12 %, Marco Dente 8 %, Agostino 19 %, Maître I.B. 0 %. Par période : 7 %, 10 %, 15 % (non significatif). Aucune négation trouvée. *Modi* : 2 sur 40.

### T-reuse (`t-reemploi/`)
54 estampes, dont 15 n'apparaissent qu'une fois. Estampes nouvelles par période : 29, puis 18, puis 6. La concentration est stable (les 5 estampes principales font 44 %, 49 %, 44 % des références). Les pièces tardives n'introduisent pas moins de nouveautés que le hasard ; la part de leurs références qui va à des estampes nouvelles est même plus forte (8 % contre 3 % attendus, p = 0,007). Les combinaisons exactes déjà vues sont un peu plus fréquentes à la fin (14 pièces sur 38). La plus répétée, *Parnaso* + *Contesa*, revient sur 8 pièces de 1529 à 1538.

### T-revers (`t-revers/`)
61 pièces portent un mot de genre : *historia* 24, *fabula* 21, *nota* 13, *sporcitia* 1, deux mots 2. Ces mots datent de 1528-1531 et n'apparaissent jamais avec une source nommée au revers (Ovide 32, Virgile 9, Justin 5, toutes sur d'autres pièces). Le mot ne suit pas le type des estampes employées. Il suit le genre du récit.

### T-rebaptism (`t-rebapteme/`)
Sur 616 références (*Modi* compris), 225 ont une cible nommée. Parmi elles : 46 conservations (dont 36 Cupidons), 100 changements d'identité et 79 figures anonymes devenues nommées. La part des changements est stable dans le temps (70 %, 67 %, 78 %). Les 23 cibles nommées tirées de la *Contesa* changent toutes d'identité.

### T-whole (`t-entier/`)
22 compositions entières sur 472 références classées (4,7 %), 119 groupes, 324 figures isolées, 7 parties de figure. Caraglio est un peu plus souvent repris par groupes (*Contesa*), et en entier pour trois estampes narratives.

### T-sources-per-plate (`t-sources-par-piece/`)
Estampes par pièce (si source) : 1,74, puis 2,46, puis 1,93. Part des pièces avec une source : 61 %, 89 %, 68 %. Le collage culmine en 1532-1533 (2,6 et 2,9 estampes par pièce). Maximum : 8 estampes (pièce 399).

## Limites communes

1. **Ce sont les phrases d'un seul rédacteur** (C.G.), avec ses formules et ses silences. Un silence (pas d'inversion notée, pas de source) n'est pas une observation.
2. **Chronologie inégale** (voir T-dates) : la période ≤ 1530 repose surtout sur des estimations.
3. **Classements approximatifs** : les classes de T-rebaptism et T-whole dépendent de règles simples sur des phrases italiennes. Entre 104 et 185 références restent non classées selon le test.
4. **Tables faites à la main** dans `commun.py` : graveur, type de sujet et figures de chaque estampe. Elles sont à relire.
5. Le catalogue de Rovigo n'est pas toute l'œuvre de Xanto, et quelques fiches font peut-être doublon (par exemple 254 et 278).
6. Les p-valeurs servent de repères. Plusieurs tests sont faits sur les mêmes données, sans correction pour comparaisons multiples.

## Fichiers

- `commun.py` : lecture des fiches, dates, découpage des propositions, table des estampes, test par permutation.
- `t_dates.py`, `t_inversion.py`, `t_reemploi.py`, `t_revers.py`, `t_rebapteme.py`, `t_entier.py`, `t_sources_par_piece.py` : un script par test. Chacun écrit dans son dossier un `README.md`, des CSV et un `resultats.json`.
- `tout.py` : lance tout et écrit `resultats.json`, qui rassemble les résultats pour une démo de visualisation. On y trouve, par test : les comptes par année, le réemploi de chaque estampe (liste des pièces avec id et année), les taux d'inversion, les tableaux de contingence et les exemples avec leurs liens.
