# Recherche automatique de sources, étape 2 : reclasser en comparant des détails (règle écrite avant calcul)

Date : 13/10/2026, écrite **avant de connaître le résultat de l'étape 1**. Mêmes 49 requêtes, même galerie, même règle de décision que `PREINSCRIPTION.md`.

## Idée

L'étape 1 résume chaque morceau d'image par un seul vecteur. Ici on compare des **détails** : on cherche des petits carrés de l'image (patches) qui se correspondent entre la figure du plat et l'estampe, et on ne garde que ceux qui sont **disposés de la même façon** (une même figure, à une échelle, une rotation et une position près). C'est le principe d'ArtMiner (Shen, Aubry et al. 2019), avec un modèle plus récent.

## Méthode (fixée)

- Candidats : les 50 premières images proposées par l'étape 1 pour chaque requête.
- Vecteurs locaux DINOv2-base (patches de 14 px), niveaux de gris. Requête redimensionnée à 448 px sur son plus grand côté ; estampe à 896 px sur son plus grand côté.
- Paires de patches **mutuellement plus proches voisins** (similarité cosinus) entre la requête et l'estampe.
- Cohérence spatiale : RANSAC sur une similitude (échelle, rotation, translation), 2 000 tirages, graine fixe, seuil d'inlier 1,5 patch dans l'estampe. Le score est le nombre de paires cohérentes. On fait de même avec la requête en miroir et on garde le meilleur.
- Les 50 candidats sont reclassés par ce score (égalités départagées par le rang de l'étape 1) ; les images au-delà de la 50e gardent leur rang.

## Règles

- **Même règle de décision que l'étape 1** sur le rappel à 10 (praticable ≥ 40 % et p < 0,01 contre le hasard ; fermée < 15 % ; partiel entre les deux).
- **L'étape 2 apporte-t-elle quelque chose ?** Oui si elle retrouve dans les 10 premières au moins 5 requêtes de plus que l'étape 1 et que la différence est significative (test de McNemar exact, p < 0,05) ; non sinon.

## Exploratoire (ne compte pas pour la décision)

- MARCO (CVPR 2026, `visinf/MARCO`) : transporter des points de la figure vers l'estampe puis les ramener, et mesurer l'erreur d'aller-retour.
- DINOv3 à la place de DINOv2, si l'accès au modèle (soumis à autorisation sur Hugging Face) est obtenu.
