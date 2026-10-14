# Étape 2 du plan, DINOv3 dans la présélection : résultat

14/10/2026. Règle écrite avant calcul : `PREINSCRIPTION_DINOV3.md`. Script : `aikon.py` (modèle et taille en paramètres). Résultats par requête : `resultats/dinov3_base_mise_au_point.csv`, `resultats/dinov3_large_mise_au_point.csv`. Lot de mise au point (19 requêtes) seulement.

## Verdict selon la règle : **aucune variante ne gagne ; on garde DINOv2** — mais de très peu pour DINOv3 large

| Lot de mise au point (19 requêtes) | Rang 1 | 10 premières | 50 premières | Rang médian | Monte / descend (vs base) | Test du signe |
|---|---|---|---|---|---|---|
| Base : AIKON, DINOv2-B, 224 px | 1 | 4 | 7 | 175 | — | — |
| A : DINOv3-B/16, 512 px | 3 | 5 | 7 | 129 | 12 / 7 (net 5) | p = 0,36 |
| **B : DINOv3-L/16, 512 px** | **5** | **9** | **12** | **29** | **14 / 5 (net 9)** | **p = 0,064** |

- La règle demandait un solde d'au moins six requêtes **et** p < 0,05. A échoue sur les deux. B remplit le solde (9) et ne perd rien dans les 50 premières (12 contre 7), mais **manque le seuil de significativité** (p = 0,064). Le verdict préinscrit est donc « on garde DINOv2 ».
- Ce verdict tient à 19 requêtes : avec si peu de cas, même un écart de 4 à 9 dans les 10 premières ne passe pas un test exigeant. DINOv3 large est néanmoins, de loin, **le meilleur résultat obtenu jusqu'ici** sur ce lot : la vraie estampe arrive dans les 10 premières pour Q01, Q02, Q07, Q09, Q28, Q29, Q32, Q51, Q53 (dont un groupe et deux compositions, que rien ne retrouvait auparavant).
- Ce que rien ne retrouve encore (rang > 100 pour toutes les variantes) : Q21, Q22, Q33, Q47, Q54, cinq figures isolées.

## Observations hors règle (exploratoires)

- **La présélection seule fait l'essentiel.** Avec le cosinus DINOv3 large sans reclassement : 5 au rang 1, 8 dans les 10 premières, 12 dans les 50. SegSwap ajoute une requête dans les 10 premières mais en fait aussi descendre (Q09 : 1 → 7 ; Q13, Q14 hors des 20 de toute façon).
- **Test « source absente »** : les scores SegSwap des meilleurs candidats quand la vraie estampe est retirée (3,6 à 17,7) recouvrent toujours ceux des vraies estampes trouvées (2,7 à 20,3). Aucun seuil ne sépare « source trouvée » de « pas de source dans la base ».
- La taille 512 px et le modèle changent en même temps entre la base et A/B : on ne sait pas lequel des deux compte le plus.

## Écarts à signaler

Aucun écart à la règle. Calcul local (Mac) : environ 15 minutes pour A, 1 h 15 pour B.
