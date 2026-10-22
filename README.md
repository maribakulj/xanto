# xanto

Essais sur les emprunts de Francesco Xanto Avelli (majolique d'Urbino, années 1530) aux estampes de Marcantonio Raimondi et de son entourage.

Deux questions :

1. Que disent les fiches du catalogue sur ces emprunts : estampes reprises, inversions, dates, taille des figures ?
2. Peut-on retrouver automatiquement l'estampe source d'une figure peinte ?

Aucun résultat n'a été vérifié par un historien de l'art.

## Contenu

| Dossier | Contenu |
|---|---|
| `data/` | Table pièce ↔ estampe extraite automatiquement des 374 fiches du catalogue *Xanto nel mondo* (Fondazione Banca del Monte di Rovigo) : 576 références Bartsch dans 278 fiches. Chaque ligne porte le lien vers sa fiche et reste à vérifier. Script : `scripts/rovigo_table.py`. |
| `analyses/` | Tests descriptifs sur cette table (inversion, réemploi, dates, revers, compositions entières ou découpées). Synthèse : `analyses/RESULTATS.md`. |
| `tests-echelle/` | Mesure de la taille d'une même figure sur l'estampe et sur des plats de diamètres différents (Apollon du *Parnasse*, Métabus, deux témoins). |
| `recherche-sources/` | Recherche automatique de l'estampe source, avec une règle de décision écrite avant chaque calcul (`PREINSCRIPTION_*.md`, puis `RESULTAT_*.md`). |
| `demo/` | Page locale qui présente les données et les tests (ouvrir `demo/index.html`). |
| `prototype/` | Premier essai de localisation sur deux plats (7 octobre 2026), remplacé par `recherche-sources/`. |
| `docs/BIBLIOGRAPHIE.md` | Textes cités et statut de lecture. |
| `JOURNAL.md` | Journal des étapes, résultats et échecs. |

## Résultats

- **Taille des figures** : sur une douzaine de figures et trois plats, la figure peinte a la même taille que sur l'estampe (à quelques pour cent près), quel que soit le diamètre du plat. Les deux agrandissements signalés par Wilson (1990) ne sont pas confirmés. Voir `tests-echelle/`.
- **Tests sur les fiches** : exploratoires, voir `analyses/RESULTATS.md`.
- **Recherche de la source** : sur 105 requêtes jamais utilisées pour le réglage, la bonne estampe est au premier rang dans 22 cas et parmi les 10 premières dans 40 cas, sur une galerie de 1 604 estampes. Voir `recherche-sources/RESULTAT_EVALUATION.md`.

## Ce qui n'est pas publié

Les photographies des plats, les fiches complètes du catalogue, les PDF d'articles et les conversations de travail restent privés. Les images d'estampes viennent des collections en accès ouvert du Metropolitan Museum, du Rijksmuseum, de la National Gallery of Art, de l'Art Institute of Chicago et du Cleveland Museum of Art.
