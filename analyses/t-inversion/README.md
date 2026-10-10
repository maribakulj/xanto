# T-inversion (B1) — figures reprises « in controparte »

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. Chaque ligne est à vérifier sur la fiche (colonne `link`).**

## Thèses discutées

- Hess 1999 (n. 44) : l'inversion « is irrelevant » *comme indice* (de l'emploi direct de l'estampe ou non), puisqu'un carton troué se ponce des deux côtés. Hess ne dit rien de la fréquence des inversions ni d'un carton posé au hasard.
- Rondot 1994, Gallian (essais du site de Rovigo) : Xanto inverse volontairement les figures (« in controparte ») pour varier ; une même figure serait reprise « inversée ou non ».

## Méthode (`../t_inversion.py`)

- Unité : une référence Bartsch dans une fiche. Il y en a 576, dans 278 fiches.
- On cherche `controparte`, `contro parte`, `invertit…`, `inversione`, `speculare`… dans la proposition qui contient la référence. On regarde d'abord à gauche de la référence (« X è ripresa, in controparte, dalla … (Bartsch …) »). On regarde à droite seulement si aucune autre source n'est introduite entre les deux.
- On cherche aussi les négations (« non in controparte », « senza inversione », « non invertita »). On n'en trouve **aucune**.
- Le graveur de chaque estampe vient d'une table faite à la main dans `../commun.py`, d'après ce que disent la plupart des fiches.
- Test de tendance : on permute les périodes entre pièces, pas entre références (les références d'une même pièce ne sont pas indépendantes). 10 000 tirages. La période est une propriété du plat : cette permutation est valable ici.
- **Résultat principal : les seules dates inscrites.** Avant 1531 les dates sont surtout des estimations (voir `../t-dates`). La pièce 194 n'est plus comptée parmi les dates inscrites (sa date de 1522 est peinte dans la scène).

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

**Dans le temps : pas de tendance.** Résultat principal, avec les seules dates inscrites :

| Période | Dates inscrites seulement | Toutes les dates (pour mémoire) |
|---|---|---|
| ≤ 1530 | **3/15 (20 %)** | 8/105 (7,6 %) |
| 1531-1535 | **31/291 (11 %)** | 33/331 (10,0 %) |
| 1536-1542 | **18/109 (17 %)** | 20/128 (15,6 %) |

Avec les dates inscrites, la série n'est pas monotone (20 %, 11 %, 17 %), et aucune différence n'est significative (≤ 1530 contre 1536-1542 : −3,5 points, p = 0,76 ; 1531-1535 contre 1536-1542 : +5,9 points, p = 0,14). La « légère tendance à la hausse » annoncée avant le 10/10/2026 (7 %, 10 %, 15 % ; p = 0,10 avec les données corrigées, 0,14 avant) **disparaît** : elle tenait à la période ≤ 1530, datée surtout par estimation. La variation dépend de la qualité des dates. (La relecture critique donnait 22 %, 11 %, 17 % : la différence vient de la pièce 194, retirée des dates inscrites.)

Sensibilité (`../t-sensibilite`) : sans les 26 pièces d'attribution débattue (groupe de Gubbio 1522-1527, initiales F.R.), la série « toutes dates » devient 5,5 %, 10 %, 15,6 % et la différence extrême passe sous 0,05 (p = 0,04) ; avec les dates inscrites, 2/8, 31/291, 18/109 (p = 0,59). La conclusion ne change pas : la seule série fiable (dates inscrites) n'a pas de tendance, et ≤ 1530 n'y compte que 3 à 15 références.

Par estampe (`inversion_par_estampe.csv`), on va de 0 % (*Davide e Golia*, 13 références ; *Sol* du Maître I.B., 11) à 33 % (*Martirio di Santa Cecilia* et *Cristo in casa di Simone*, 4 sur 12). L'estampe la plus employée, le *Parnaso* (76 références), n'est dite inversée que 4 fois (5 %). La *Contesa* de Caraglio l'est 10 fois sur 71 (14 %).

Données du graphique : `resultats.json` → `par_graveur`, `par_periode_dates_inscrites` (série principale, avec les effectifs), `par_periode` (toutes dates, pour mémoire), `par_estampe` (part inversée par barre).

## Ce que cela dit des thèses

**Pas de conclusion possible.** Le chiffre de 11 % ne soutient ni n'affaiblit Hess : Hess soutient seulement que l'inversion ne prouve rien (un carton se ponce des deux côtés), pas que le carton est posé au hasard. Un peintre qui ponce toujours par le même côté donne 0 % d'inversion, et Hess reste juste. Le silence d'une fiche ne prouve pas non plus que la figure garde son sens : 11 % est un minimum. Il n'y a pas de tendance dans le temps avec les dates fiables. Le test qui départagerait Rondot et Hess serait autre : pour une même figure répétée sur plusieurs plats, l'orientation change-t-elle d'un plat à l'autre ? Il se compte par estampe et par figure, pas par référence (non fait).

## Limites

- C'est l'auteur de la fiche (C.G.) qui dit « in controparte », pas une mesure sur les images. La seule vérification possible est de comparer l'image de l'assiette et celle de l'estampe (voir `prototype/`).
- Les références d'une fiche ont souvent la même formule. Une fiche attentive au sens des figures pèse plus qu'une fiche rapide.
- Le graveur attribué à une estampe varie selon les fiches (par exemple B26.211 est donnée à Marco Dente, à Agostino ou à Marcantonio). On a gardé une seule attribution par estampe.

## Fichiers

`inversion_par_reference.csv` (une ligne par référence : estampe, graveur, position de la mention, année, lien), `inversion_par_estampe.csv`, `mentions_non_rattachees.csv`, `resultats.json`.
