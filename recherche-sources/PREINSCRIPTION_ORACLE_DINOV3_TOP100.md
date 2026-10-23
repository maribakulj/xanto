# Oracle avec DINOv3 et reclassement de 100 candidats (règles écrites avant calcul)

Date : 23/10/2026, avant tout calcul. Motif : la chaîne retenue (`RESULTAT_EVALUATION.md`) ne reclasse que les 20 premières estampes de la présélection. Sur les 105 requêtes d'évaluation, la bonne estampe y figure 47 fois ; elle figure 74 fois parmi les 100 premières. Le reclassement ne peut donc pas dépasser 47 sur 105 dans les 10 premières. Par ailleurs, l'oracle du 14/10 n'a été fait qu'avec DINOv2.

## Test 1 : oracle avec DINOv3 (diagnostic)

- Même protocole que `PREINSCRIPTION_ORACLE.md` : mêmes 49 requêtes, mêmes découpes oracle, mêmes découpes témoins (Grounding DINO, 6 956 figures), même mesure (rang de la découpe oracle parmi toutes les découpes, meilleur des deux sens de la figure du plat).
- Seuls les vecteurs changent : ceux de la chaîne retenue (DINOv3-L, vecteur de classe, découpe complétée en carré par le gris moyen, 384 px, couleur). Script : `oracle_dinov3.py`.
- Règle : si la découpe oracle est dans les 10 premières pour **au moins 25 requêtes sur 49**, le problème principal est la localisation de la figure dans l'estampe (priorité aux régions). Sinon, le vecteur de classe de DINOv3 ne relie pas assez la figure peinte à la figure gravée (priorité aux correspondances de détails ou à l'apprentissage).
- Ce test utilise des requêtes des deux lots ; il ne choisit aucun réglage de la chaîne.

## Test 2 : reclasser 100 candidats au lieu de 20

- Chaîne retenue inchangée (`regions.py`, `RECLASSE=region`), sauf le nombre d'estampes reclassées par SegSwap : 100 au lieu de 20 (variable `TOPK=100`). Les mêmes caches de vecteurs sont utilisés.
- Lot : les **58 requêtes de mise au point** seulement.
- Comparaison requête par requête avec la chaîne retenue sur ce lot (`resultats/regions_reclasse_region_mise_au_point58.csv`, rang final) :
  - la variante **gagne** si elle fait monter la vraie estampe **au moins six fois de plus** qu'elle ne la fait descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** si elle ne place pas moins de requêtes dans les 10 premières ;
  - publiés sans valeur de verdict : rang 1, 10 premières, 50 premières, rang médian ; le test par estampe ; le plafond (requêtes dont la vraie estampe est parmi les 100 premières de la présélection) ; le test « source absente ».
- Le lot d'évaluation de 105 requêtes est consommé. Si la variante gagne, elle ne sera confirmée que sur un **nouveau lot fermé** (paires tirées d'estampes jamais utilisées), constitué avant son calcul.
