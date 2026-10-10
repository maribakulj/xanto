# T-rebaptism (D2) — la figure empruntée change-t-elle d'identité ?

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. Classement approximatif, à vérifier sur les fiches.**

## Thèse discutée

Boutin Vitela 2014 : l'inscription du revers réoriente la lecture d'une image empruntée. Thèse opposée sur le sens : Wilson 1990, Holcroft 1988, Lessmann (figures prises « often without any reference to their original meanings »), c'est-à-dire l'indifférence au sens d'origine. Ce test ne mesure pas la lecture. Il mesure une condition de la thèse : la figure empruntée reçoit-elle souvent une autre identité que dans l'estampe ? Par exemple, Apollon reste Apollon, mais une Muse devient Circé.

## Méthode (`../t_rebapteme.py`)

On lit la proposition de la fiche qui contient la référence : « [cible] è ripresa / tratta / desunta / citata … [source] (Bartsch …) ». Les *Modi* sont compris (616 références en tout).

- **Cible** : nom propre le plus proche avant le verbe d'emprunt (« la figura di Leandro… », « Circe è desunta… »). Si le sujet est un nom commun (« la fanciulla », « il guerriero »), la cible est « générique ».
- **Source explicite** : « dalla figura di X », « dal personaggio di X », « dalla Musa … » après le verbe.
- Sinon, on compare la cible aux **figures connues de l'estampe**, une liste faite à la main dans `../commun.py` (par exemple *Parnaso* : Apollon, Muses, poètes, putti).

Classes : conservée (explicite ou présumée), changée (explicite ou présumée), anonyme → nommée (l'estampe est une foule, une bataille ou une scène des *Modi*, et la cible n'est pas un protagoniste), cible générique, non classé.

## Résultats

| Classe | Références |
|---|---|
| conservée (explicite) | 1 |
| conservée (présumée) | 45 |
| changée (explicite) | 6 |
| changée (présumée) | 94 |
| anonyme → nommée (présumée) | 79 |
| cible générique | 206 |
| non classé | 185 |

- Sur les 225 références dont la cible est nommée, **46 seulement gardent l'identité de la figure source**, et 36 de ces 46 sont des putti devenus Cupidon. Les 179 autres changent d'identité (100) ou donnent un nom à une figure anonyme (79).
- Si l'on met Cupidon à part, l'identité change dans **98 cas sur 111 (88 %)** parmi les cibles qu'on peut comparer.
- Les 7 cas explicites : 6 changements (644 : une Muse du *Parnaso* devient Circé ; 194 : Didone du *Quos Ego* devient Onfale ; 247 : la *Carità* devient Ascagne ; 935 et 626 : David devient Esaque ; 1118 : Cacus devient Palinure) et 1 conservation (331 : Glaucus).
- La part des changements est voisine aux trois périodes : 64 % (≤ 1530), 68 % (1531-1535), 78 % (1536-1542) (70 %, 67 %, 78 % avant la correction des dates du 10/10/2026).
- Exemples d'anonyme → nommée : 956 (Ériphyle tirée du *San Lorenzo*), 637 et 85 (Alcyone tirée des *Modi*), 64 (Métabos tiré de la *Battaglia*), 139 et 237 (Léandre tiré de la *Battaglia col coltellaccio*), 1328 et 414 (Rome tirée des *Modi*).
- Par estampe : sur 23 cibles nommées tirées de la *Contesa* de Caraglio, 23 changent d'identité (Daphné, Thisbé, Ino, Circé…). Les 8 cibles tirées de *Davide e Golia* changent toutes. Dans le *Parnaso*, ce sont surtout les putti qui sont repris comme Cupidon.

Données du graphique : `resultats.json` → `classes` (barres), `par_periode`, `par_estampe` (cibles par estampe), `exemples` (id, cible, figure source, lien).

## Ce que cela dit de la thèse

**Condition commune aux deux lectures ; le test ne départage pas.** Renommer la figure empruntée est la règle chez Xanto (88 % des cibles comparables hors Cupidon). Mais ce taux est prédit **à la fois** par Boutin Vitela (l'inscription réoriente la lecture) et par le camp de l'indifférence au sens d'origine (Wilson 1990, Lessmann : la figure est prise pour sa forme, sans égard à son sens). Il ne soutient donc pas l'une plus que l'autre. Ce qui distinguerait les deux lectures (l'inscription change-t-elle la façon dont on lit l'image ?) n'est pas mesurable ainsi.

Il faut aussi distinguer la part **explicite** (7 cas où la fiche nomme la figure source : 6 changées, 1 conservée) de la part **présumée** (94 changées sur 100, qui reposent sur les listes de figures faites à la main dans `../commun.py`). La part présumée dépend de ces listes : une Muse du *Parnaso* renommée Calliope, ou « Musa », compterait comme conservée.

## Limites

- Le repérage de la cible est fragile : 185 références ne sont pas classées, et 206 ont une cible générique.
- « Présumée » veut dire qu'on ne sait pas quelle figure de l'estampe a servi. Seule la liste des figures de l'estampe est connue, et elle est incomplète.
- Le classement d'un putto devenu Cupidon comme « conservé » est discutable. Les deux chiffres sont donnés, avec et sans Cupidon.
- Ce sont les noms donnés par l'auteur de la fiche, pas toujours par Xanto.

## Fichiers

`rebapteme_par_reference.csv` (id, estampe, classe, cible, figure source, année, lien), `resultats.json`.
