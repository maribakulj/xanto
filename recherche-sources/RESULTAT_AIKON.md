# Étape 1 du plan, AIKON tel quel : résultat

14/10/2026. Règle écrite avant calcul : `PREINSCRIPTION_AIKON.md`. Script : `aikon.py`. Résultats par requête : `resultats/aikon_mise_au_point.csv`. Lot de mise au point seulement (19 requêtes, `lots.csv`) ; le lot d'évaluation n'a pas été calculé.

## Verdict selon la règle : **AIKON devient la base**, de justesse

| Lot de mise au point (19 requêtes) | Rang 1 | 10 premières | 50 premières | Rang médian |
|---|---|---|---|---|
| Notre étape 2 du 13/10 (fenêtres DINOv2 + détails cohérents) | 3 | 4 | 7 | 176 |
| **AIKON** (DINOv2 sur l'image entière, 20 premières reclassées par SegSwap) | 1 | 4 | 7 | 175 |

- AIKON fait monter la vraie estampe pour **13 requêtes** et descendre pour **5** (une égalité) ; il place autant de requêtes dans les 10 premières (4). La règle (« au moins aussi souvent monter que descendre, et au moins autant dans les 10 premières ») est remplie. Au test du signe, la différence n'est pas significative (p = 0,10) : AIKON n'est **pas meilleur**, il n'est **pas moins bon**, et il devient la base parce que c'est une chaîne publiée et reproductible.
- **Les gains sont surtout loin dans la liste** (par exemple du rang 945 au rang 550) : ils ne changent rien en pratique.
- **Les deux méthodes ne trouvent pas les mêmes requêtes.** Dans les 10 premières : AIKON Q01, Q09, Q29, Q32 ; notre étape 2 Q09, Q21, Q22, Q32. Ensemble, 6 sur 19. C'est ce que la littérature récente décrit (une recherche globale et une recherche locale retrouvent des images correctes en nombre comparable, mais pas les mêmes).

## Ce que fait SegSwap ici

- Sur les 6 requêtes dont la vraie estampe était parmi les 20 candidates, SegSwap la fait monter 3 fois (Q01 11 → 7, Q09 4 → 1, Q29 15 → 3) et descendre 3 fois (Q13 4 → 18, Q14 12 → 14, Q32 1 → 2). Le reclassement appris par SegSwap, tel qu'il est réglé dans AIKON (images écrasées en 244 × 244), n'apporte pas de gain net sur nos paires peinture/gravure.
- **Test « source absente »** : quand on retire la vraie estampe, le meilleur candidat restant obtient un score de 3,6 à 12,7 ; les vraies estampes retrouvées obtiennent 1,5 à 14,0. Les deux plages se recouvrent entièrement : **le score SegSwap ne permet pas de dire si la source est dans la base**. Seule la composition entière (Q09, *Enlèvement d'Hélène*, 14,0) dépasse presque tous les scores sans source.
- Sens : la présélection retient le miroir pour 5 des 6 requêtes trouvées dans les 20 premières, ce qui ne vaut pas preuve d'inversion (le vecteur global est peu sensible au sens).

## Écarts à signaler

- Le vecteur DINOv2 est pris dans la version Hugging Face (`facebook/dinov2-base`, mêmes poids que `torch.hub dinov2_vitb14` utilisé par AIKON).
- Comme annoncé dans la règle, SegSwap compare la requête dans le sens retenu par la présélection (AIKON l'applique sans transposition).
- Le code de SegSwap (licence MIT) a été adapté pour tourner hors carte Nvidia (masques créés sur le processeur courant, même calcul). Calcul local sur le Mac, environ 5 minutes.

## Limites

19 requêtes : une différence de deux ou trois requêtes n'est pas interprétable. Les chiffres du lot de mise au point servent à choisir l'ordre des essais, pas à juger la méthode, qui le sera une seule fois sur les 30 requêtes du lot d'évaluation.
