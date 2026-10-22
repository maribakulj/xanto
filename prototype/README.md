# Prototype v0.2 (7 octobre 2026)

Page locale qui cherche, dans deux plats de Xanto (*Apollon et Pan*, *Jugement de Pâris*), la région la plus proche d'une figure du *Parnasse* de Raimondi. Deux méthodes : descripteurs DINOv2 par patches, et un gabarit de gradients pour comparaison.

## Résultat

Recouvrement (IoU, de 0 à 1) entre le premier candidat et une référence placée à la main :

| | DINOv2 | Gradients | Boîte centrée |
|---|---|---|---|
| *Apollon et Pan* | 0,71 | 0,18 | 0,49 |
| *Jugement de Pâris* | 0,24 | 0,00 | 0,10 |

Deux cibles seulement : aucune conclusion générale. Ce prototype a été remplacé par les essais de `../recherche-sources/`.

## Utilisation

```sh
python3 scripts/fetch_assets.py   # télécharge les images et vérifie leurs empreintes
python3 scripts/serve.py          # ou ouvrir index.html
python3 scripts/run_experiment.py # relance le calcul (DINOv2 déjà en cache)
python3 -m unittest discover -s tests
```

Paramètres : `cv/ALGORITHM-NOTES.txt`. Les annotations de la page restent dans le navigateur ; le bouton d'export les enregistre en JSON.
