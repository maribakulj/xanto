# Tests descriptifs sur le catalogue de Rovigo (Xanto Avelli, 374 fiches) — synthèse

**À lire d'abord.** Tous les chiffres ci-dessous viennent d'une **extraction automatique** (expressions régulières) des fiches du catalogue *Xanto nel mondo* (Fondazione Banca del Monte di Rovigo). Ils décrivent ce que **disent les fiches**, pas ce que montrent les objets. Chaque ligne des fichiers CSV porte le lien vers sa fiche, et chaque ligne est **à vérifier**. Aucun passage des commentaires n'est recopié ici : seulement des identifiants, des comptes et des liens. **Tous ces tests sont exploratoires** (voir « Tests multiples »).

- Données : 374 fiches. 576 références Bartsch dans 278 fiches, plus 40 mentions des *Modi* (jamais numérotées Bartsch, donc absentes de `data/emprunts.csv`). 54 estampes distinctes.
- Périodes : ≤ 1530 (101 pièces), 1531-1535 (164), 1536-1542 (101). 8 pièces n'ont pas de période (intervalle à cheval sur deux périodes).
- Tests statistiques : permutations **entre pièces** quand la variable est une propriété du plat (période) ; bootstrap en grappes ou permutation **entre estampes** quand c'est une propriété de l'estampe (graveur). Le hasard sert de point de comparaison.

Pour relancer les calculs : `python3 analyses/tout.py`. Il faut les sources privées dans `~/Documents/Codex/2026-10-08-continuation-claude/sources-libres/`.

## Corrections du 10/10/2026 (après la revue critique n° 1)

1. **Dates.** `scripts/rovigo_table.py` lisait le champ `data` par position : pour 38 fiches il contenait l'inscription, pour 25 il était vide. Il est maintenant repéré par sa forme (année, intervalle, « ca. »). 63 lignes de `data/pieces.csv` ont changé (`data` et, pour 50, `forma`) ; plus aucune pièce sans date (13 avant). La date de la pièce 194 (« 1522 », peinte sur une tablette dans la scène) n'est plus comptée comme date inscrite ; les 11 autres dates inscrites d'avant 1528 sont des dates de lustre de Gubbio.
2. **Briend.** Le test Caraglio contre Marcantonio donnait à chaque plat le graveur de sa première référence (78 plats citent les deux). Il est refait par référence (bootstrap en grappes) et par estampe.
3. **Inversion.** Le résultat principal porte sur les seules dates inscrites : la « tendance à la hausse » disparaît. La phrase attribuant à Hess un seuil de « 50 % attendus » est retirée.
4. **Modi × politique**, **Jestaz**, **rebaptême** : verdicts reformulés (voir le tableau).
5. **Sensibilité** : tests chronologiques refaits sans le groupe de Gubbio 1522-1527 (`t-sensibilite/`).
6. **Tests multiples** : liste de toutes les p, avec une correction de Holm indicative.

## Les thèses une à une

| Thèse | Test | Chiffre clé | Verdict |
|---|---|---|---|
| Hess 1999 (n. 44) : l'inversion ne prouve rien (un carton se ponce des deux côtés) | T-inversion | 63 références sur 576 (10,9 %) dites « in controparte », aucune négation | **Non testable ainsi.** Hess ne dit rien de la fréquence des inversions : un peintre qui ponce toujours du même côté donne 0 %, et Hess reste juste. Le chiffre ne soutient ni n'affaiblit Hess. |
| Rondot 1994, Gallian : inversion volontaire, pour varier | T-inversion | Dates inscrites seulement : 3/15 (20 %), 31/291 (11 %), 18/109 (17 %) ; p = 0,76 et 0,14 | **Indécis, pas de tendance.** La « légère hausse » annoncée avant (7 %, 10 %, 15 % avec toutes les dates) **disparaît** avec les dates inscrites : elle tenait à la période ≤ 1530, datée surtout par estimation. Le vrai test (orientation d'une même figure d'un plat à l'autre) reste à faire. |
| Liverani 1962 : réemploi = négligence, hâte | T-reuse | 3 estampes (*Parnaso* 76 pièces, *Contesa* 71, *San Lorenzo* 52) servent de 1528 à 1542 | **Non testable** (la hâte ne se lit pas dans les fiches). Le réemploi constant d'un petit noyau d'estampes s'accorde mieux avec une méthode qu'avec un accident. |
| Poole 1995 : « repetitiousness » ; Mallet : fin de carrière « répétitive » | T-reuse, T-sources | 6 estampes nouvelles après 1536, pour 4,3 attendues par hasard ; combinaisons déjà vues : 36 % contre 31 % (p = 0,19 ; p = 0,012 avec les dates inscrites) ; 1,93 estampe identifiée par pièce contre 2,47 (p = 0,002) | **Mitigé.** Le recul des estampes nouvelles est un **effet d'accumulation**, pas un signe de répétition. Répétition faible des mêmes assemblages (dates inscrites seulement). Moins d'estampes **identifiées** par plat à la fin (collages plus simples, ou catalogue moins attentif). Inchangé sans le groupe de Gubbio. |
| Mallet 2007 : méthode délibérée de couper-coller | T-whole, T-sources | 76 % des pièces ont une source identifiée ; 2,17 estampes par pièce ; composition entière dans 4,7 % des références seulement | **Soutenu** (description) : on emprunte surtout des figures et des groupes, venus de plusieurs estampes. |
| Jestaz 1976 : *fabula* / *historia* / *sporcitia* renverraient à des recueils de modèles classés par genre | T-revers | 61 mots de genre, presque tous de 1528-1531 ; le seul *sporcitia* (354) n'a aucune estampe connue ; 0 *sporcitia* sur 40 pièces aux *Modi* | **Non testable avec ces données (n = 1).** Un seul *sporcitia* ne peut rien réfuter (et son absence de source est ce que prédirait Jestaz). Le mot suit le **genre du récit** (*fabula* → Ovide 15/21 ; *nota* → actualité politique 6/13), mais en partie par construction (le genre vient du commentaire, qui lit l'inscription). Cela s'accorde avec Mallet (2007, p. 34) et Castelletti (le mot comme consigne de lecture). |
| Boutin Vitela 2014 : l'inscription réoriente la lecture ; contre elle, Wilson 1990, Lessmann : indifférence au sens d'origine | T-rebaptism | 88 % des figures nommées changent d'identité (98/111, Cupidon à part) ; cas explicites : 6 changées sur 7 ; 79 figures anonymes reçoivent un nom | **Ne départage pas.** Renommer est la règle, mais ce taux est prédit par les deux lectures opposées. C'est une condition commune, pas un soutien à l'une d'elles. La part présumée (94 sur 100) dépend de listes de figures faites à la main. |
| Briend 1992 : Caraglio copié en entier, Marcantonio découpé (échelle des figures) | T-whole | entière : Caraglio 7,0 %, Marcantonio 4,0 % (par référence, p = 0,27 ; par estampe, p = 0,11) ; entière ou groupe : 45,6 % contre 27,5 % (p = 0,001 en grappes de plats, mais 0,11 en grappes d'estampes, 0,17 par estampe, 0,47 sans la *Contesa*) | **Indécis.** Aucune différence détectable au niveau de l'estampe, l'unité de Briend. Trois estampes narratives de Caraglio sont copiées en entier (*Fuga di Enea*, *Alessandro e Rossana*, *Adorazione*) ; la différence « groupe » vient de la seule *Contesa*. L'explication par l'échelle des figures n'est pas testée. |
| Talvacchia 1994 : les emprunts aux *Modi*, messages codés érotiques ou politiques | T-revers, T-rebaptism | 7 des 40 pièces aux *Modi* ont un sujet politique, pour 2,7 attendues. Trois définitions essayées : p = 0,040 ; 0,007 ; 0,011 ; après Holm sur les trois : 0,040 ; 0,022 ; 0,022 ; stratifié par période : p = 0,010 | **Fragile.** Association descriptive sur 4 à 7 pièces, attendue en partie par la façon dont les *Modi* ont été identifiés (cherchés surtout sur les plats du Sac et de Pavie : circularité). Elle s'accorde aussi bien avec Mallet (poses athlétiques et raccourcis utiles aux scènes violentes). Ne départage pas Talvacchia et Mallet. Rien ne mesure ici le volet « codé érotique ». |

## Résultats par test

### T-dates (`t-dates/`)
243 dates sont inscrites sur la pièce, 61 viennent d'une année de la fiche (dont 25 « ca. »), 67 du milieu d'un intervalle, 2 d'un désaccord entre inscription et fiche, et 1 date peinte dans la scène n'est pas retenue comme date inscrite (194). Plus aucune pièce sans date (13 avant la correction). L'année la plus fournie est 1532 (56 pièces). **Attention** : avant 1531, les dates sont surtout des estimations du catalogue ; après, presque toutes sont inscrites. Les 26 pièces datées avant 1528 sont d'attribution débattue (groupe de Gubbio) : leurs dates lues sur la pièce sont des dates de lustre de Gubbio (11) ou une date figurée (194).

### T-inversion (`t-inversion/`)
10,9 % des références sont dites inversées (53 fiches sur 278). Par graveur : Marcantonio 11 %, Caraglio 12 %, Marco Dente 8 %, Agostino 19 %, Maître I.B. 0 %. Par période, dates inscrites seulement (résultat principal) : 20 % (3/15), 11 % (31/291), 17 % (18/109), sans tendance. Avec toutes les dates (pour mémoire) : 7,6 % (8/105), 10,0 % (33/331), 15,6 % (20/128), p = 0,10. Aucune négation trouvée. *Modi* : 2 sur 40.

### T-reuse (`t-reemploi/`)
54 estampes, dont 15 n'apparaissent qu'une fois. Estampes nouvelles par période : 30, puis 18, puis 6. La concentration est stable (les 5 estampes principales font 46 %, 49 %, 44 % des références). Les pièces tardives n'introduisent pas moins de nouveautés que le hasard ; la part de leurs références qui va à des estampes nouvelles est même plus forte (7,9 % contre 3,1 % attendus, p = 0,006 ; p = 0,06 avec les dates inscrites). Les combinaisons exactes déjà vues sont un peu plus fréquentes à la fin (14 pièces sur 39). La plus répétée, *Parnaso* + *Contesa*, revient sur 8 pièces de 1529 à 1538. Le *Quos Ego* « de 1522 » vient de la pièce 194 (date peinte dans la scène) : sans le groupe de Gubbio, sa première année est 1528.

### T-revers (`t-revers/`)
61 pièces portent un mot de genre : *historia* 24, *fabula* 21, *nota* 13, *sporcitia* 1, deux mots 2. Ces mots datent de 1528-1531 et n'apparaissent jamais avec une source nommée au revers (Ovide 32, Virgile 9, Justin 5, toutes sur d'autres pièces). Le mot ne suit pas le type des estampes employées (mais ce type, classé d'après le sujet de l'estampe, n'est pas le bon indicateur pour Jestaz). Il suit le genre du récit, en partie par construction.

### T-rebaptism (`t-rebapteme/`)
Sur 616 références (*Modi* compris), 225 ont une cible nommée. Parmi elles : 46 conservations (dont 36 Cupidons), 100 changements d'identité et 79 figures anonymes devenues nommées. Cas explicites : 7 (6 changements, 1 conservation). La part des changements varie peu dans le temps (64 %, 68 %, 78 %). Les 23 cibles nommées tirées de la *Contesa* changent toutes d'identité.

### T-whole (`t-entier/`)
22 compositions entières sur 472 références classées (4,7 %), 119 groupes, 324 figures isolées, 7 parties de figure. Test Caraglio contre Marcantonio corrigé : voir le tableau de `t-entier/README.md` (par référence avec bootstrap en grappes de plats ou d'estampes ; par estampe avec permutation entre estampes).

### T-sources-per-plate (`t-sources-par-piece/`)
Estampes identifiées par pièce (si source) : 1,76, puis 2,47, puis 1,93. Part des pièces avec une source : 62 %, 88 %, 68 %. Le collage culmine en 1532-1533. Maximum : 8 estampes (pièce 399).

### T-sensibilité (`t-sensibilite/`)
Les tests chronologiques (dates, inversion, réemploi, estampes par pièce) sont refaits sans les 26 pièces d'attribution débattue (datées avant 1528 ou aux initiales F.R.), puis sans les 70 pièces qui comprennent aussi la marque y/Ø. **Aucune conclusion ne change.** Seul effet notable : la série d'inversion « toutes dates » passe à p = 0,04 sans le groupe de Gubbio ; elle repose sur des dates estimées, n'est pas corrigée pour les tests multiples, et la série par dates inscrites reste sans tendance (p = 0,59).

## Tests multiples

Toutes les p rapportées ci-dessus (analyse complète). Elles sont calculées sur les mêmes 374 fiches et ne sont pas indépendantes. **Aucune correction pour comparaisons multiples n'est appliquée dans les verdicts, sauf la correction de Holm sur les trois définitions de « politique » (T-revers).** La dernière colonne applique Holm à toute la liste, à titre indicatif. Données : `resultats.json` → `p_valeurs`.

| Test | Comparaison | p | Holm (toute la liste) |
|---|---|---|---|
| T-inversion | ≤ 1530 vs 1536-1542, toutes dates | 0,10 | 1 |
| T-inversion | 1531-1535 vs 1536-1542, toutes dates | 0,10 | 1 |
| T-inversion | ≤ 1530 vs 1536-1542, dates inscrites (principal) | 0,76 | 1 |
| T-inversion | 1531-1535 vs 1536-1542, dates inscrites (principal) | 0,14 | 1 |
| T-reuse | estampes introduites dès 1536, moins que le hasard ? (toutes ; inscrites) | 0,89 ; 0,44 | 1 ; 1 |
| T-reuse | part tardive vers estampes nouvelles (toutes ; inscrites) | 0,006 ; 0,06 | 0,12 ; 0,84 |
| T-reuse | combinaisons déjà vues (toutes ; inscrites) | 0,19 ; 0,012 | 1 ; 0,18 |
| T-sources | estampes par pièce, 1531-1535 vs 1536-1542 | 0,002 | 0,03 |
| T-whole | entière, par référence (grappes = plats ; = estampes) | 0,27 ; 0,60 | 1 ; 1 |
| T-whole | entière ou groupe, par référence (grappes = plats ; = estampes) | 0,001 ; 0,11 | 0,03 ; 1 |
| T-whole | entière ; entière ou groupe, par estampe (≥ 3 réf.) | 0,11 ; 0,17 | 1 ; 1 |
| T-revers | *Modi* × politique : *nota* ; commentaire ; l'un ou l'autre | 0,040 ; 0,007 ; 0,011 | 0,55 ; 0,13 ; 0,17 |
| T-revers | *Modi* × politique, stratifié par période | 0,010 | 0,17 |

Seules deux p restent sous 0,05 après correction sur toute la liste : la baisse du nombre d'estampes identifiées par plat après 1535 (à lire avec la réserve sur les silences du catalogue) et la différence « entière ou groupe » de Briend quand les plats sont les grappes (qui disparaît quand l'estampe est l'unité). Tous ces résultats sont **exploratoires** : ils indiquent où regarder, ils ne confirment aucune thèse.

## Limites communes

1. **Ce sont les phrases d'un seul rédacteur** (C.G.), avec ses formules et ses silences. Un silence (pas d'inversion notée, pas de source) n'est pas une observation.
2. **Chronologie inégale** (voir T-dates) : la période ≤ 1530 repose surtout sur des estimations, et contient le groupe de Gubbio d'attribution débattue (voir T-sensibilité).
3. **Classements approximatifs** : les classes de T-rebaptism et T-whole dépendent de règles simples sur des phrases italiennes. Entre 104 et 185 références restent non classées selon le test.
4. **Tables faites à la main** dans `commun.py` : graveur, type de sujet et figures de chaque estampe. Elles sont à relire.
5. Le catalogue de Rovigo n'est pas toute l'œuvre de Xanto, et quelques fiches font peut-être doublon (par exemple 254 et 278).
6. **Tests multiples** : voir la section ci-dessus. Les p sont des repères exploratoires.

## Fichiers

- `commun.py` : lecture des fiches, dates (avec les indicateurs de date de lustre, de date peinte dans la scène et d'attribution débattue), découpage des propositions, table des estampes, tests par permutation, bootstrap en grappes, permutation entre estampes, correction de Holm.
- `t_dates.py`, `t_inversion.py`, `t_reemploi.py`, `t_revers.py`, `t_rebapteme.py`, `t_entier.py`, `t_sources_par_piece.py`, `t_sensibilite.py` : un script par test. Chacun écrit dans son dossier des CSV et un `resultats.json` ; chaque dossier a son `README.md`.
- `tout.py` : lance tout et écrit `resultats.json`, qui rassemble les résultats pour une démo de visualisation. On y trouve, par test : les comptes par année, le réemploi de chaque estampe (liste des pièces avec id et année), les taux d'inversion, les tableaux de contingence et les exemples avec leurs liens ; plus `t_sensibilite` et `p_valeurs`. Les clés existantes sont conservées ; les clés `test_caraglio_vs_marcantonio` et `test_groupe_ou_entier_caraglio_vs_marcantonio` contiennent désormais le test corrigé (par référence, bootstrap en grappes de plats ; champ `p_bootstrap_bilateral` au lieu de `p_permutation_bilateral`).
