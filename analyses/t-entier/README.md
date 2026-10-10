# T-whole (E1, Briend) — estampe copiée en entier ou découpée ?

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches.**

## Thèse discutée

Briend 1992 : les estampes de Caraglio seraient copiées en entier, celles de Marcantonio découpées en motifs, à cause de l'échelle des figures.

## Méthode (`../t_entier.py`)

On lit ce qui précède chaque référence dans la fiche. On décide dans cet ordre :

1. **composition entière** : « l'intera composizione », « l'intera scena », « la scena è tratta / ripresa », « la composizione è derivata », « interamente », « citazione letterale » dite de la composition ;
2. **partie de figure** : « le gambe », « la parte superiore », « il resto del corpo »… ;
3. **groupe** : sujet au pluriel avant le verbe (« il gruppo », « la coppia », « le due figure », « sono riprese ») ;
4. **figure isolée** : sujet au singulier ;
5. **non classé** : simple liste de sources.

Seul le sujet placé avant le verbe est lu. Sans cette précaution, le titre « Contesa tra le Muse » faisait classer « groupe » toute figure tirée de cette estampe. Une seconde mesure regroupe « composition entière » et « groupe ».

**Test Caraglio contre Marcantonio (corrigé le 10/10/2026).** L'ancienne version permutait les graveurs entre pièces en donnant à chaque pièce le graveur de sa *première* référence. C'était faux : 78 des 278 pièces citent à la fois Caraglio et Marcantonio (60 parmi les références classées), et le graveur est une propriété de l'estampe, pas du plat. Le test est maintenant fait de deux façons :

1. **Par référence**, chaque référence gardant le graveur de *son* estampe. L'incertitude vient d'un bootstrap en grappes : on tire des pièces avec remise (10 000 tirages), les références d'une même pièce restant ensemble. On refait le même bootstrap en tirant des **estampes** comme grappes, car la dépendance principale est par estampe (la *Contesa* fournit 62 des 114 références classées de Caraglio).
2. **Par estampe**, l'unité de la thèse de Briend : part « entière » de chaque estampe, moyenne par graveur, et permutation des étiquettes de graveur **entre estampes**. Toutes les estampes (22 Marcantonio, 9 Caraglio), puis celles qui ont au moins 3 références classées (14 et 9).

## Résultats

| Graveur | Références | Entière | Groupe | Figure | Partie | Non classé | Part entière* | Part entière ou groupe* |
|---|---|---|---|---|---|---|---|---|
| Marcantonio | 303 | 10 | 58 | 172 | 7 | 56 | 4,0 % | 27,5 % |
| Caraglio | 132 | 8 | 44 | 62 | 0 | 18 | 7,0 % | 45,6 % |
| Marco Dente | 90 | 2 | 15 | 60 | 0 | 13 | 2,6 % | 22,1 % |
| Agostino Veneziano | 32 | 2 | 1 | 21 | 0 | 8 | 8,3 % | 12,5 % |
| *Modi* (Marcantonio, sans numéro) | 40 | 0 | 8 | 23 | 0 | 9 | 0 % | 25,8 % |

\* parmi les références classées.

- Sur l'ensemble, la composition entière est **rare** : 22 références sur 472 classées (4,7 %). Liste des pièces : 112, 116, 339, 446, 461, 489, 590, 756, 760, 820, 827, 925, 939, 950, 1000, 1101, 1129, 1131, 1152, 1257, 1263, 1344.
- Caraglio contre Marcantonio (`resultats.json` → `test_*`) :

| Mesure | Unité, grappes | Marcantonio | Caraglio | Différence | IC 95 % | p |
|---|---|---|---|---|---|---|
| entière | référence, grappes = pièces | 10/247 (4,0 %) | 8/114 (7,0 %) | +3,0 pts | −2,2 à +8,6 | 0,27 |
| entière | référence, grappes = estampes | idem | idem | +3,0 pts | −5,0 à +23,7 | 0,60 |
| entière | estampe (≥ 3 réf.), moyenne non pondérée | 3,0 % (14 estampes) | 14,4 % (9) | +11,4 pts | – | 0,11 |
| entière | estampe (toutes) | 15,5 % (22) | 14,4 % (9) | −1,2 pt | – | 0,96 |
| entière ou groupe | référence, grappes = pièces | 68/247 (27,5 %) | 52/114 (45,6 %) | +18,1 pts | +7,2 à +28,7 | 0,001 |
| entière ou groupe | référence, grappes = estampes | idem | idem | +18,1 pts | −8,0 à +31,7 | 0,11 |
| entière ou groupe | référence, sans la *Contesa* | 27,5 % | 17/52 (32,7 %) | +5,2 pts | −8,6 à +19,4 | 0,47 |
| entière ou groupe | estampe (≥ 3 réf.) | 20,7 % (14) | 34,5 % (9) | +13,9 pts | – | 0,17 |

  Avant correction, on affichait +3,1 points (p = 0,22) et +10 points (p = 0,06). La différence « entière » n'est significative à aucun niveau. La différence « entière ou groupe » ne l'est que si l'on traite les références comme indépendantes d'une estampe à l'autre. Elle vient presque toute de la *Contesa* (35 groupes sur 62) : sans elle, ou quand l'estampe est l'unité, elle n'est plus significative.
- Caraglio **sans la *Contesa*** (B28.53) : 8 compositions entières sur 52 références classées (15 %). Ce sont la *Fuga di Enea* (461, 827, 1257), les *Nozze di Alessandro e Rossana* (489, 760, 939) et l'*Adorazione dei pastori* (1101, 1263). La *Contesa*, estampe de Caraglio la plus employée (71 références), n'est jamais copiée en entier : on en tire des figures et des groupes.

Données du graphique : `entier_par_graveur.csv` (barres empilées par graveur), `resultats.json` → `par_estampe`.

## Ce que cela dit de la thèse

**Pas de conclusion nette, avec des nuances.** Au niveau de l'estampe, l'unité dont parle Briend, on ne voit **pas de différence détectable** entre les deux graveurs : 9 estampes de Caraglio, c'est peu. Ce n'est pas Caraglio en général qui est copié en entier, mais trois estampes narratives (*Enea*, *Alessandro e Rossana*, *Adorazione*). Son estampe la plus utilisée, la *Contesa*, fournit surtout des groupes de Muses. C'est elle qui fait la différence « entière ou groupe » au niveau des références. L'explication de Briend par **l'échelle des figures n'est pas testée ici** : il faudrait mesurer la hauteur des figures dans chaque estampe (rapport, Test 9).

## Limites

- Le classement dépend des formules du rédacteur. « La scena è tratta da… » peut désigner une adaptation libre.
- 104 références sont des listes de sources sans verbe, donc non classées.
- L'échelle des figures n'est pas mesurée ici. Le dossier `../../tests-echelle` contient un premier test sur image.

## Fichiers

`entier_par_reference.csv`, `entier_par_graveur.csv`, `resultats.json`.
