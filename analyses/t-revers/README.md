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
- Les *Modi* et les sujets politiques : 7 des 40 pièces aux *Modi* ont *nota* ou un sujet politique selon le commentaire. Le hasard en donnerait 2,7 (p hypergéométrique = 0,011 ; pièces 973, 145, 1328, 428, 414, 889, 1122). Ce point concerne Talvacchia (voir `../RESULTATS.md`).

## Ce que cela dit de la thèse

**Elle est affaiblie, dans la forme testable ici.** Le mot ne suit pas le type des estampes : 12 pièces *fabula* sur 20 empruntent à une estampe religieuse (surtout le *Martirio di San Lorenzo*), et les pièces *historia* empruntent surtout à des estampes mythologiques. Le seul *sporcitia* n'a pas de source connue. Le mot suit plutôt le **genre du récit peint** : *fabula* pour Ovide, *historia* pour l'histoire et Pétrarque, *nota* pour l'actualité politique. Il occupe la place que prendra ensuite la référence au livre.

## Limites

- Les effectifs sont petits (61 pièces, un seul *sporcitia*). Un recueil de modèles n'aurait pas besoin d'être identifiable par les estampes citées dans les fiches.
- Le type de l'estampe est un classement à la main, sujet par sujet. Une même estampe fournit des figures sans rapport avec son sujet : c'est justement ce que montre `../t-rebapteme`.
- Le texte des inscriptions est celui des fiches. Les lectures peuvent différer d'un catalogue à l'autre.

## Fichiers

`revers_par_piece.csv`, `contingence_genre_x_type_estampe.csv`, `contingence_genre_x_source_litteraire.csv`, `contingence_genre_x_source_selon_commentaire.csv`, `genre_par_annee.csv`, `resultats.json`.
