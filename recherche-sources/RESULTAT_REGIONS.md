# Étape 3, régions côté estampe : résultat (règle : `PREINSCRIPTION_REGIONS.md`)

Date : 15/10/2026. Calcul complet en local (DINOv3 large, 27 547 régions à 384 px, environ 8 h sur MPS). Données : `resultats/regions_dinov3_large_mise_au_point58.csv`, comparé à la base `resultats/paires_dinov3_large_mise_au_point58.csv` (58 requêtes de mise au point ; les 105 d'évaluation restent fermées).

## Verdict préinscrit : la règle n'est pas remplie

| | rang 1 | 10 premières | 50 premières | rang médian |
|---|---|---|---|---|
| base (image entière 512 px + SegSwap) | 8 | 20 | 31 | 39 |
| régions (max base/régions + SegSwap) | 5 | 24 | 36 | 17 |

29 requêtes montent, 24 descendent : net 5 (il fallait au moins 6), p = 0,58 au test du signe (il fallait p < 0,05). Il n'y a pas moins de requêtes dans les 50 premières (36 contre 31), mais les deux autres conditions échouent. Par estampe : 6 montent, 4 descendent (p = 0,75). **La base reste DINOv3 large sur l'image entière.**

## Descriptif (sans verdict ; plusieurs comparaisons faites après coup, à ne pas lire comme des preuves)

Rangs **avant** SegSwap (présélection par cosinus), comparés à la présélection de la base (7 / 21 / 31, médiane 39) :

| présélection | rang 1 | 10 prem. | 50 prem. | médiane | monte / descend | p |
|---|---|---|---|---|---|---|
| régions (grille + personnes) | 10 | 28 | 36 | 17 | 32 / 18 | 0,065 |
| grille seule | 8 | 24 | 30 | 47 | 27 / 22 | 0,57 |
| personnes seules | 11 | 28 | 40 | 12 | 32 / 16 | 0,029 |
| régions sans l'image entière | 9 | 27 | 36 | 17 | 32 / 20 | 0,13 |

- **Les régions améliorent la présélection, mais le reclassement par SegSwap défait une partie du gain** : avant SegSwap, 10 requêtes au rang 1 et 28 dans les 10 premières ; après, 5 et 24. SegSwap compare la figure du plat à l'estampe *entière* (244 px). Il ne voit donc pas la région qui a fait remonter l'estampe. Dans la base aussi, SegSwap n'apportait presque rien (7/21 avant, 8/20 après).
- Ce sont les **boîtes « personne »** qui portent le gain ; la grille seule n'apporte rien. Le seuil de Holm pour quatre comparaisons (0,0125) n'est pas atteint par « personnes seules » (p = 0,029), et cette variante a été choisie après avoir vu les chiffres.
- *Bataille au coutelas* (26/211, 9 requêtes) : 8 montent sur 9 ; 5 requêtes passent de 318-707 à 27-93, et la meilleure région est le plus souvent la boîte du soldat tombé (2183,1977,3384,2466). Aucune n'entre dans les 10 premières : la région du soldat reste trop grossière.
- Grandes pertes : Q055 (398 → 669), Q071 (145 → 324), Q47 (104 → 356), Q059 (5 → 60), Q51 (3 → 28). Pour une même figure, d'autres estampes ont une région qui lui ressemble davantage : le nombre de candidats est multiplié par 17.
- Source absente : les scores SegSwap de la vraie estampe (1,0-21,5) et de la meilleure estampe fausse quand la vraie est retirée (3,9-15,5) se chevauchent toujours. Le système ne sait toujours pas dire « la source n'est pas dans la collection ».

## Ce qui en découle (à préinscrire avant tout nouveau calcul)

La piste suivante, la plus directe, est de faire reclasser par SegSwap (ou par une correspondance patch par patch) la **région** qui a fait remonter l'estampe, et non l'estampe entière. Les vecteurs des régions sont en cache : un tel essai prendrait quelques minutes. Les 58 requêtes de mise au point ont déjà servi plusieurs fois ; seule l'évaluation sur les 105 requêtes fermées tranchera.
