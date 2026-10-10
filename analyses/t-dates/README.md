# T-dates — une date par pièce

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. Chaque date est à vérifier sur la fiche (colonne `link`).**

## Question

Les autres tests ont besoin d'une année par pièce. Une date peinte sur la pièce est plus sûre qu'une datation « vers 1530 » proposée par le catalogue. On garde donc la source de chaque date.

## Méthode (`../t_dates.py`, fonctions dans `../commun.py`)

1. On lit la section « Iscrizioni » de la fiche et on cherche une année entre 1500 et 1545, en chiffres arabes (`1532`) ou romains (`M.D.XXXI`).
2. Sans année lisible, on prend la date de la fiche : année simple (`1532`), année « ca. », ou milieu d'un intervalle (`1527-1530 ca.` donne 1528).
3. Si l'inscription et la fiche donnent deux années différentes, on garde celle de la fiche et on le signale (2 cas : 843 et 1138).
4. Une année lue **seulement sur le droit**, dans un cartouche ou une tablette peints dans la scène, est signalée (`note_date` : « date peinte dans la scène »). Avant 1528, elle n'est pas comptée comme date inscrite : c'est le cas de la pièce 194 (« OMNIA VINCIT AMOR 1522 » sur une tablette, revers non travaillé), le prétendu premier emploi du *Quos Ego* « en 1522 ». Après 1528, ces dates sur le droit (360, 1106, 387, 1221, 1239) accompagnent la signature de Xanto et sont gardées.
5. Périodes : ≤ 1530, 1531-1535, 1536-1542. Une pièce datée par un intervalle qui chevauche deux périodes n'a pas de période.
6. Indicateurs d'attribution (colonnes de `dates_par_piece.csv`) : `avant_1528` (année retenue avant 1528), `initiales_FR`, `marque_y_slash`, et `attribution_debattue` = avant 1528 ou F.R. (26 pièces). Ils servent à l'analyse de sensibilité (`../t-sensibilite`).

**Correction du 10/10/2026.** Le champ `data` de `data/pieces.csv` était lu par position dans `scripts/rovigo_table.py` : pour 38 fiches il contenait l'inscription, pour 25 il était vide. Il est maintenant repéré par sa forme (année, intervalle, « ca. »). 63 lignes ont changé ; il n'y a plus de pièce sans date.

## Résultats

| Source de la date | Pièces (avant correction) |
|---|---|
| année inscrite sur la pièce | 243 (244) |
| année de la fiche | 36 (28) |
| année de la fiche « ca. » | 25 (25) |
| milieu d'un intervalle de la fiche | 67 (62) |
| désaccord inscription / fiche | 2 (2) |
| date peinte dans la scène, non retenue (194) | 1 (0) |
| aucune date | 0 (13) |

| Période | Pièces (avant correction) |
|---|---|
| ≤ 1530 | 101 (93) |
| 1531-1535 | 164 (161) |
| 1536-1542 | 101 (100) |
| sans période (intervalle à cheval) | 8 (20) |

L'année la plus fournie est 1532 (56 pièces, dont 49 dates inscrites). Données du graphique : `pieces_par_annee.csv` (barres empilées par année : inscrites / année de la fiche / milieu d'intervalle).

### Les pièces datées avant 1528

26 pièces ont une année retenue entre 1522 et 1527. **Aucune de leurs dates « inscrites » n'est une date d'exécution sûre de Xanto** :
- les 11 dates lues sur le revers sont des **dates de lustre de Gubbio** (« M° G° », « Mastro Giorgio da ugubio ») : 1045, 1052, 1175 (1524) ; 190, 346, 1129, 1148, 1166, 1171, 1179, 1184 (1525). Elles datent le lustre posé dans l'atelier de Maestro Giorgio, pas forcément la peinture. (Sur toute la table, 16 dates de lustre, dont 116 en 1529.)
- 1 date est **peinte dans la scène** (194, 1522), voir plus haut.
- les autres sont des estimations du catalogue (611 « 1522 ca. », 942 « 1522-1525 ca. », 126, 507, 1133 « 1525 »…), dont 4 pièces aux initiales F.R. (942, 947, 950, 446).

Ce groupe de Gubbio, que Mallet donne au jeune Xanto et que Wilson lui refuse, est d'**attribution débattue**. Les tests chronologiques sont refaits sans lui dans `../t-sensibilite`.

## Limites

- **Les deux bouts de la carrière ne sont pas datés de la même façon.** Avant 1531, la plupart des dates sont des estimations du catalogue (en 1528-1529, 39 pièces sur 50 sont datées par le milieu d'un intervalle). À partir de 1531, presque toutes les dates sont inscrites. Toute comparaison entre « avant 1531 » et « après » mélange donc une différence de période et une différence de qualité de la date.
- 16 dates sont des dates de lustre, posées à Gubbio (« M° G° »). Elles datent le lustre, pas forcément la peinture. Elles sont signalées dans `note_date` (l'expression régulière en manquait 4 avant le 10/10/2026 : « M°. G°. »).
- Le chiffre romain est lu automatiquement. Une transcription fautive de la fiche donne une fausse année (cas 843, signalé).
- Le catalogue de Rovigo ne contient pas toute l'œuvre de Xanto, et les fiches en double (même objet décrit deux fois) n'ont pas été dédoublonnées.

## Fichiers

- `dates_par_piece.csv` : id, année retenue, bornes, source de la date, période, lien vers la fiche.
- `pieces_par_annee.csv` : comptes par année et par source.
- `resultats.json` : les mêmes comptes, plus les listes d'identifiants (sans date, à cheval, désaccords, dates de Gubbio, dates peintes dans la scène, pièces avant 1528, attribution débattue).
