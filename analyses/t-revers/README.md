# T-revers (D1, Jestaz) — mots de genre au revers et type des estampes

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches.**

## Thèse discutée

Jestaz 1976 : les mots *fabula*, *historia* et *sporcitia* écrits au revers renverraient à des recueils de modèles classés par genre (*sporcitia* = les parties honteuses, donc les estampes érotiques).

Si c'est vrai, le mot devrait suivre le type des estampes employées : *sporcitia* avec les *Modi*, *fabula* avec les estampes mythologiques, *historia* avec les estampes historiques ou religieuses.

## Méthode (`../t_revers.py`)

- On lit seulement le texte entre guillemets de la section « Iscrizioni ». Cela évite de prendre « si nota » dans la description du catalogue pour le mot *nota*.
- Mots de genre : *historia*/*istoria*/*hist.*, *fabula*/*favola*, *nota*, *sporcitia*, *imaginatione*. Le mot *historico* (« Iustino historico ») n'est pas compté.
- Sources nommées au revers : Ovide (*Ouidio Met.*), Virgile (*Eneida*), Arioste, Pétrarque, Justin, Tite-Live, Turpin.
- Type d'estampe : classement à la main du sujet de chaque estampe, dans `../commun.py` (religieux, mythologique, bataille, historique, autre). Les *Modi* sont repérés par leur mention dans le commentaire (ils ne sont jamais numérotés Bartsch) et classés « érotique ».
- On regarde aussi les sources littéraires que nomme le **commentaire** de la fiche.

## Résultats

- 361 pièces ont une inscription. **61 portent un mot de genre** : 24 *historia*, 21 *fabula*, 13 *nota*, 1 *sporcitia*, 2 avec deux mots (*fabula o historia*, *fabula et hist.*).
- Ces mots datent presque tous de **1528-1531** (`genre_par_annee.csv`). Il y en a un seul en 1533, un en 1534 et un en 1536.
- **Aucune pièce ne porte à la fois un mot de genre et une source au revers** (« Nel … libro d'Ovidio Met. »). Il y a 32 renvois à Ovide, 9 à Virgile et 5 à Justin, tous sur des pièces sans mot de genre. Les deux formules se succèdent : le mot de genre vers 1528-1531, la référence au livre à partir de 1532.

Mot de genre × type d'estampe (pièces avec au moins une estampe de ce type) :

| Mot | Pièces | avec source | érotique (*Modi*) | religieux | mythologique | bataille | historique |
|---|---|---|---|---|---|---|---|
| historia | 24 | 16 | 4 | 9 | 12 | 1 | 2 |
| fabula | 21 | 20 | 1 | 12 | 15 | 5 | 0 |
| nota | 13 | 13 | 4 | 2 | 9 | 2 | 0 |
| sporcitia | 1 | 0 | – | – | – | – | – |
| aucun | 313 | 232 | 31 | 92 | 171 | 38 | 44 |

Mot de genre × source littéraire nommée par le commentaire :

| Mot | Pièces | Ovide | Pétrarque | Virgile | actualité / allégorie politique |
|---|---|---|---|---|---|
| historia | 24 | 9 | 6 | 2 | 1 |
| fabula | 21 | 15 | 1 | 1 | 1 |
| nota | 13 | 1 | 0 | 0 | 6 (et Arioste : 2) |

- Le seul *sporcitia* (pièce 354, Phèdre) n'a **aucune estampe identifiée**. Sur les 40 pièces aux *Modi*, 31 n'ont pas de mot de genre, et aucune ne porte *sporcitia*.
### *Modi* et sujets politiques (Talvacchia)

**Trois définitions de « politique » ont été essayées.** Seule la troisième était publiée avant le 10/10/2026. Les voici toutes, avec la correction de Holm sur les trois (p hypergéométrique unilatéral ; 374 pièces, dont 40 aux *Modi*) :

| Définition de « politique » | Pièces de la catégorie | *Modi* observées | attendues | p | p Holm (3 définitions) |
|---|---|---|---|---|---|
| mot *nota* au revers | 13 | 4 | 1,39 | 0,040 | 0,040 |
| actualité / allégorie politique selon le commentaire | 18 | 6 | 1,93 | 0,007 | 0,022 |
| l'une ou l'autre (retenue avant) | 25 | 7 | 2,67 | 0,011 | 0,022 |

- Pièces : 973, 145, 1328, 428, 414, 889, 1122.
- Par période (définition combinée) : ≤ 1530, 3 observées pour 0,59 attendue ; 1531-1535, 3 pour 1,65 ; 1536-1542, 0 pour 0,18 ; sans période, 1 pour 0,25. Permutation du statut « *Modi* » à l'intérieur des périodes : p = 0,010. La date n'explique pas l'association.
- Les trois définitions se recouvrent ; Holm est donc prudent. Mais l'effectif reste de 4 à 7 pièces, et la colonne `p_holm_toutes` de `../resultats.json` (correction sur toutes les p rapportées) dépasse 0,1.

**Circularité.** Les identifications des *Modi* dans les fiches viennent en bonne partie de Talvacchia, Petruzzellis Scherer et Mallet, qui les ont cherchés précisément sur les plats du Sac de Rome et de Pavie (*Allégorie du Sac*, *Châtiment de Rome*, *Inondation du Tibre*…). Les *Modi* ont sans doute été cherchés plus attentivement sur les plats politiques. Retrouver l'association, c'est en partie retrouver le corpus d'où la thèse est partie. Les pièces 1328 et 414 (Rome tirée du neuvième *Modo*) sont d'ailleurs le cas du pilote.

**L'association ne départage pas Talvacchia et Mallet.** Les scènes de violence et de désastre demandent des corps renversés et raccourcis : c'est l'explication de Mallet (« foreshortened figures in athletic poses »), que Talvacchia relève elle-même (corrélation avec les sujets de « violence and disaster »). Les deux lectures prédisent la même association.

**Verdict : fragile.** Association descriptive, attendue en partie par la façon dont les *Modi* ont été identifiés, et compatible avec Mallet comme avec Talvacchia. Un vrai test de Talvacchia passerait par les mesures d'occlusion et de raccourci sur les images (rapport, Test 5).

## Ce que cela dit de la thèse

**Non testable avec ces données ; le résultat s'accorde avec Mallet et Castelletti, en partie par construction.**

- Le mot ne suit pas le type des estampes : 12 pièces *fabula* sur 20 empruntent à une estampe religieuse (surtout le *Martirio di San Lorenzo*), et les pièces *historia* empruntent surtout à des estampes mythologiques. Mais le type d'estampe est classé d'après le **sujet** de l'estampe source, alors que `../t-rebapteme` montre que les figures sont détachées de leur sujet. Un recueil de *pudenda* pouvait contenir des figures érotiques tirées d'estampes qui ne le sont pas. Ce n'est donc pas le bon indicateur pour Jestaz.
- Le mot suit le **genre du récit peint** : *fabula* pour Ovide, *historia* pour l'histoire et Pétrarque, *nota* pour l'actualité politique. Ce lien est **en partie circulaire** : le « genre du récit » vient du commentaire de la fiche, qui s'appuie lui-même sur l'inscription du revers (sujet, source nommée).
- Le seul *sporcitia* (pièce 354, Phèdre, 1527-1528) n'a **pas de source identifiée**. Un seul cas ne peut rien réfuter. C'est même ce que prédirait Jestaz (un recueil propre à l'atelier, hors des estampes connues). Le texte « phedra da amore et da luxuria oppresa » se lit aussi comme un jugement moral sur le sujet.
- La lecture « le mot donne une consigne de lecture du récit » n'est pas nouvelle : c'est celle de Mallet (« it was he who set the fashion », 2007, p. 34) et de Castelletti. Le résultat les soutient, sans rien ajouter.
- Le mot de genre occupe la place que prendra ensuite la référence au livre (« Nel … libro d'Ovidio », jamais sur la même pièce) : constat descriptif.

## Limites

- Les effectifs sont petits (61 pièces, un seul *sporcitia*). Un recueil de modèles n'aurait pas besoin d'être identifiable par les estampes citées dans les fiches.
- Le type de l'estampe est un classement à la main, sujet par sujet. Une même estampe fournit des figures sans rapport avec son sujet : c'est justement ce que montre `../t-rebapteme`.
- Le texte des inscriptions est celui des fiches. Les lectures peuvent différer d'un catalogue à l'autre.

## Fichiers

`revers_par_piece.csv`, `contingence_genre_x_type_estampe.csv`, `contingence_genre_x_source_litteraire.csv`, `contingence_genre_x_source_selon_commentaire.csv`, `genre_par_annee.csv`, `resultats.json`.
