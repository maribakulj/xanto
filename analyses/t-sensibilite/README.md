# T-sensibilité — les tests chronologiques sans les pièces d'attribution débattue

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches.**

## Question

La période « ≤ 1530 » contient le groupe de Gubbio de 1522-1527, que Mallet donne au jeune Xanto et que Wilson lui refuse (« unable to see Xanto's hand »). Toute différence « début contre fin » peut donc venir de cette attribution, pas d'un changement de pratique. On refait chaque test chronologique sans ces pièces.

## Méthode (`../t_sensibilite.py`)

Les scripts `t_dates`, `t_inversion`, `t_reemploi` et `t_sources_par_piece` sont relancés avec un filtre sur les fiches (`commun.FILTRE`). Trois variantes :

- `complet` : toutes les fiches (374) ;
- `sans_gubbio_1522_1527` : sans les 26 pièces datées avant 1528 ou portant les initiales F.R. (348 pièces). Liste dans `resultats.json` → `exclues` ;
- `sans_gubbio_ni_y_slash` : en plus, sans les pièces marquées y/Ø, marque elle aussi discutée (304 pièces, 70 exclues).

Les sorties complètes de chaque variante sont dans `<variante>/<test>/` ; le résumé dans `resultats.json` → `variantes`.

## Résultats

| Mesure | Complet | Sans Gubbio 1522-1527 | Sans Gubbio ni y/Ø |
|---|---|---|---|
| pièces ≤ 1530 / 1531-1535 / 1536-1542 | 101 / 164 / 101 | 75 / 164 / 101 | 44 / 157 / 101 |
| inversion, dates inscrites (≤ 1530 ; 1531-1535 ; 1536-1542) | 3/15 ; 31/291 ; 18/109 | 2/8 ; 31/291 ; 18/109 | 1/3 ; 31/291 ; 18/109 |
| inversion, p ≤ 1530 vs 1536-1542, dates inscrites | 0,76 | 0,59 | 0,69 |
| inversion, toutes dates (part ≤ 1530 → 1536-1542) | 7,6 % → 15,6 % | 5,5 % → 15,6 % | 7,3 % → 15,6 % |
| inversion, p ≤ 1530 vs 1536-1542, toutes dates | 0,10 | **0,04** | 0,18 |
| réemploi : estampes nouvelles par période | 30 / 18 / 6 | 26 / 19 / 6 | 23 / 21 / 6 |
| réemploi : part tardive vers estampes nouvelles, p (toutes ; inscrites) | 0,006 ; 0,06 | 0,004 ; 0,06 | 0,016 ; 0,04 |
| réemploi : combinaisons déjà vues, p (toutes ; inscrites) | 0,19 ; 0,012 | 0,13 ; 0,007 | 0,12 ; 0,009 |
| estampes par pièce si source (par période) | 1,76 / 2,47 / 1,93 | 1,83 / 2,47 / 1,93 | 1,97 / 2,46 / 1,93 |
| estampes par pièce, p 1531-1535 vs 1536-1542 | 0,002 | 0,002 | 0,002 |

## Ce que cela change

**Les conclusions ne changent pas.**

- Inversion : avec les dates inscrites (le résultat principal), il n'y a de tendance dans aucune variante. La série « toutes dates » passe sous 0,05 quand on retire le groupe de Gubbio (p = 0,04), mais elle repose toujours sur des dates estimées, et ce p n'est pas corrigé pour les tests multiples : on ne retient pas de tendance.
- Réemploi : les mêmes effets dans le même sens, avec des p voisins.
- Estampes par pièce : la baisse tardive ne touche pas la période ≤ 1530 ; elle ne bouge pas.
- Les tests non chronologiques (T-whole, T-rebaptism, T-revers) ne sont pas refaits ici.

## Fichiers

`resultats.json` (pièces exclues et chiffres clés par variante), `complet/`, `sans_gubbio_1522_1527/`, `sans_gubbio_ni_y_slash/` (sorties complètes des quatre tests).
