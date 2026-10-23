# Reproduire les résultats

Trois expériences indépendantes. Chacune a un **mode léger** (on relit les CSV publiés, rien à installer sauf Python 3) et, quand c'est possible, un **mode complet** (on recalcule depuis les images).

Rappel : aucun résultat n'a été vérifié par un historien de l'art ; ces commandes disent seulement si les chiffres publiés se retrouvent.

## Données publiques et privées

| | Dans le dépôt | Hors dépôt (privé, dossier `XANTO_PRIVE`) |
|---|---|---|
| Estampes | `recherche-sources/manifeste_estampes.csv` (identifiant du musée, URL, licence, SHA-256) | les images (musées en accès ouvert : Met, Rijksmuseum, NGA, Art Institute, Cleveland) |
| Photos des plats | `recherche-sources/manifeste_plats.csv` (fiche, fichier, URL, SHA-256, dimensions) | les photos (`corpus-images/rovigo/`) |
| Fiches du catalogue | `data/*.csv` (tables extraites, liens vers les fiches) | le JSON complet des 374 fiches (`sources-libres/Rovigo_Xanto_catalogo_374_schede.json`) |
| Résultats | `recherche-sources/resultats/*.csv`, `analyses/resultats.json`, `tests-echelle/*.csv` | caches de vecteurs (`*.pt`, plusieurs Go) |
| Modèles | rien (voir `MODELES.md`) | poids DINOv3 (licence à accepter), Grounding DINO, SegSwap |

Dictionnaire des colonnes : `DONNEES.md`. Versions : `requirements.txt`.

Pour le mode complet, créer un dossier privé et le désigner :

```
export XANTO_PRIVE=/chemin/vers/dossier_prive
python3 recherche-sources/telecharger_donnees.py "$XANTO_PRIVE"   # estampes des musées + photos des plats, SHA-256 vérifiés
```

Le fichier des fiches complètes n'est pas téléchargé par ce script : il se récupère sur le site du catalogue (API `wp-json/wp/v2/posts` de `xanto.fondazionebancadelmonte.rovigo.it`) et se place dans `$XANTO_PRIVE/sources-libres/Rovigo_Xanto_catalogo_374_schede.json`. Les images réduites (Met, galerie agrandie) n'ont pas d'empreinte stable (voir `DONNEES.md`).

## Contrôle rapide de tout ce qui est public

```
make verifier-resultats     # chiffres de l'évaluation et des analyses
make verifier-donnees       # cohérence des manifestes (et SHA-256 des images si XANTO_PRIVE est défini)
```

Ces deux commandes sont aussi lancées par GitHub Actions (`.github/workflows/verifier.yml`).

## A. Tests sur les fiches du catalogue

Question : que disent les 374 fiches des estampes reprises, des inversions, des dates ? (`analyses/RESULTATS.md`.) Extraction automatique par expressions régulières : chaque chiffre est à vérifier sur la fiche.

- **Léger** : `python3 recherche-sources/verifier_resultats.py` recoupe `analyses/resultats.json` avec `data/pieces.csv` et `data/emprunts.csv` : 374 fiches, 576 références Bartsch dans 278 fiches, périodes (101 / 164 / 101 / 8 sans période), répartition des estampes par pièce, nombre de pièces par estampe. Il ne refait pas les tests statistiques.
- **Complet** : `XANTO_PRIVE=... make analyses` (équivalent de `python3 analyses/tout.py`). Données privées nécessaires : le JSON des fiches. Résultat attendu : `analyses/resultats.json` et les dossiers `analyses/t-*/` réécrits avec les mêmes valeurs (seule la date `genere_le` change ; les tests par permutation utilisent un tirage fixé dans le code). Attention : la commande écrase les fichiers suivis par git ; vérifier avec `git diff`.

## B. Taille des figures (échelle)

Question : une figure est-elle reportée à la taille de l'estampe ? (`tests-echelle/README.md`.) Les repères ont été relevés à la main sur des images : les CSV de repères sont publics, le calcul n'a pas besoin des images.

- **Léger (= complet pour le calcul)** :
  ```
  python3 tests-echelle/calcul.py                       # Apollon du Parnasse : 9,87 / 9,90 / 9,79 cm (estampe / deux plats)
  python3 tests-echelle/camille_calcul.py               # Métabus, série du Sauvetage de Camille
  python3 tests-echelle/astolphe/rapports.py tests-echelle/astolphe/donnees annotateur1 plat_commons.jpg 26.1
  python3 tests-echelle/lacma/rapports.py tests-echelle/lacma/donnees annotateur1
  ```
  Résultat attendu : les valeurs de `tests-echelle/README.md` et des `RESULTAT.md` de chaque dossier ; `calcul.py` et `camille_calcul.py` réécrivent `cas.json` et `camille_resultats.json` à l'identique.
- **Complet** : refaire les relevés suppose de retrouver les images (Met, Fitzwilliam, fiches de Rovigo ; voir `tests-echelle/README.md` et `prototype/scripts/fetch_assets.py`) puis de reporter les repères à la main : non automatisable.

## C. Recherche de la source d'un plat

Question : sur 105 requêtes (figures découpées sur les plats, 18 estampes jamais utilisées pour le réglage), dans quel rang la bonne estampe arrive-t-elle, sur une galerie de 1 604 images ? (`recherche-sources/RESULTAT_EVALUATION.md`.)

Résultat attendu :

| | rang 1 | 10 premières | 50 premières | rang médian |
|---|---|---|---|---|
| base (image entière) | 5 | 14 | 27 | 195 |
| candidate (régions + SegSwap sur la région) | 22 | 40 | 61 | 34 |

La vraie estampe monte 85 fois et descend 15 fois. Attention au nommage : dans les CSV, `rang_aikon` est le rang final (après SegSwap) et `rang_cosinus` la présélection ; voir `DONNEES.md`.

- **Léger** : `make verifier-resultats` relit `resultats/evaluation_base_dinov3_large.csv` et `resultats/evaluation_candidate_regions.csv` et retrouve ces chiffres, les intervalles de Wilson, le test du signe, les rangs avant SegSwap (17 / 40 / 61 et 5 / 15 / 27) et les grandes pertes.
- **Complet** (`make reproduire-evaluation`, calcul long, un seul calcul lourd à la fois sur un Mac de 16 Go) :
  1. installer l'environnement (`make setup`), accepter la licence DINOv3 et se connecter à Hugging Face, préparer SegSwap (`MODELES.md`) ;
  2. `python3 recherche-sources/telecharger_donnees.py "$XANTO_PRIVE"` ;
  3. `cp recherche-sources/resultats/oracle_temoins.csv "$XANTO_PRIVE/recherche-sources/"` (les boîtes « personne » de Grounding DINO sont fournies ; pour les recalculer : `oracle_detection.py "$XANTO_PRIVE/recherche-sources"`) ;
  4. chaîne de base : `python3 recherche-sources/aikon.py "$XANTO_PRIVE/recherche-sources" "$SEGSWAP" evaluation facebook/dinov3-vitl16-pretrain-lvd1689m 512` → `resultats_aikon_evaluation_dinov3-vitl16-pretrain-lvd1689m_512.csv` ;
  5. chaîne candidate : `RECLASSE=region python3 recherche-sources/regions.py "$XANTO_PRIVE/recherche-sources" "$SEGSWAP" evaluation` → `resultats_regions_evaluation_reclasse_region.csv` ;
  6. comparer aux CSV publiés (`cmp`, ou `python3 recherche-sources/comparer.py base.csv candidate.csv` pour le test du signe).

  Données privées nécessaires : images d'estampes et photos des plats (étape 2). Le calcul publié a été fait avec le code du commit `a9bb8a7` ; `regions.py` a changé depuis. Pour la version exacte : `git worktree add ../xanto-a9bb8a7 a9bb8a7` puis `make reproduire-evaluation CODE=../xanto-a9bb8a7/recherche-sources`. Les rangs peuvent différer légèrement selon la machine et la version de PyTorch (voir `MODELES.md`) : la comparaison attendue est celle des effectifs (22 / 40 / 61 et 5 / 14 / 27), pas l'égalité de chaque ligne.

La galerie agrandie (1 285 estampes de plus) et la recherche de sources inconnues (`PROTOCOLE_INCONNUES.md`, `chercher.py`) ne sont pas couvertes par ces vérifications : elles ne reposent que sur `manifeste_estampes.csv` et sur `galerie_plus.py`, qui interroge les musées.
