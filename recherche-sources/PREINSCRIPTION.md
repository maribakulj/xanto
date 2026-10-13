# Recherche automatique de sources : essai de faisabilité, règle écrite avant calcul

Date : 13/10/2026, avant tout calcul de similarité. Rien ne sera réglé après avoir vu les résultats ; tout réglage ultérieur sera signalé comme exploratoire.

## Question

Un logiciel de vision par ordinateur, sans apprentissage sur ce corpus, retrouve-t-il, parmi plus d'un millier d'estampes, la gravure dont le catalogue de Rovigo dit qu'une figure d'un plat de Xanto est tirée ? Si non, la voie « chercher des sources inconnues » est fermée pour cette méthode ; si oui, elle peut servir aux figures sans source et à mettre à l'épreuve les attributions aux *Modi*.

## Requêtes

`requetes.csv`, tiré par `selection_requetes.py` (graine 13102026) : les emprunts du catalogue dont l'estampe source a une épreuve libre (28 estampes, `data/estampes_sources.csv`) et dont le plat a une photographie ; au plus 2 par estampe, plats tous distincts ; 54 requêtes. Chaque figure est encadrée sur la photographie du plat par un annotateur qui lit la phrase du catalogue et ne voit **aucune estampe**. Les requêtes jugées « non trouvées » sont retirées et comptées.

## Galerie

Toutes les épreuves libres des 28 estampes sources (Rijksmuseum, Met, Art Institute of Chicago), plus les estampes du Met en domaine public (gravure, eau-forte, bois, clair-obscur) de quinze graveurs de l'entourage de Marcantonio, datées 1490-1570 (`galerie_met.py`). Images ramenées à 1 200 px au plus.

## Méthode (fixée)

- Modèle : DINOv2-base (`facebook/dinov2-base`), vecteur CLS, sans apprentissage ; images en niveaux de gris.
- Requête : la figure découpée et son image en miroir (Xanto inverse souvent) ; on garde la meilleure des deux.
- Estampe : l'image entière et des fenêtres glissantes de hauteur 90 %, 60 % et 40 % de la hauteur de l'image, de proportions largeur/hauteur 0,5, 0,8 et 1,2, avec un pas d'un tiers de fenêtre ; le score d'une estampe est la meilleure similarité cosinus de ses fenêtres.
- Une requête est **retrouvée au rang k** si une épreuve de la bonne estampe (même numéro Bartsch) figure parmi les k premières images.

## Règle de décision (rappel à 10)

- **Voie praticable** : au moins 40 % des requêtes retrouvées dans les 10 premières, et nettement au-dessus du hasard (test binomial, p < 0,01, contre le taux attendu en tirant les images au hasard).
- **Voie fermée pour cette méthode** : moins de 15 % retrouvées dans les 10 premières.
- **Partiel** entre les deux : on dira pour quels types d'emprunt (figure isolée, groupe, composition entière) la méthode marche.
- **Indécis** si moins de 30 requêtes restent utilisables.

Seront aussi publiés : rappel à 1 et à 50, rang médian, résultats par type d'emprunt et par musée de l'épreuve (pour vérifier que le style de photographie ne fait pas le travail). Les épreuves du Met d'une même composition non étiquetées dans `estampes_sources.csv` ne comptent pas comme réussite dans le chiffre principal ; une vérification visuelle sera rapportée à part. Le modèle CLIP pourra être essayé, à titre exploratoire seulement.
