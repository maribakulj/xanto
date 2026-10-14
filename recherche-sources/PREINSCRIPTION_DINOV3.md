# Étape 2 du plan : DINOv3 à la place de DINOv2 dans la présélection (règle écrite avant calcul)

Date : 14/10/2026, avant tout calcul DINOv3, après le résultat de l'étape AIKON (`RESULTAT_AIKON.md`), qui devient la base.

## Méthode

Chaîne AIKON inchangée (`aikon.py`), sauf le modèle et la taille de la présélection :

- **A** : DINOv3 ViT-B/16 (`facebook/dinov3-vitb16-pretrain-lvd1689m`), images (figure du plat et estampes entières) redimensionnées à **512 × 512** ;
- **B** : DINOv3 ViT-L/16 (`facebook/dinov3-vitl16-pretrain-lvd1689m`), même taille.

Vecteur de classe normalisé, requête à l'endroit et en miroir, 20 premières reclassées par SegSwap exactement comme dans la base. Lot de mise au point seulement (19 requêtes) ; le lot d'évaluation n'est pas calculé.

## Règle (cadre du plan)

Comparaison requête par requête avec la base (AIKON avec DINOv2, `resultats/aikon_mise_au_point.csv`) sur le rang final de la vraie estampe :

- une variante **gagne** si elle fait monter la vraie estampe **au moins six fois de plus** qu'elle ne la fait descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** si elle ne place pas moins de requêtes dans les 50 premières ;
- si A et B gagnent toutes deux, on retient celle qui place le plus de requêtes dans les 50 premières (à égalité, A, plus légère) ;
- si aucune ne gagne, on garde DINOv2 (licence plus simple).

On publie aussi le rang 1, les 10 premières, le rang médian et le test « source absente », quel que soit le verdict.
