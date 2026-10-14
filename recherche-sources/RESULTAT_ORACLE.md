# Test de l'oracle : résultat

14/10/2026. Règle écrite avant calcul : `PREINSCRIPTION_ORACLE.md`. Données : `resultats/oracle_decoupes.csv` (figures sources encadrées à la main dans les vraies estampes), `resultats/oracle_temoins.csv` (6 956 figures détectées par Grounding DINO dans les 1 604 images), `resultats/oracle.csv` (rang par requête). Scripts : `oracle_detection.py`, `oracle_rangs.py`.

## Verdict selon la règle : **médium**

| | Rang 1 | 10 premières | 50 premières | Rang médian |
|---|---|---|---|---|
| Découpe oracle parmi 6 891 découpes (dont 6 844 témoins) | 0 / 49 | **3 / 49** | 7 / 49 | 923 |
| Sensibilité (non préinscrite, borne haute) : meilleure découpe de n'importe quelle épreuve de la bonne estampe, quelle que soit la figure | 2 / 49 | 7 / 49 | 13 / 49 | — |

Il fallait au moins 25 sur 49 dans les 10 premières pour conclure à l'échelle. Même la borne haute en est très loin. Au hasard, on attendrait 0,07 requête dans les 10 premières.

**Ce que cela veut dire.** Même quand on donne au modèle la bonne figure gravée, déjà découpée et cadrée, la figure peinte du plat ne la reconnaît presque jamais parmi d'autres figures gravées. L'échec de l'essai du 13/10 ne venait donc pas surtout de la petite taille des figures dans les grandes estampes : il vient de ce que **le vecteur global de DINOv2 ne relie pas une figure peinte à la même figure gravée**. Indexer les estampes par régions (étape 3 du plan) ne suffirait pas à lui seul ; la priorité passe aux transformations d'images et aux paires d'apprentissage (étapes 4 et 7), et aux correspondances de détails, qui sont une autre famille de méthode.

## Détails

- Requêtes trouvées dans les 10 premières : Q06, Q18, Q21 (trois figures isolées). Groupes 0 / 8, compositions 0 / 5.
- Figures encadrées avec certitude par l'annotateur : 3 / 24 dans les 10 premières ; encadrées avec doute : 0 / 23 ; introuvables dans l'estampe : 2 (Q08, Q17), comptées comme échecs.
- Comparaison avec l'essai du 13/10, à prendre avec prudence (les concurrents ne sont pas les mêmes : 1 604 estampes entières alors, 6 891 figures découpées ici, qui se ressemblent davantage entre elles) : la recherche par fenêtres sur l'estampe entière mettait 5 requêtes dans les 10 premières (Q15, Q21, Q22, Q24, Q32). Une découpe parfaite ne fait pas mieux que des fenêtres approximatives.
- Le reclassement par détails cohérents (étape 2 du 13/10) remontait la bonne estampe au premier rang dans 5 cas sur 8 où elle était candidate : les correspondances locales franchissent l'écart peinture/gravure mieux que le vecteur global. C'est ce que teste l'étape suivante (AIKON : présélection puis appariement de détails par SegSwap).

## Écarts à signaler

- Une détection avait une coordonnée négative (−6 px) qui faisait planter le calcul. Les boîtes sont désormais bornées à l'image (correction technique, sans effet sur la méthode).
- La colonne de sensibilité « même estampe » a été ajoutée après le premier calcul, pour vérifier que les autres épreuves de la même estampe (présentes dans la galerie) ne faussaient pas le verdict. Elle n'était pas préinscrite et ne change pas le verdict. Les rangs préinscrits sont identiques d'un calcul à l'autre.
- Calcul local (Mac, MPS), détection 2 h 45 environ.

## Limites

- Les découpes oracle ont été faites par des passes du même modèle d'IA, pas par des historiens de l'art ; 23 sur 47 sont marquées « incertaines ».
- 49 requêtes, 28 estampes ; un seul modèle de vecteurs (DINOv2-base, niveaux de gris). Le verdict porte sur cette famille de représentation, pas sur la vision par ordinateur en général.
