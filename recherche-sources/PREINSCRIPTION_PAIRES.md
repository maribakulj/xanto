# Agrandissement du jeu de paires figure peinte / estampe source (règle écrite avant annotation et avant tout calcul)

Date : 14/10/2026. Motif (`RESULTAT_CANAUX.md`) : avec 19 requêtes de mise au point, aucun écart de moins de 6 requêtes ne peut passer nos règles, et l'étape 7 du plan (paires synthétiques, apprentissage) demande au moins 100 paires réelles pour juger. Nous en avions 49.

## Tirage (`selection_requetes2.py`, sortie `requetes2.csv`)

- Candidats : les emprunts du catalogue de Rovigo dont l'estampe source a une épreuve dans `data/estampes_sources.csv` (les 28 estampes déjà dans la galerie) et dont le plat a une photographie, **en excluant les plats déjà tirés** pour les 54 premières requêtes.
- **Au plus 8 nouvelles requêtes par estampe**, tirées au sort (graine 15102026), un même plat au plus une fois par estampe. Résultat : **114 nouvelles requêtes** (Q055 à Q168), sur 75 plats et 23 estampes.
- Un même plat peut servir pour deux estampes différentes (deux figures différentes du même plat) ; il peut alors se trouver dans les deux lots. On le signale, sans l'exclure : les figures encadrées sont différentes.

## Lots (le partage par estampe est conservé)

- Chaque nouvelle requête va dans le lot de son estampe (`lots.csv`). L'estampe 26/23, dont aucune des requêtes du premier tirage n'était utilisable, va au lot d'évaluation.
- **40 nouvelles requêtes de mise au point** (total prévu 59) et **74 d'évaluation** (total prévu 104). Le lot d'évaluation reste fermé.

## Encadrement des figures

- Même consigne que pour les 54 premières (sous-agents annotateurs qui ne voient que la photo du plat et la phrase du catalogue, jamais l'estampe ni le web) : une boîte serrée sur la figure ou le groupe que la phrase dit emprunté ; `trouve` = oui, incertain ou non ; les « non » sont écartés, comme avant.
- Contrôle de fiabilité : 23 requêtes (20 %, tirées avec la graine 15102026 : Q057, Q063, Q067, Q068, Q083, Q102, Q107, Q110, Q112, Q119, Q120, Q122, Q123, Q126, Q132, Q135, Q144, Q150, Q152, Q157, Q163, Q165, Q168) sont encadrées une seconde fois par un annotateur indépendant. On publie l'accord (recouvrement des boîtes, IoU) ; **la boîte retenue reste celle de la première passe**, quel que soit l'accord. (Précision : pour les 54 premières requêtes, chaque requête n'avait été encadrée qu'une fois.)

## Premier usage prévu, règle fixée maintenant

Sur les **seules nouvelles requêtes de mise au point** (jamais vues par aucun essai), on rejoue la comparaison de `PREINSCRIPTION_DINOV3.md` entre AIKON avec DINOv2 (base officielle) et AIKON avec DINOv3 large à 512 px, qui l'avait frôlée sur les 19 premières (net 9, p = 0,064) :

- DINOv3 large **remplace DINOv2** comme base s'il fait monter la vraie estampe **au moins six fois de plus** qu'il ne la fait descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** s'il ne place pas moins de requêtes dans les 50 premières ;
- comme plusieurs requêtes partagent une même estampe, on publie aussi le même test **agrégé par estampe** (une voix par estampe, signe de la somme des écarts de rang en log), à titre de contrôle ; le verdict reste celui de la règle ci-dessus.

On publie aussi les chiffres sur les 59 requêtes de mise au point réunies, à titre descriptif.
