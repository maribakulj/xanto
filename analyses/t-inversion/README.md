# T-inversion (B1) — figures reprises « in controparte »

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. Chaque ligne est à vérifier sur la fiche (colonne `link`).**

## Thèses discutées

- Hess 1999 (n° 44) : le sens de la figure n'a pas d'importance. Le carton troué pour le poncif peut être posé d'un côté ou de l'autre.
- Rondot 1994, Gallian (essais du site de Rovigo) : Xanto inverse volontairement les figures (« in controparte ») pour varier.

## Méthode (`../t_inversion.py`)

- Unité : une référence Bartsch dans une fiche. Il y en a 576, dans 278 fiches.
- On cherche `controparte`, `contro parte`, `invertit…`, `inversione`, `speculare`… dans la proposition qui contient la référence. On regarde d'abord à gauche de la référence (« X è ripresa, in controparte, dalla … (Bartsch …) »). On regarde à droite seulement si aucune autre source n'est introduite entre les deux.
- On cherche aussi les négations (« non in controparte », « senza inversione », « non invertita »). On n'en trouve **aucune**.
- Le graveur de chaque estampe vient d'une table faite à la main dans `../commun.py`, d'après ce que disent la plupart des fiches.
- Test de tendance : on permute les périodes entre pièces, pas entre références (les références d'une même pièce ne sont pas indépendantes). 10 000 tirages.

## Résultats

- **63 références sur 576 (10,9 %)** sont dites inversées. Cela touche 53 des 278 fiches qui ont une référence.
- Presque toutes les mentions (62) précèdent la référence. Une seule la suit.
- Il y a 15 fiches qui parlent d'une inversion sans la rattacher à une référence Bartsch (liste : `mentions_non_rattachees.csv`). C'est surtout le cas des *Modi*, cités sans numéro : 2 inversions sur 40 mentions (pièces 469 et 484).

| Graveur | Références | Inversées | Part |
|---|---|---|---|
| Marcantonio | 303 | 34 | 11 % |
| Caraglio | 132 | 16 | 12 % |
| Marco Dente | 90 | 7 | 8 % |
| Agostino Veneziano | 32 | 6 | 19 % |
| Maestro I.B. | 15 | 0 | 0 % |

| Période | Références | Inversées | Part | Avec les seules dates inscrites |
|---|---|---|---|---|
| ≤ 1530 | 94 | 7 | 7,4 % | 4/18 (22 %) |
| 1531-1535 | 325 | 32 | 9,8 % | 31/291 (11 %) |
| 1536-1542 | 126 | 19 | 15,1 % | 18/109 (17 %) |

La hausse entre ≤ 1530 et 1536-1542 n'est pas significative (différence de +7,6 points, p de permutation = 0,14). Celle entre 1531-1535 et 1536-1542 ne l'est pas non plus (+5,2 points, p = 0,14).

Par estampe (`inversion_par_estampe.csv`), on va de 0 % (*Davide e Golia*, 13 références ; *Sol* du Maître I.B., 11) à 33 % (*Martirio di Santa Cecilia* et *Cristo in casa di Simone*, 4 sur 12). L'estampe la plus employée, le *Parnaso* (76 références), n'est dite inversée que 4 fois (5 %). La *Contesa* de Caraglio l'est 10 fois sur 71 (14 %).

Données du graphique : `resultats.json` → `par_graveur`, `par_periode`, `par_estampe` (part inversée par barre).

## Ce que cela dit des thèses

**Pas de conclusion possible.** Si le carton était posé au hasard d'un côté ou de l'autre, comme le suppose Hess, on attendrait environ une figure sur deux inversée. Le catalogue n'en signale qu'une sur neuf. Mais le silence d'une fiche ne prouve pas que la figure est dans le même sens : le rédacteur peut ne pas l'avoir noté. Le chiffre de 11 % est donc un minimum. La hausse en fin de carrière va dans le sens d'un procédé employé de plus en plus. Elle n'est pas significative.

## Limites

- C'est l'auteur de la fiche (C.G.) qui dit « in controparte », pas une mesure sur les images. La seule vérification possible est de comparer l'image de l'assiette et celle de l'estampe (voir `prototype/`).
- Les références d'une fiche ont souvent la même formule. Une fiche attentive au sens des figures pèse plus qu'une fiche rapide.
- Le graveur attribué à une estampe varie selon les fiches (par exemple B26.211 est donnée à Marco Dente, à Agostino ou à Marcantonio). On a gardé une seule attribution par estampe.

## Fichiers

`inversion_par_reference.csv` (une ligne par référence : estampe, graveur, position de la mention, année, lien), `inversion_par_estampe.csv`, `mentions_non_rattachees.csv`, `resultats.json`.
