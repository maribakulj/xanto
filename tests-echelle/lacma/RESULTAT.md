# Témoin positif : plat de Los Angeles (LACMA 49.26.3) — résultat

12/10/2026. Règle de décision écrite avant mesure : `PREINSCRIPTION.md`. Données : `donnees/`. Calcul : `python3 rapports.py donnees annotateur1` (puis `annotateur2`).

## Verdict selon la règle préinscrite : **indécis**

Deux conditions de réussite ne sont pas remplies :
1. **La figure tirée du *Quos Ego* (B. 352) n'est pas identifiée de façon sûre.** Sur quatre annotateurs, un seul la trouve dans la recherche générale (confiance moyenne-faible : Achate, de dos, dans le panneau gauche), l'autre n'en trouve aucune. Dans une vérification ciblée sur ce seul rapprochement, un annotateur le juge **probable** (même schéma de corps : de dos, manteau noué, tête levée, bras tendu ; mais tête jeune et tournée dans l'autre sens), l'autre le **rejette** (pose inversée, bras et vêtement différents, traits seulement génériques).
2. **Une figure de contrôle sort de l'intervalle 0,90-1,10** : le vieillard du centre (tiré du *Massacre des Innocents*), à 0,87 chez les deux annotateurs. Ses jambes sont recomposées sur le plat.

La méthode n'a donc **pas encore de témoin positif validé**. L'axe « reconstituer la version des *Modi* par la taille » reste suspendu, comme prévu par la règle.

## Ce qui est établi quand même

**Les figures que Wilson dit « much the same size » le sont, mesure à l'appui.** Deux annotateurs, indépendamment, sur 6 à 7 figures tirées de quatre estampes :

| Figure (estampe) | Annotateur 1 | Annotateur 2 |
|---|---|---|
| Vieillard à l'extrême droite (*Massacre*, B. 21) | 1,06 | 1,08 |
| Homme au bâton, à gauche (*Massacre*, B. 21) | 1,04 | 0,99 |
| Vieillard du centre (*Massacre*, B. 21), jambes recomposées | 0,87 | 0,87 |
| Homme barbu en jaune (*Parnasse*, B. 247) | 0,98 | 1,02 |
| Jeune homme en bleu (*Parnasse*, B. 247) | 1,03 | 1,01 |
| Putto vu de dos (*Amours dansants*, B. 217) | 1,06 | 1,03 |
| Figure du *Martyre de saint Laurent* (B. 104) | 1,08 (jeune homme en jaune) | 0,98 (dieu-fleuve, autre figure) |

Rapport = longueur sur le plat / même longueur sur l'estampe, en centimètres réels (échelle du plat : 45 cm ; échelle des estampes : dimensions des feuilles publiées par les musées). Hors vieillard du centre, les rapports vont de 0,98 à 1,08 (moyenne 1,03). Sur un plat de 45 cm, Xanto reproduit donc ces figures **à la taille de la gravure**, comme sur les plats d'Apollon (26,7 et 29,8 cm).

**La mesure détecte aussi un écart réel.** Le vieillard du centre, dont les jambes sont recomposées, ressort à 0,87 chez les deux annotateurs : la méthode distingue une figure retravaillée d'une figure reportée. C'est une observation, pas le témoin positif prévu.

**Le rapprochement avec le *Quos Ego*, s'il est juste, va dans le sens de Wilson.** La largeur des épaules (seul segment fiable chez l'annotateur qui le juge probable) donne 2,0 cm sur le plat contre 1,6 cm sur la gravure, soit un rapport d'environ 1,26 (± 12 %, car 25 pixels seulement sur le plat). Observation hors règle, sur une identification disputée : à ne pas compter comme une réussite.

## Limites

- Image du plat en basse définition (640 px pour 45 cm, 0,08 cm par pixel).
- Les annotateurs sont des passes du même modèle d'IA ; ils connaissaient les sources, pas la règle ni la prédiction de Wilson.
- L'échelle des estampes dépend de la feuille : feuilles rognées (B. 21, B. 104), bord douteux (B. 352), bord invisible (B. 420, d'où l'exclusion de Ruggiero).
- Le B. 4 cité par Wilson n'a pas été mesuré (pas d'épreuve dans le corpus).

## Pour obtenir un vrai témoin positif

Une image du plat en haute définition, l'identification de la figure du *Quos Ego* par un spécialiste (Wilson 1990 ne précise pas laquelle), et une épreuve du *Quos Ego* avec son bord de feuille visible. Sinon, chercher un autre cas publié de figure agrandie (Wilson signale aussi le B. 104 sur le plat d'*Astolphe* du British Museum).
