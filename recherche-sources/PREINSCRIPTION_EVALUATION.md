# Évaluation finale : calcul unique sur le lot d'évaluation (règle écrite avant calcul)

Date : 17/10/2026. Décision de Marcel (17/10) : figer la meilleure chaîne de la mise au point et l'évaluer **une seule fois** sur le lot fermé. Aucune requête de ce lot n'a été passée dans un calcul de rang à ce jour.

## Lot

Les **105 requêtes** du lot `evaluation` de `lots.csv` qui ont une boîte utilisable (`requetes_boites.csv`, boîtes réencadrées sur le commentaire complet, `PREINSCRIPTION_PAIRES.md` et son amendement). Elles viennent d'estampes qui n'ont jamais servi à la mise au point (partage par estampe). Galerie inchangée : 1 604 images.

## Les deux chaînes, figées

- **Base** : AIKON avec DINOv3 large, image entière réduite à 512 px, 20 premières reclassées par SegSwap sur l'estampe entière (`aikon.py <privé> <segswap> evaluation facebook/dinov3-vitl16-pretrain-lvd1689m 512`), comme dans `RESULTAT_PAIRES.md`.
- **Candidate** : présélection = max(base, meilleure région parmi la grille 2×2 et 3×3 et les boîtes « personne » agrandies de 10 %, en carré gris, 384 px), figure à l'endroit et en miroir ; 20 premières reclassées par SegSwap sur la région gagnante (`RECLASSE=region regions.py <privé> <segswap> evaluation`), comme dans `RESULTAT_RECLASSEMENT_REGION.md`. Code au commit a9bb8a7, sans aucune modification.

## Règle

Comparaison requête par requête (rang final de la vraie estampe parmi 1 604) :

- la candidate **est retenue** si elle fait monter la vraie estampe **au moins six fois de plus** qu'elle ne la fait descendre, avec **p < 0,05** au test du signe exact bilatéral (égalités exclues), **et** si elle ne place pas moins de requêtes dans les 50 premières ;
- sinon, **la base reste la chaîne de référence**. Si la candidate fait significativement pire (p < 0,05 dans l'autre sens), on le dira comme tel.

Publiés quel que soit le verdict, sans valeur de verdict :

- pour chaque chaîne : rang 1, 10 et 50 premières (avec intervalle de Wilson à 95 %), rang médian ;
- le même test agrégé par estampe (une voix par estampe) ;
- le test « source absente » (scores SegSwap de la vraie estampe et de la meilleure fausse quand la vraie est retirée) ;
- la comparaison avec les chiffres de mise au point (13/58 et 29/58 pour la candidate ; 8/58 et 20/58 pour la base), pour mesurer l'optimisme dû aux réglages.

## Après

Le lot d'évaluation est alors **consommé** : toute méthode nouvelle devra être jugée sur des paires nouvelles, tirées et encadrées avant calcul. Aucun réglage ne sera fait, ni aucun calcul relancé sur ce lot, après avoir vu un rang ; une erreur technique qui empêcherait le calcul (plantage, fichier manquant) sera corrigée et signalée ici.
