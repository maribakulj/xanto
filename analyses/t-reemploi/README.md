# T-reuse (C1) — réemploi des estampes dans le temps

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches (liens dans les fichiers).**

## Thèses discutées

- Liverani 1962 : le réemploi trahirait la négligence (« trascuratezza ») et la hâte.
- Poole 1995 : « repetitiousness ».
- Mallet 2007 : une méthode délibérée de couper-coller. La fin de carrière serait « répétitive ».

## Méthode (`../t_reemploi.py`)

- Une estampe = une clé Bartsch `B<vol>.<n>` (54 estampes distinctes). Pour chaque pièce, on prend l'ensemble des estampes citées : une estampe citée deux fois dans la même fiche compte une fois.
- Pour chaque estampe : liste des pièces avec leur année, première et dernière année.
- Pour chaque année : estampes distinctes employées. Une estampe est « nouvelle » l'année de sa première apparition datée.
- Pour chaque période : nombre d'estampes nouvelles, part des 5 estampes les plus citées, indice de Herfindahl, références par pièce, et nombre de pièces dont la combinaison exacte d'estampes (au moins 2) a déjà servi sur une pièce plus ancienne.
- **Contrôle par permutation.** Plus on avance dans la carrière, plus on a déjà vu d'estampes. Il y a donc mécaniquement moins d'estampes nouvelles à la fin, même si la méthode ne change pas. Pour en tenir compte, on mélange 10 000 fois les années entre les pièces et on regarde la valeur obtenue par hasard.
- Deux variantes : `toutes` (année retenue, y compris « ca. » et milieux d'intervalle) et `inscrites` (seulement les dates lues sur la pièce).

## Résultats

Estampes les plus réemployées (`reemploi_par_estampe.csv`) :

| Estampe | Pièces | Première année | Dernière année |
|---|---|---|---|
| B26.247 *Parnaso* (Marcantonio) | 76 | 1528 | 1542 |
| B28.53 *Contesa tra le Muse e le Pieridi* (Caraglio) | 71 | 1528 | 1541 |
| B26.104 *Martirio di San Lorenzo* (Marcantonio) | 52 | 1528 | 1542 |
| B27.352 *Quos Ego* | 29 | 1522 | 1540 |
| B27.420 *Battaglia* (Marco Dente) | 29 | 1528 | 1542 |
| B26.209 *Ratto di Elena* | 27 | 1528 | 1540 |
| B28.62 *Alessandro e Rossana* (Caraglio) | 27 | 1530 | 1541 |

15 estampes sur 54 n'apparaissent que sur une seule pièce. Les trois estampes principales servent du début à la fin de la carrière.

Par période (variante `toutes` ; ici la période vient de l'année retenue, milieu d'intervalle compris, d'où 97 / 164 / 100 pièces au lieu de 93 / 161 / 100 dans T-dates) :

| | ≤ 1530 | 1531-1535 | 1536-1542 |
|---|---|---|---|
| pièces | 97 | 164 | 100 |
| part des pièces avec au moins une source identifiée | 61 % | 87 % | 68 % |
| estampes par pièce (si source) | 1,78 | 2,30 | 1,84 |
| estampes distinctes employées | 29 | 39 | 29 |
| estampes nouvelles | 29 | 18 | 6 |
| part des 5 estampes les plus citées | 44 % | 49 % | 44 % |
| pièces dont la combinaison exacte est déjà vue (sur les pièces à ≥ 2 estampes) | 2/32 | 19/102 | 14/38 (37 %) |

Contrôle par permutation (variante `toutes`, puis `inscrites`) :

| Mesure pour 1536-1542 | Observé | Hasard (moyenne, intervalle à 95 %) | Lecture |
|---|---|---|---|
| estampes introduites | 6 (4) | 4,3 [1-8] (4,5 [1-8]) | normal |
| part des références tardives qui vont à des estampes nouvelles | 8,0 % (7,4 %) | 3,1 % [0,7-6,5] (4,2 % [0,8-8,7]) | plus de nouveauté que le hasard (p = 0,007 ; p = 0,07) |
| combinaisons déjà vues | 37 % (38 %) | 30 % [20-41] (27 % [17-37]) | un peu au-dessus (p = 0,10 ; p = 0,02) |

Données du graphique : `par_annee_toutes.csv` (estampes distinctes et estampes nouvelles par année), `resultats.json` → `par_estampe` (pour chaque estampe, liste des pièces avec id et année : frise de réemploi).

## Ce que cela dit des thèses

- **Le petit nombre d'estampes nouvelles après 1536 ne prouve pas une fin de carrière répétitive.** Il est attendu par simple accumulation. Le nombre observé (6) est même un peu au-dessus de ce que donne le hasard, et la part des références tardives qui vont à des estampes nouvelles est plus forte que par hasard.
- Les pièces tardives sont **plus simples** : moins d'estampes par pièce (1,93 contre 2,46 en comptant les *Modi*, p = 0,003 ; voir `../t-sources-par-piece`), et moins de pièces avec une source identifiée.
- Les combinaisons exactes déjà employées sont un peu plus fréquentes à la fin (37 % contre 30 % par hasard). C'est significatif seulement avec les dates inscrites. Cela soutient faiblement le jugement « répétitif » de Mallet, au niveau des assemblages et non du stock d'estampes.
- La hâte (Liverani) n'est pas mesurable avec ces données. Le réemploi d'un petit noyau d'estampes pendant quinze ans est compatible avec la méthode délibérée décrite par Mallet.

## Limites

- On ne compte que les estampes identifiées par le catalogue. Une pièce sans référence n'est pas forcément sans source.
- La répétition par Xanto de ses propres compositions (renvois « Scheda n. ») n'est pas comptée. Ces renvois donnent un numéro de fiche, pas l'identifiant de la pièce.
- Les doublons possibles du catalogue (par exemple 254 et 278, même texte) gonflent les combinaisons répétées.
- Avant 1531, les dates sont surtout des estimations (voir `../t-dates`).

## Fichiers

`reemploi_par_estampe.csv`, `par_annee_toutes.csv`, `par_annee_inscrites.csv`, `combinaisons_repetees.csv`, `resultats.json`.
