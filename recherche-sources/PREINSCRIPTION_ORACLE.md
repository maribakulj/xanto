# Test de l'oracle : l'échec vient-il de la taille de la figure ou du changement de médium ? (règle écrite avant calcul)

Date : 14/10/2026, avant tout calcul. Étape 0 du plan de `reports/Vision et sources gravées.md` (revue de littérature, privée).

## Principe

Dans l'essai de recherche de sources, la vraie estampe n'arrivait parmi les 50 premières que pour 11 requêtes sur 49. Deux causes possibles : (a) **l'échelle** — la petite figure se noie dans la grande estampe résumée par quelques vecteurs ; (b) **le médium** — la figure peinte et la figure gravée ne se ressemblent pas assez pour le modèle. On supprime la cause (a) en découpant à la main, dans la vraie estampe, la figure que le catalogue désigne, et on regarde si la figure du plat la retrouve parmi d'autres figures découpées.

## Protocole (fixé)

- **Requêtes** : les 49 figures déjà encadrées sur les plats (`requetes_boites.csv`), chacune aussi en miroir (on garde la meilleure des deux).
- **Découpe oracle** : pour chaque requête, un annotateur voit la figure du plat et une épreuve de la vraie estampe (Rijksmuseum de préférence), et encadre dans l'estampe la figure (ou le groupe, ou la composition) correspondante. S'il ne la trouve pas, la requête est notée « introuvable » et comptée comme échec.
- **Découpes témoins** : toutes les figures humaines détectées automatiquement (Grounding DINO, invite « person », seuil fixé à 0,30) dans les 1 604 images de la galerie, y compris les autres figures des vraies estampes ; une découpe témoin qui recouvre la découpe oracle (IoU > 0,5) est retirée.
- **Vecteurs** : exactement ceux de l'essai (DINOv2-base, niveaux de gris, redimensionnement à 224 px), une découpe = un vecteur.
- **Mesure** : rang de la découpe oracle parmi toutes les découpes.

## Règle de décision

- **Échelle** : la découpe oracle est dans les 10 premières pour **au moins la moitié** des requêtes (≥ 25 sur 49). Priorité à l'indexation des estampes par régions (étape 3 du plan).
- **Médium** : moins de 25 sur 49. Priorité aux transformations d'images et aux paires synthétiques (étapes 4 et 7).
- On publiera aussi le rappel à 1 et à 50, et le nombre de découpes témoins.

Ce test est un **diagnostic** : il ne choisit aucun réglage, il oriente l'ordre des étapes suivantes. Toutes les 49 requêtes y servent ; le partage entre lot de mise au point et lot d'évaluation sera fait avant l'étape 1 (AIKON).
