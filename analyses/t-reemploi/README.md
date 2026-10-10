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
| B26.104 *Martirio di San Lorenzo* (Marcantonio) | 52 | 1525* (1528 sans le groupe de Gubbio) | 1542 |
| B27.352 *Quos Ego* | 29 | 1522* (1528 sans le groupe de Gubbio) | 1540 |
| B27.420 *Battaglia* (Marco Dente) | 29 | 1525* (1528 sans le groupe de Gubbio) | 1542 |
| B26.209 *Ratto di Elena* | 27 | 1528 | 1540 |
| B28.62 *Alessandro e Rossana* (Caraglio) | 27 | 1530 | 1541 |

\* Premières années tirées de pièces d'attribution débattue, datées avant 1528 (voir `../t-dates`). Le *Quos Ego* « de 1522 » vient de la pièce 194, dont la date est peinte sur une tablette dans la scène (« OMNIA VINCIT AMOR 1522 ») : ce n'est très probablement pas une date d'exécution. Elle n'est plus comptée parmi les dates inscrites ; l'année retenue reste celle du catalogue (1522), signalée. Les premières années à 1525 viennent de pièces dont le champ date était mal lu avant le 10/10/2026 (ex. 126).

15 estampes sur 54 n'apparaissent que sur une seule pièce. Les trois estampes principales servent du début à la fin de la carrière.

Par période (variante `toutes` ; ici la période vient de l'année retenue, milieu d'intervalle compris, d'où 106 / 167 / 101 pièces au lieu de 101 / 164 / 101 dans T-dates) :

| | ≤ 1530 | 1531-1535 | 1536-1542 |
|---|---|---|---|
| pièces | 106 | 167 | 101 |
| part des pièces avec au moins une source identifiée | 61 % | 86 % | 68 % |
| estampes par pièce (si source) | 1,78 | 2,31 | 1,84 |
| estampes distinctes employées | 30 | 40 | 29 |
| estampes nouvelles | 30 | 18 | 6 |
| part des 5 estampes les plus citées | 44 % | 49 % | 44 % |
| pièces dont la combinaison exacte est déjà vue (sur les pièces à ≥ 2 estampes) | 4/35 | 20/104 | 14/39 (36 %) |

Contrôle par permutation (variante `toutes`, puis `inscrites`) :

| Mesure pour 1536-1542 | Observé | Hasard (moyenne, intervalle à 95 %) | Lecture |
|---|---|---|---|
| estampes introduites | 6 (4) | 4,3 [1-8] (4,9 [1-9]) | normal |
| part des références tardives qui vont à des estampes nouvelles | 7,9 % (7,4 %) | 3,1 % [0,7-6,3] (4,3 % [1,3-8,5]) | plus de nouveauté que le hasard (p = 0,006 ; p = 0,06) |
| combinaisons déjà vues | 36 % (38 %) | 31 % [21-42] (26 % [17-36]) | un peu au-dessus (p = 0,19 ; p = 0,012) |

Avant la correction des dates du 10/10/2026 : p = 0,007 et 0,07 (nouveauté), p = 0,10 et 0,02 (combinaisons).

**Sensibilité** (`../t-sensibilite`), sans les 26 pièces d'attribution débattue (Gubbio 1522-1527, F.R.) : nouveauté p = 0,004 (toutes dates) et 0,06 (inscrites) ; combinaisons p = 0,13 et 0,007. Sans, en plus, les pièces marquées y/Ø (70 pièces exclues) : nouveauté p = 0,016 et 0,04 ; combinaisons p = 0,12 et 0,009. Les conclusions ne changent pas.

Données du graphique : `par_annee_toutes.csv` (estampes distinctes et estampes nouvelles par année), `resultats.json` → `par_estampe` (pour chaque estampe, liste des pièces avec id et année : frise de réemploi).

## Ce que cela dit des thèses

- **Le petit nombre d'estampes nouvelles après 1536 ne prouve pas une fin de carrière répétitive.** Il est attendu par simple accumulation. Le nombre observé (6) est même un peu au-dessus de ce que donne le hasard, et la part des références tardives qui vont à des estampes nouvelles est plus forte que par hasard.
- Les pièces tardives sont **plus simples** : moins d'estampes par pièce (1,93 contre 2,47 en comptant les *Modi*, p = 0,002 ; voir `../t-sources-par-piece`), et moins de pièces avec une source identifiée.
- Les combinaisons exactes déjà employées sont un peu plus fréquentes à la fin (36 % contre 31 % par hasard). C'est significatif seulement avec les dates inscrites (p = 0,012, sans correction pour tests multiples ; 0,18 après correction de Holm sur toutes les p rapportées). Cela soutient faiblement le jugement « répétitif » de Mallet, au niveau des assemblages et non du stock d'estampes.
- La hâte (Liverani) n'est pas mesurable avec ces données. Le réemploi d'un petit noyau d'estampes pendant quinze ans est compatible avec la méthode délibérée décrite par Mallet.

## Limites

- On ne compte que les estampes identifiées par le catalogue. Une pièce sans référence n'est pas forcément sans source.
- La répétition par Xanto de ses propres compositions (renvois « Scheda n. ») n'est pas comptée. Ces renvois donnent un numéro de fiche, pas l'identifiant de la pièce.
- Les doublons possibles du catalogue (par exemple 254 et 278, même texte) gonflent les combinaisons répétées.
- Avant 1531, les dates sont surtout des estimations (voir `../t-dates`).

## Fichiers

`reemploi_par_estampe.csv`, `par_annee_toutes.csv`, `par_annee_inscrites.csv`, `combinaisons_repetees.csv`, `resultats.json`.
