# Étape 1 du plan : AIKON tel quel (règle écrite avant calcul)

Date : 14/10/2026, avant tout calcul. Plan : `reports/Vision et sources gravées.md` (privé), étape 1. Le test de l'oracle (`RESULTAT_ORACLE.md`) a conclu « médium » : le vecteur global ne relie pas peinture et gravure ; l'appariement de détails (ici SegSwap, appris sur des paires dont le style a été changé) est la piste à éprouver.

## Lots (fixés une fois pour toutes, `lots.csv`)

Les 49 requêtes sont coupées **par estampe source** (27 estampes) : ordre des estampes tiré avec la graine 14102026, puis lot de mise au point rempli jusqu'à 19 requêtes ; le reste (30 requêtes) forme le lot d'évaluation. **Le lot d'évaluation n'est pas calculé à cette étape** ; il ne sera ouvert qu'une fois, pour la chaîne finale. (Le test de l'oracle, simple diagnostic, avait utilisé les 49 requêtes.)

Lot de mise au point : Q01, Q02, Q07, Q08, Q09, Q13, Q14, Q21, Q22, Q28, Q29, Q32, Q33, Q46, Q47, Q51, Q52, Q53, Q54.

## Méthode (reprise du code d'AIKON, `Aikon-platform/aikon-api`, module `similarity`, réglages par défaut)

- **Présélection** : DINOv2 ViT-B/14 (`torch.hub`, `facebookresearch/dinov2`), vecteur de classe normalisé, image en couleur redimensionnée à 224 × 224 (sans garder les proportions, comme AIKON), normalisation ImageNet. Requête = la figure encadrée sur le plat (`requetes_boites.csv`), à l'endroit et en miroir (option « transpositions » d'AIKON) ; on garde le meilleur des deux sens. Galerie = les 1 604 images entières. Cosinus, **20 premières**.
- **Reclassement** : SegSwap, poids `hard_mining_neg5.pth` du dépôt d'origine (`XiSHEN0220/SegSwap`, MIT), images à 244 × 244, score « correspondances locales pondérées par le masque cohérent » d'AIKON ; dans le sens (endroit ou miroir) retenu par la présélection. Les 20 candidates sont reclassées par ce score ; les suivantes gardent l'ordre du cosinus.
- Une épreuve de la bonne estampe compte comme réussite (comme le 13/10).

## Mesures et règle

- Sur les 19 requêtes : rang de la première épreuve de la bonne estampe ; présence dans les 10 et les 50 premières ; rang médian ; sens gagnant (endroit / miroir).
- **Comparaison** avec notre reclassement du 13/10 (étape 2, `resultats/etape2.csv`), requête par requête.
- **Règle** (plan, étape 1) : AIKON devient la base si, sur les 19 requêtes, il fait monter la vraie estampe **au moins aussi souvent** qu'il la fait descendre par rapport à notre étape 2 (égalités exclues) **et** place au moins autant de requêtes dans les 10 premières. Sinon on garde notre base.
- **Test « source absente »** : pour chaque requête, on retire toutes les épreuves de la vraie estampe et on note le score SegSwap du meilleur candidat restant ; on publie la distribution à côté des scores des vraies sources trouvées.
