# Étape 3 bis : faire reclasser par SegSwap la région gagnante (règle écrite avant calcul)

Date : 17/10/2026, avant tout calcul de rang avec cette variante. Motif : `RESULTAT_REGIONS.md`. Les régions améliorent la présélection (10 requêtes au rang 1 et 28 dans les 10 premières, contre 7 et 21). Mais SegSwap compare ensuite la figure du plat à l'estampe *entière* et défait une partie du gain (5 et 24 après reclassement).

## Méthode (`regions.py`, variable d'environnement `RECLASSE=region`)

- Présélection **identique** à l'étape 3 : score = max(base sur l'image entière, meilleure région parmi la grille 2×2 et 3×3 et les boîtes « personne »), figure à l'endroit et en miroir, 20 premières ; mêmes vecteurs (caches de l'étape 3).
- Reclassement SegSwap des 20 premières (et des 20 premières fausses pour le test « source absente »), mais sur une autre image : pour chaque estampe dont la meilleure région bat l'image entière, SegSwap reçoit **cette région**, complétée en carré par le gris moyen, à la place de l'estampe entière, dans le sens qui a donné ce score. Sinon, il reçoit l'estampe entière, comme avant. La figure du plat est inchangée.
- Toutes les régions sont gardées, y compris la grille. La variante « personnes seules » a paru meilleure, mais elle a été repérée après coup ; elle n'est pas retenue pour le verdict.
- Aucun réglage n'est fait après avoir vu un rang.

## Règle

Sur les **58 requêtes de mise au point**, comparaison requête par requête avec la **base** (`resultats/paires_dinov3_large_mise_au_point58.csv`, rang final de la vraie estampe) :

- la variante **gagne** si elle fait monter la vraie estampe **au moins six fois de plus** qu'elle ne la fait descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** si elle ne place pas moins de requêtes dans les 50 premières ;
- publiés sans valeur de verdict : le même test par estampe ; la comparaison avec l'étape 3 (`regions_dinov3_large_mise_au_point58.csv`) ; les 9 requêtes de la *Bataille au coutelas* ; le test « source absente ».

Réserve : les 58 requêtes ont déjà servi à plusieurs choix. Même si la variante gagne, seul l'unique calcul sur les 105 requêtes d'évaluation fermées tranchera. Le lot d'évaluation n'est pas calculé.
