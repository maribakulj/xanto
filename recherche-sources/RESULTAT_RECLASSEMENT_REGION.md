# Étape 3 bis, reclassement SegSwap sur la région gagnante : résultat (règle : `PREINSCRIPTION_RECLASSEMENT_REGION.md`)

Date : 17/10/2026. Calcul en local, environ 25 min (vecteurs des régions repris du cache de l'étape 3). Données : `resultats/regions_reclasse_region_mise_au_point58.csv`.

## Verdict préinscrit : la règle n'est pas remplie (de peu)

| 58 requêtes de mise au point | rang 1 | 10 premières | 50 premières | rang médian |
|---|---|---|---|---|
| base (image entière + SegSwap sur l'estampe entière) | 8 | 20 | 31 | 39 |
| étape 3 (régions + SegSwap sur l'estampe entière) | 5 | 24 | 36 | 17 |
| présélection de l'étape 3 seule, sans SegSwap | 10 | 28 | 36 | 17 |
| **régions + SegSwap sur la région gagnante** | **13** | **29** | **36** | **11** |

Contre la base, 32 requêtes montent et 20 descendent : net 12 (il fallait au moins 6), 36 requêtes dans les 50 premières contre 31 (il ne fallait pas moins), mais **p = 0,13** (il fallait p < 0,05). Par estampe : 7 montent, 3 descendent (p = 0,34). **La base ne change pas.**

## Descriptif (sans verdict)

- Contre l'étape 3, qui ne diffère que par l'image donnée à SegSwap : 17 montent, 6 descendent (p = 0,035 ; par estampe 7/1). Donner la région à SegSwap fait bien mieux que lui donner l'estampe entière.
- Le p contre la base reste élevé parce que la présélection par régions, commune à l'étape 3, déplace beaucoup de requêtes dans les deux sens au-delà des 20 premières : les pertes de l'étape 3 (Q055, Q071, Q47…) sont toujours là.
- Parmi les 30 requêtes dont la vraie estampe est dans les 20 premières de la présélection, SegSwap la fait encore descendre plus souvent qu'il ne la fait monter (9 montent, 13 descendent ; 7 et 20 à l'étape 3). Il met cependant plus de vraies estampes au rang 1 (13 contre 10).
- *Bataille au coutelas* : inchangée par rapport à l'étape 3 (aucune requête dans les 20 premières, donc SegSwap n'intervient pas).
- Source absente : scores de la vraie estampe 0,4-29,8 ; de la meilleure fausse quand la vraie est retirée 1,0-26,3. Toujours indiscernables.

## Où en est la mise au point

C'est la meilleure chaîne mesurée : 13 requêtes sur 58 au rang 1 et 29 dans les 10 premières, contre 8 et 20 pour la base. Mais aucun test préinscrit ne la valide sur les requêtes de mise au point, qui ont désormais servi à cinq choix successifs. Les 105 requêtes d'évaluation restent fermées.
