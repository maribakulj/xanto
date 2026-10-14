# Agrandissement du jeu de paires et nouveau test DINOv3 large : résultat

14/10/2026. Règle écrite avant annotation et avant calcul : `PREINSCRIPTION_PAIRES.md` (avec son amendement). Scripts : `selection_requetes2.py`, `assembler.py`, `accord_boites.py`, `aikon.py`, `comparer.py`. Le lot d'évaluation n'a pas été calculé.

## Le jeu de paires

- **114 nouvelles requêtes** tirées (Q055-Q168), en plus des 54 du premier tirage ; les 168 ont été **réencadrées** à partir du commentaire complet des fiches de Rovigo (la phrase utilisée jusqu'ici était tronquée à 300 caractères et, pour 70 requêtes sur 168, ne citait même pas l'estampe).
- Résultat : 138 figures trouvées, 25 incertaines, 5 introuvables (photo illisible ou ne montrant pas le plat décrit) ; **163 paires utilisables** contre 49 avant.
- Lots (partage par estampe conservé) : **58 requêtes de mise au point** (sur 10 estampes) et **105 d'évaluation**, qui reste fermé. Quatre anciennes requêtes jugées introuvables avec la phrase tronquée sont récupérées et rangées dans le lot de leur estampe (Q10 en mise au point ; Q05, Q19, Q20 en évaluation) ; Q49 est perdue (photo qui ne correspond pas à la fiche).
- **Accord entre annotateurs** (23 requêtes encadrées deux fois, `resultats/accord_controle.txt`) : IoU médian 0,88 ; 22 sur 23 au-dessus de 0,5 ; une seule figure différente (Q157, deux Daphné possibles). Même jugement « trouvé / incertain » pour les 23.
- **Anciennes et nouvelles boîtes** des 54 premières requêtes (`resultats/accord_anciennes_boites.txt`) : IoU médian 0,81, mais **5 figures différentes** (Q05, Q08, Q14, Q34, Q49), dont deux du lot de mise au point (Q08, Q14). Les résultats publiés avant ce jour reposaient sur les anciennes boîtes ; ils restent tels quels.
- Rappel : les annotateurs sont des instances du même modèle ; leur accord mesure la stabilité de la consigne, pas une indépendance humaine.

## Test préinscrit : DINOv3 large contre DINOv2, sur les 38 nouvelles requêtes de mise au point

| 38 requêtes jamais vues | Rang 1 | 10 premières | 50 premières | Rang médian |
|---|---|---|---|---|
| AIKON avec DINOv2 (base) | 3 | 5 | 7 | 290 |
| **AIKON avec DINOv3 large, 512 px** | 2 | **12** | **18** | **63** |

- DINOv3 large fait monter la vraie estampe **29 fois** et descendre **8 fois** (net 21, **p = 0,001**) et place plus de requêtes dans les 50 premières : **la règle est remplie, DINOv3 large remplace DINOv2 comme base.**
- Contrôle par estampe : ces 38 requêtes ne portent que sur 7 estampes ; DINOv3 gagne pour 6, perd pour 1 (p = 0,125, non significatif avec 7 voix). **L'estampe perdante, 26/211** (*Bataille au coutelas*, attribuée à Marco Dente), voit 6 de ses 7 requêtes descendre : le gain n'est pas universel.
- Descriptif, 58 requêtes de mise au point réunies (nouvelles boîtes) : DINOv2 5 / 7 / 14, médiane 291 ; **DINOv3 large 8 / 20 / 31** dans le premier rang, les 10 et les 50 premières, médiane 39 ; 44 montées contre 11 descentes ; par estampe 9 sur 10.
- Ce gain confirme sur des requêtes neuves ce que les 19 premières laissaient voir (net 9, p = 0,064).

## Ce qui ne change pas

- **Source absente** : le score SegSwap de la meilleure candidate quand la vraie estampe est retirée (3,1 à 15,5) recouvre toujours celui des vraies estampes trouvées (1,7 à 21,5). Aucune méthode ne sait encore dire « la source n'est pas dans la base ».
- Le lot d'évaluation (105 requêtes) n'a pas été ouvert. Il servira une seule fois, pour la chaîne finale.

## Suite

Avec 58 requêtes de mise au point, une différence de quelques requêtes devient mesurable. Les essais suivants partent de DINOv3 large : régions côté estampe (étape 3), reclassement par correspondances (étape 5), fusion avec notre recherche locale du 13/10, qui ne trouvait pas les mêmes requêtes.
