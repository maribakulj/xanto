# T-sources-per-plate — combien d'estampes par pièce ?

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches.**

## Question

Le collage se complique-t-il ou se simplifie-t-il avec le temps ? On compte les estampes distinctes citées par pièce, *Modi* compris.

## Méthode (`../t_sources_par_piece.py`)

- Pour chaque pièce, on compte les estampes distinctes citées dans la fiche : les clés Bartsch, plus « Modi » si les *Modi* sont mentionnés.
- La moyenne est calculée seulement sur les pièces qui ont au moins une source. Une fiche muette ne dit pas qu'il n'y a pas de source.
- Test 1531-1535 contre 1536-1542 : permutation des pièces, 10 000 tirages.

## Résultats

- Sur 374 pièces, 283 (76 %) ont au moins une estampe identifiée. La moyenne est de 2,17 estampes par pièce (médiane 2, maximum 8 : pièce 399).
- Répartition : 0 estampe : 91 pièces ; 1 : 92 ; 2 : 98 ; 3 : 59 ; 4 : 28 ; 5 ou plus : 6.

| Période | Pièces | Part avec source | Estampes par pièce (si source) |
|---|---|---|---|
| ≤ 1530 | 93 | 61 % | 1,74 |
| 1531-1535 | 161 | 89 % | 2,46 |
| 1536-1542 | 100 | 68 % | 1,93 |

- Avec les seules dates inscrites, on obtient 1,43, puis 2,49, puis 1,93.
- La baisse entre 1531-1535 et 1536-1542 est de −0,54 estampe par pièce (p = 0,003).
- Le collage culmine en 1532-1533 : 2,6 et 2,9 estampes par pièce (`par_annee.csv`).

Données du graphique : `par_annee.csv` (moyenne et part avec source par année).

## Lecture

Le collage le plus complexe date du milieu de la carrière (1531-1535). Les pièces tardives citent moins d'estampes, et une plus grande part n'a aucune source identifiée. Deux explications restent possibles, et ce test ne permet pas de choisir :
- un changement de pratique (figures inventées, reprise de ses propres compositions, travail d'atelier) ;
- un catalogue moins attentif pour ces pièces.

Cela ne va pas dans le sens d'une fin de carrière faite d'assemblages d'estampes de plus en plus mécaniques.

## Limites

Mêmes limites que pour `../t-reemploi`. Le nombre d'estampes identifiées dépend aussi de l'état des recherches sur chaque pièce.

## Fichiers

`sources_par_piece.csv`, `par_annee.csv`, `resultats.json`.
