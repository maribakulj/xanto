# Recherche automatique de sources : résultat de l'essai de faisabilité

13/10/2026. Règles écrites avant calcul : `PREINSCRIPTION.md` (étape 1), `PREINSCRIPTION_ETAPE2.md` (étape 2). Résultats par requête : `resultats/etape1.csv`, `resultats/etape2.csv`.

## Verdicts selon les règles préinscrites

| | Retrouvées au rang 1 | dans les 10 premières | dans les 50 premières | Rang médian | Verdict |
|---|---|---|---|---|---|
| Étape 1 (vecteur global par fenêtre) | 0 / 49 | **5 / 49 (10 %)** | 11 / 49 | 249 | **voie fermée pour cette méthode** (< 15 %) |
| Étape 2 (détails cohérents, sur les 50 premières) | 5 / 49 | **8 / 49 (16 %)** | 11 / 49 | 249 | **partiel** (entre 15 et 40 %) |

- Au hasard, on attendrait 0,7 requête retrouvée dans les 10 premières : les deux étapes font nettement mieux que le hasard (p < 0,001), mais **très loin d'un outil utilisable**.
- **L'étape 2 n'apporte rien au sens de la règle** : 3 requêtes gagnées, aucune perdue (il en fallait 5, test de McNemar p = 0,25). Elle change en revanche l'ordre en tête : quand la bonne estampe est parmi les 50 premières, elle passe au **premier rang** dans 5 cas sur 8 (contre 0 à l'étape 1).
- **Le goulot est la première étape** : pour 38 requêtes sur 49, la bonne estampe n'est même pas dans les 50 premières sur 1 604 ; aucun reclassement ne peut la rattraper.

## Ce qui est retrouvé

- **Compositions entières** (Xanto reprend toute la gravure) : 2 sur 5 au premier rang à l'étape 2 (*Enlèvement d'Hélène*, B. 209 ; *Adoration des bergers*, B. XV 4).
- **Figures isolées** : 6 sur 36 dans les 10 premières (putto des *Amours dansants* B. 217, homme poursuivant une naïade B. 226, deux figures du *Trône de Neptune* B. 242, *Jugement de Pâris* B. 245, *Naissance de Vénus* B. 323).
- **Groupes** : 0 sur 8.
- Les figures que l'annotateur a encadrées avec certitude sont un peu mieux retrouvées (6 / 32) que les incertaines (2 / 17).

## Ce que cela veut dire

Comparer des **morceaux d'images résumés en un vecteur** (DINOv2, sans apprentissage) ne franchit pas l'écart entre une figure peinte sur un plat, recolorée, recomposée, et la même figure gravée au milieu d'autres : la voie « chercher les sources inconnues dans des milliers d'estampes » est **fermée pour cette méthode**, comme la règle le prévoyait. La comparaison de **détails cohérents** marche quand la bonne estampe est déjà parmi les candidats (elle la remonte au premier rang), ce qui suggère qu'une **première étape locale** (correspondances de détails dès le départ, et non en reclassement) est la piste à éprouver, plutôt qu'un plus gros vecteur global.

## Écarts à signaler (aucun ne touche la méthode)

- Calcul sur Colab (carte T4, compte gratuit) ; découpe et redimensionnement faits sur la carte graphique (bicubique avec anti-crénelage), en demi-précision, identiquement pour les estampes et les figures.
- Les 1 536 estampes du Met ont été prises dans une copie publiée en « release » du dépôt (domaine public CC0), l'API du Met refusant les serveurs de Colab ; deux épreuves de la *Cléopâtre* (B. 198), que le Met a rephotographiées depuis, ont été remplacées par la version d'origine (empreintes SHA-256 vérifiées).
- L'essai DINOv3 (exploratoire) n'a pas été lancé.

## Limites

- 49 requêtes, 28 estampes sources, une galerie de 1 604 images ; les annotateurs qui ont encadré les figures sont des passes du même modèle d'IA.
- Les épreuves du Met d'une même composition non étiquetées ne sont pas comptées comme réussites (aucune vérification visuelle faite à ce stade).
