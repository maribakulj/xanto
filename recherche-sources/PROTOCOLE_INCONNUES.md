# Chercher des sources encore inconnues (protocole écrit avant calcul)

Date : 17/10/2026. Outil : la chaîne retenue par l'évaluation finale (`RESULTAT_EVALUATION.md`), sans aucune modification de réglage (`chercher.py`, copie de `regions.py` en mode `RECLASSE=region`, qui garde les 10 premières estampes au lieu de calculer un rang).

Ce n'est pas un test : personne ne connaît la réponse. Il s'agit de proposer à un regard humain des rapprochements à vérifier. On fixe d'avance comment les juger, pour ne pas confondre une ressemblance vague avec un emprunt.

## Plats

Plats du catalogue de Rovigo qui ont une photographie et aucun emprunt à une estampe de la série Bartsch (`inconnues_detection.py`) :

- **sans source citée** (19 plats) : la fiche ne nomme aucune estampe ;
- **« invention » de Xanto** (4 plats : 383, 1347, 1179, 709) : la fiche dit que les figures ne viennent d'aucune estampe ; un rapprochement solide contredirait la fiche ;
- **témoins** (6 plats : 942, 1103, 1144, 629, 435, 466) : la fiche nomme l'estampe mais pas son numéro Bartsch. Si cette estampe est dans la galerie, l'outil devrait la proposer : c'est un contrôle de bon fonctionnement sur des plats neufs, pas une découverte.

Retirés après la planche de contrôle des découpes, avant tout calcul de rang : 315 (salière, sans figure) et 1175 (décor sans scène). Pour 499, la première photo est le revers ; on prend la vue du recto.

## Requêtes

Pour chaque plat : la scène entière et jusqu'à 5 figures humaines détectées automatiquement (Grounding DINO, invite « person », seuil 0,30, petit côté ≥ 8 % de la photo, les plus grandes d'abord). Aucune boîte n'est retouchée à la main.

## Jugement (humain, sur une page privée)

Pour chaque requête, les 10 premières estampes sont montrées à côté de la figure, avec la région qui a fait remonter l'estampe et le sens (endroit ou miroir). Le juge coche :

- **oui** : même figure, avec la même pose et les mêmes membres placés de la même façon, et au moins un détail non nécessaire repris (draperie, attribut, raccourci, position d'un doigt ou d'un pied) ;
- **peut-être** : même pose générale, sans détail probant ;
- **non** : autre chose.

Un « oui » n'est retenu comme proposition d'emprunt qu'après une vérification par un historien de l'art (l'auteur du catalogue de Rovigo ou un spécialiste de Xanto). Les « oui » confirmés deviendront de nouvelles paires pour juger les méthodes futures.

## Témoins

On publiera combien de témoins voient leur estampe parmi les 10 premières, si elle est dans la galerie (vérifié à la main d'après le titre de la fiche, après calcul).

## Confidentialité

Les photographies des plats et les recadrages restent en privé (Drive). Seuls ce protocole, les scripts et, après vérification, les rapprochements confirmés sont publiés.
