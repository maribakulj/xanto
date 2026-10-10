# T-dates — une date par pièce

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. Chaque date est à vérifier sur la fiche (colonne `link`).**

## Question

Les autres tests ont besoin d'une année par pièce. Une date peinte sur la pièce est plus sûre qu'une datation « vers 1530 » proposée par le catalogue. On garde donc la source de chaque date.

## Méthode (`../t_dates.py`, fonctions dans `../commun.py`)

1. On lit la section « Iscrizioni » de la fiche et on cherche une année entre 1500 et 1545, en chiffres arabes (`1532`) ou romains (`M.D.XXXI`).
2. Sans année lisible, on prend la date de la fiche : année simple (`1532`), année « ca. », ou milieu d'un intervalle (`1527-1530 ca.` donne 1528).
3. Si l'inscription et la fiche donnent deux années différentes, on garde celle de la fiche et on le signale (2 cas : 843 et 1138).
4. Périodes : ≤ 1530, 1531-1535, 1536-1542. Une pièce datée par un intervalle qui chevauche deux périodes n'a pas de période.

## Résultats

| Source de la date | Pièces |
|---|---|
| année inscrite sur la pièce | 244 |
| année de la fiche | 28 |
| année de la fiche « ca. » | 25 |
| milieu d'un intervalle de la fiche | 62 |
| désaccord inscription / fiche | 2 |
| aucune date | 13 |

| Période | Pièces |
|---|---|
| ≤ 1530 | 93 |
| 1531-1535 | 161 |
| 1536-1542 | 100 |
| sans période (pas de date, ou intervalle à cheval) | 20 |

L'année la plus fournie est 1532 (54 pièces, dont 49 dates inscrites). Données du graphique : `pieces_par_annee.csv` (barres empilées par année : inscrites / année de la fiche / milieu d'intervalle).

## Limites

- **Les deux bouts de la carrière ne sont pas datés de la même façon.** Avant 1531, la plupart des dates sont des estimations du catalogue (en 1528-1529, 39 pièces sur 50 sont datées par le milieu d'un intervalle). À partir de 1531, presque toutes les dates sont inscrites. Toute comparaison entre « avant 1531 » et « après » mélange donc une différence de période et une différence de qualité de la date.
- 12 dates sont des dates de lustre, posées à Gubbio (« M° G° »). Elles datent le lustre, pas forcément la peinture. Elles sont signalées dans `note_date`.
- Le chiffre romain est lu automatiquement. Une transcription fautive de la fiche donne une fausse année (cas 843, signalé).
- Le catalogue de Rovigo ne contient pas toute l'œuvre de Xanto, et les fiches en double (même objet décrit deux fois) n'ont pas été dédoublonnées.

## Fichiers

- `dates_par_piece.csv` : id, année retenue, bornes, source de la date, période, lien vers la fiche.
- `pieces_par_annee.csv` : comptes par année et par source.
- `resultats.json` : les mêmes comptes, plus les listes d'identifiants (sans date, à cheval, désaccords, dates de Gubbio).
