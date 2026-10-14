# Étape 4 du plan : transformer les images pour rapprocher peinture et gravure (règle écrite avant calcul)

Date : 14/10/2026, avant tout calcul de rang. Le test de l'oracle a conclu « médium » (`RESULTAT_ORACLE.md`) : la priorité va aux transformations d'images. Base officielle : AIKON avec DINOv2 (`RESULTAT_AIKON.md`, `RESULTAT_DINOV3.md`). Marcel a validé le 14/10 de mener en parallèle, à titre exploratoire, les mêmes essais avec DINOv3 large (512 px), qui a frôlé la règle à l'étape 2 ; le choix entre les deux bases se fera par une règle écrite avant l'unique calcul sur le lot d'évaluation.

## Canaux (n'agissent que sur la présélection ; SegSwap reclasse ensuite les 20 premières en couleur, comme dans la base)

Appliqués après redimensionnement à la taille du modèle (224 px pour DINOv2, 512 px pour DINOv3 large), réglages fixés d'avance (`aikon.py`, fonctions `prep` et `xdog`) :

- **gris** : figure du plat et estampes en niveaux de gris (la couleur du plat disparaît) ;
- **flou** : niveaux de gris des deux côtés, et flou gaussien de rayon taille/256 sur les estampes seulement (les tailles et hachures de la gravure sont gommées, pour ressembler aux aplats peints) ;
- **trait** : dessin au trait des deux côtés (XDoG : sigma = max(0,7 ; taille/512), k = 1,6, tau = 0,98, eps = 0, phi = 200) ;
- **fusion** : fusion des rangs des quatre canaux (couleur, gris, flou, trait) par la formule 1/(60 + rang) ; le sens (endroit/miroir) est celui du canal couleur.

Une seule vérification visuelle a été faite avant calcul (Q29 et son estampe, pour s'assurer que le trait et le flou produisent bien ce qui est décrit) ; aucun réglage n'a été modifié ensuite.

## Règle (cadre du plan, étape 4)

Pour chaque modèle séparément, chaque canal est comparé, requête par requête sur les 19 requêtes de mise au point, au canal couleur du même modèle (rang final de la vraie estampe) :

- un canal **gagne** s'il fait monter la vraie estampe **au moins six fois de plus** qu'il ne la fait descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** s'il ne fait pas sortir des 50 premières **plus de deux** requêtes qui y étaient ;
- si plusieurs canaux gagnent pour un même modèle, on retient celui qui place le plus de requêtes dans les 50 premières (à égalité, le plus simple : gris, puis flou, trait, fusion) ;
- quatre canaux étant testés par modèle, on signalera aussi si un gain survit à la correction de Holm (seuils 0,0125 ; 0,0167 ; 0,025 ; 0,05).

Le verdict officiel porte sur DINOv2 ; celui sur DINOv3 large est exploratoire. On publie pour chaque variante le rang 1, les 10 et 50 premières, le rang médian et le test « source absente ».
