# Dictionnaire des données

Les chemins sont relatifs à la racine du dépôt. « Privé » = dossier désigné par `XANTO_PRIVE`, hors dépôt (voir `REPRODUIRE.md`).

## Fichiers de résultats de la recherche de source (`recherche-sources/resultats/`)

Une ligne par requête (une figure découpée sur la photo d'un plat). Le rang est celui de la vraie estampe parmi les 1 604 images de la galerie (1 = premier).

### Colonnes communes

| Colonne | Sens |
|---|---|
| `requete` | identifiant de la requête (Q01…). Le lot (mise au point ou évaluation) est dans `recherche-sources/lots.csv`, la boîte découpée sur la photo dans `recherche-sources/requetes_boites.csv`. |
| `bartsch` | estampe source, sous la forme volume/numéro de Bartsch (26/247 = *Parnasse*). Source établie d'après le commentaire de la fiche de Rovigo. |
| `type` | `figure` ou `groupe` : ce que la boîte découpe. |
| `trouve` | certitude de l'annotateur qui a encadré la figure sur le plat : `oui` = figure encadrée avec certitude, `incertain` = encadrement ou identification douteux (voir `RESULTAT.md`). Le rang est calculé dans les deux cas. |
| `sens` | sens de la figure (`endroit` ou `miroir`) qui a donné le meilleur score pour la candidate classée au rang retenu. |
| `score_vraie` | score SegSwap de la vraie estampe ; vide si elle n'est pas dans les 20 premières reclassées. |
| `score_premier` | score SegSwap de l'estampe classée première. |
| `score_absente` | score SegSwap de la meilleure fausse estampe quand la vraie est retirée de la liste (mesure de ce que donne le système quand la source est absente). |

### Attention : noms de colonnes trompeurs

Les noms viennent du premier script (`aikon.py`) et n'ont pas été changés pour ne pas modifier les fichiers publiés après coup.

- **`rang_aikon` est le rang FINAL**, après reclassement des 20 premières par SegSwap (même dans les fichiers de la chaîne « régions »). C'est lui qu'on lit pour « rang 1 / 10 premières / 50 premières / médiane ».
- **`rang_cosinus` est le rang de la PRÉSÉLECTION**, avant SegSwap, d'après la similarité entre vecteurs.

Dans `evaluation_candidate_regions.csv` : `rang_aikon` = 22 / 40 / 61 (rang 1 / 10 premières / 50 premières), `rang_cosinus` = 17 / 40 / 61. Dans `evaluation_base_dinov3_large.csv` : `rang_aikon` = 5 / 14 / 27, `rang_cosinus` = 5 / 15 / 27. Dans les fichiers « base », le score de présélection est celui de l'image entière ; dans les fichiers « régions », c'est le maximum entre l'image entière et la meilleure région de l'estampe.

### Colonnes propres aux fichiers « régions » (`evaluation_candidate_regions.csv`, `regions_*.csv`)

| Colonne | Sens |
|---|---|
| `rang_grille_seule` | rang de présélection si on n'utilise que l'image entière et la grille 2×2 / 3×3 (sans boîtes de personnes). |
| `rang_personnes_seules` | idem avec l'image entière et les boîtes « personne » (Grounding DINO) seulement. |
| `rang_regions_sans_base` | idem avec les régions seulement, sans l'image entière. |
| `region_vraie` | meilleure région de la vraie estampe : `type:x0,y0,x1,y1` (`grille2`, `grille3` ou `personne`, en pixels de l'image de la galerie). |

Ces trois derniers rangs sont des rangs de présélection (avant SegSwap).

### Liste des fichiers

| Fichier | Contenu | Étape |
|---|---|---|
| `evaluation_base_dinov3_large.csv` | 105 requêtes d'évaluation, chaîne de base (DINOv3 large, image entière) | évaluation finale |
| `evaluation_candidate_regions.csv` | mêmes requêtes, chaîne candidate (régions + SegSwap sur la région) | évaluation finale |
| `aikon_mise_au_point.csv`, `dinov3_*_mise_au_point.csv`, `canal_*`, `paires_*`, `regions_*` | requêtes de mise au point (58 ou 19), variantes essayées avant l'évaluation | `RESULTAT_*.md` correspondants |
| `etape1.csv`, `etape2.csv` | première approche DINOv2 (colonnes `rang`, `rang_etape1`, `rang_etape2`) | `RESULTAT.md` |
| `oracle.csv`, `oracle_decoupes.csv`, `oracle_temoins.csv` | test de l'« oracle » : découpes faites à la main (`oracle_decoupes.csv`), figures détectées par Grounding DINO (`oracle_temoins.csv` : image, boîte, score de détection) | `RESULTAT_ORACLE.md` |
| `accord_*.txt` | accord entre deux encadrements de la même figure : requête, `trouve` de chacun, recouvrement des boîtes (IoU) ; produit par `accord_boites.py` | `PREINSCRIPTION_PAIRES.md` |

## Manifestes

### `recherche-sources/manifeste_estampes.csv` (2 889 lignes)

| Colonne | Sens |
|---|---|
| `chemin` | emplacement de l'image dans le dossier privé |
| `partie` | `met` (1 536 estampes du Met), `connues` (68 épreuves des estampes citées par les fiches), `plus` (galerie agrandie : Rijksmuseum, NGA, Art Institute, Cleveland) |
| `composition` | numéro de Bartsch (`26/247`) pour `connues` ; identifiant du musée préfixé (`met:345270`, `aic:106561`) sinon |
| `musee`, `identifiant_musee`, `url_notice` | musée, numéro dans sa base (numéro d'objet Met, d'inventaire, etc.), page de la notice |
| `url_image` | URL de l'image téléchargée quand elle est connue (vide pour `plus` et pour une partie des Met : voir plus bas) |
| `licence` | licence indiquée par le musée (ou, à défaut, licence générale de ses données ouvertes : voir plus bas) |
| `titre`, `artiste`, `date_ou_inventaire` | métadonnées du musée, quand elles ont été gardées (`date_ou_inventaire` : pour le Rijksmuseum, c'est le numéro d'inventaire, pas une date) |
| `sha256`, `largeur`, `hauteur` | empreinte et dimensions du fichier utilisé |
| `empreinte_stable` | `oui` : fichier tel que le musée le sert, l'empreinte doit se retrouver ; `non` : image réduite à 1 200 px par Pillow, l'empreinte dépend de la version de Pillow et du serveur du musée, seules les dimensions sont comparées |

Limites. `galerie.csv` (1 604 images) = `met` + `connues`. La partie `plus` (1 285 images) sert à l'essai sur la galerie agrandie et à la recherche de sources inconnues ; elle se reconstruit avec `galerie_plus.py`, qui interroge les musées, et peut donc changer si leurs collections changent. La licence de chaque objet n'a pas été revérifiée un à un : les listes ont été obtenues avec le filtre « domaine public / accès ouvert » de chaque musée, et la licence indiquée est celle de ce régime. Le dossier privé contient 36 images Rijksmuseum et 21 images Met de plus que le manifeste (non utilisées par les scripts).

### `recherche-sources/manifeste_plats.csv` (295 lignes)

Photographies des plats, **images non publiées**. `id_fiche` = identifiant de la fiche du catalogue de Rovigo (le même que dans `data/pieces.csv`), `fichier` = nom du fichier (`<id_fiche>__<nom d'origine>`), `url_fiche`, `url_image` (adresse publique de la photo sur le site de Rovigo), `sha256`, `largeur`, `hauteur`. Ces photos appartiennent à la Fondazione Banca del Monte di Rovigo / aux musées prêteurs : elles se retéléchargent depuis le site du catalogue (`telecharger_donnees.py`) et ne doivent pas être redistribuées.

### `recherche-sources/manifeste_images.csv` (ancien manifeste)

Utilisé par `telecharger_donnees.py` pour les estampes ; ses lignes `Rovigo` sont reprises, avec les 246 autres photos, dans `manifeste_plats.csv`.

## Tables tirées des fiches (`data/`)

- `pieces.csv` : une ligne par fiche (374), champs repris du catalogue (titre, date, forme, diamètre, lieu, inscription), lien vers la fiche. Extraction automatique : à vérifier sur la fiche.
- `emprunts.csv` : une ligne par référence Bartsch citée (576). `inversione` = 1 si la phrase de la référence évoque une inversion ; c'est un repérage plus large que celui des analyses (109 contre 63 : voir `analyses/t_inversion.py`).
- `estampes_sources.csv`, `titres_estampes.csv` : métadonnées des 68 épreuves de référence et titres des estampes.

## Analyses (`analyses/`)

`resultats.json` regroupe les sorties des tests sur les fiches. Seul `tout.py` les recalcule (il lit les fiches complètes, privées). `recherche-sources/verifier_resultats.py` contrôle la cohérence de `resultats.json` avec `data/*.csv` (nombre de fiches, de références, répartition des estampes par pièce, effectifs par période), mais ne refait pas les tests statistiques.
