# Évaluation finale : résultat (règle : `PREINSCRIPTION_EVALUATION.md`)

Date : 17/10/2026. Calcul unique, en local, sur les 105 requêtes du lot d'évaluation (18 estampes jamais utilisées pour la mise au point). Code inchangé depuis le commit a9bb8a7. Données : `resultats/evaluation_base_dinov3_large.csv`, `resultats/evaluation_candidate_regions.csv`.

## Verdict préinscrit : la candidate est retenue

| 105 requêtes, galerie de 1 604 images | rang 1 | 10 premières | 50 premières | rang médian |
|---|---|---|---|---|
| base (image entière + SegSwap sur l'estampe entière) | 5 (2-11 %) | 14 (8-21 %) | 27 (18-35 %) | 195 |
| **candidate (régions + SegSwap sur la région gagnante)** | **22 (14-30 %)** | **40 (29-48 %)** | **61 (49-67 %)** | **34** |

Entre parenthèses : intervalle de Wilson à 95 %. La vraie estampe monte 85 fois et descend 15 fois : net 70, p = 5 × 10⁻¹³ au test du signe ; 61 requêtes dans les 50 premières contre 27. Les trois conditions sont remplies : **la chaîne « régions + SegSwap sur la région » devient la chaîne de référence.**

## Descriptif (sans verdict)

- **Par estampe** (une voix par estampe) : 13 montent, 5 descendent, p = 0,096. Les requêtes d'une même estampe ne sont pas indépendantes : le p par requête surestime la solidité du gain. Le gain est large mais pas universel. Il est très net sur 26/104, 26/21, 26/245, 26/247, 27/352 (toutes les requêtes montent) ; il y a un recul sur 28/44 (3 descentes sur 4), 28/4 et 27/442.
- **Optimisme de la mise au point** : la candidate passe de 50 % des requêtes dans les 10 premières (29/58) à 38 % (40/105) ; la base de 34 % (20/58) à 13 % (14/105). Les estampes du lot d'évaluation sont plus difficiles pour les deux chaînes, mais l'écart entre elles est plus grand qu'en mise au point.
- **Rôle de SegSwap** : avant reclassement, la présélection de la candidate donne déjà 17 / 40 / 61. SegSwap sur la région porte le rang 1 de 17 à 22 sans changer les 10 et 50 premières. Dans la base, SegSwap n'apporte rien (5 / 15 / 27 avant, 5 / 14 / 27 après).
- **Grandes pertes** (plus de 50 rangs) : 9 requêtes, dont Q107 (2 → 119), Q152 (73 → 260), Q17 (46 → 157), Q129 (80 → 299).
- **Source absente** : scores SegSwap de la vraie estampe 0,06-37,1 ; de la meilleure fausse quand la vraie est retirée 1,4-33,4. Toujours indiscernables. Le système classe mieux, mais il ne sait pas dire « la source n'est pas dans la collection » : un humain doit regarder les premiers rangs.

## Ce que cela veut dire

Pour une figure de plat de Xanto et une galerie de 1 604 estampes, la chaîne retenue place la vraie source **au premier rang une fois sur cinq**, **dans les 10 premières un peu plus d'une fois sur trois**, **dans les 50 premières environ trois fois sur cinq**. C'est un outil de tri pour un historien, pas un système d'attribution automatique.

Le lot d'évaluation est désormais consommé : toute amélioration ultérieure devra être jugée sur des paires nouvelles.
