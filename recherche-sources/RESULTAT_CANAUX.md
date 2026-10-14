# Étape 4 du plan, transformer les images (gris, flou, trait, fusion) : résultat

14/10/2026. Règle écrite avant calcul : `PREINSCRIPTION_CANAUX.md`. Script : `aikon.py` (paramètre canal). Résultats par requête : `resultats/canal_<modèle>_<canal>_mise_au_point.csv`. Lot de mise au point (19 requêtes).

## Verdict selon la règle : **aucun canal ne gagne**, ni avec DINOv2 (verdict officiel) ni avec DINOv3 large (exploratoire)

| Variante | Rang 1 | 10 premières | 50 premières | Rang médian | Monte / descend (vs couleur, même modèle) | Test du signe | Sorties des 50 premières |
|---|---|---|---|---|---|---|---|
| DINOv2, couleur (base) | 1 | 4 | 7 | 175 | — | — | — |
| DINOv2, gris | 1 | 2 | 8 | 176 | 9 / 10 | p = 1 | 0 |
| DINOv2, flou | 1 | 2 | 8 | 127 | 9 / 10 | p = 1 | 0 |
| DINOv2, trait | 1 | 1 | 7 | 136 | 8 / 11 | p = 0,65 | 3 |
| DINOv2, fusion | 1 | 2 | 8 | 119 | 8 / 10 | p = 0,82 | 0 |
| DINOv3 large, couleur | 5 | 9 | 12 | 29 | — | — | — |
| DINOv3 large, gris | 5 | **10** | 12 | 10 | 5 / 7 | p = 0,77 | 0 |
| DINOv3 large, flou | 3 | 8 | 11 | 41 | 4 / 11 | p = 0,12 | 1 |
| DINOv3 large, trait | 1 | 4 | 9 | 57 | 2 / 15 | **p = 0,002 (pire)** | 4 |
| DINOv3 large, fusion | 3 | 9 | 11 | 30 | 4 / 11 | p = 0,12 | 1 |

## Ce que cela veut dire

- **Des transformations faites à la main ne comblent pas l'écart entre peinture et gravure.** Retirer la couleur ne change à peu près rien (les modèles y sont déjà peu sensibles). Flouter les hachures de la gravure ne rapproche pas. Le **dessin au trait fait nettement pire** avec DINOv3 large (15 requêtes descendent, 2 montent, p = 0,002) : en réduisant les deux images à leurs contours, on perd ce qui permettait de les relier.
- La seule variante qui ajoute une requête dans les 10 premières (DINOv3 large en gris, 10 sur 19) fait descendre plus de requêtes qu'elle n'en fait monter : ce n'est pas un gain.
- La fusion des quatre canaux ne fait pas mieux que la couleur seule.
- **Test « source absente »** : comme aux étapes précédentes, les scores des meilleurs candidats sans source recouvrent ceux des vraies sources, pour toutes les variantes.

## Conséquences pour la suite du plan

- Le test de l'oracle avait orienté vers les transformations (étape 4) et les paires d'apprentissage (étape 7). L'étape 4 est fermée. L'étape 7 exige, d'après le plan, **au moins 100 paires réelles** pour juger un apprentissage : nous n'en avons que 49 (dont 19 de mise au point). Le premier besoin est donc **d'agrandir le jeu de paires** (fiches de Rovigo citant une estampe Bartsch dont une épreuve est dans la galerie).
- Avec 19 requêtes, aucune différence de moins de six requêtes ne peut passer la règle : c'est aussi pour cela qu'il faut plus de paires.

## Écarts à signaler

- Premier lancement interrompu par une erreur de ma ligne de commande (modèle et taille passés en un seul argument) : rien n'avait été calculé ; relancé à l'identique.
- La règle a été enregistrée dans le dépôt local avant tout calcul ; son envoi sur GitHub a été retardé par une panne du serveur (erreur 500) et fait pendant le calcul.
