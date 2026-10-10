# Test d'échelle n° 1 (pilote) : l'Apollon du *Parnasse*

**Question.** Xanto reportait-il les figures gravées à la taille de l'estampe (calque ou poncif), comme le pensent Wilson 1990 (« most of the figures… correspond in size to the originals », p. 323-324) et Hess 1999 ? Ou les recopiait-il en changeant l'échelle, comme l'admet Mallet 2007 (« capable of copying such figures freehand, and varying them in scale », p. 32-33, d'après Wilson 2002) ? Personne n'a publié de mesure.

**Principe.** On prend une même figure, l'Apollon du *Parnasse* de Marcantonio Raimondi (Bartsch XIV 247), reprise sur des plats de diamètres différents. Si Xanto la reporte à taille fixe, sa hauteur réelle en centimètres reste la même quel que soit le plat. S'il l'adapte au plat, elle grandit avec le diamètre.

**Mesure.** Chaque image est mise à l'échelle par une longueur connue : la largeur de la feuille gravée (46,9 cm selon le Met) ou le diamètre du plat donné par le musée ou par la fiche de Rovigo, mesuré sur le bord extérieur. Sur chaque figure, trois repères sont relevés à la main : le sommet des cheveux, le genou de la jambe tendue et la pointe du pied tendu. Tableau : `mesures.csv` ; calcul : `python3 calcul.py`.

## Résultats

| Témoin | Diamètre (cm) | Tête → pied (cm) |
|---|---|---|
| Estampe, *Parnasse*, 2ᵉ état (Met 17.37.150) | feuille de 46,9 | **9,87** |
| *Apollon et Pan*, 1531 (Fitzwilliam C.88-1961) | 26,7 | **9,90** |
| *Apollon et Pan* (LACMA) | 29,8 | **9,79** |
| *Jugement de Pâris*, 1531 (Fitzwilliam C.86-1961) | 26,0 | 10,48 (tête relevée et tournée de profil) |

- **Sur les deux plats d'*Apollon et Pan*, la figure a la taille de l'estampe à 1 % près** (9,79 à 9,90 cm contre 9,87). Pourtant les deux plats diffèrent de 3,1 cm de diamètre. Si Xanto avait adapté la figure au plat, l'Apollon de Los Angeles mesurerait environ 11 cm. Pour ce cas, le résultat va dans le sens d'un report à taille fixe (Wilson 1990, Hess), et non d'un changement d'échelle.
- **Le Pâris n'est pas comparable tel quel.** La tête y a été redessinée : relevée et tournée vers Vénus. Le segment tête-pied ne mesure donc plus la même chose.
- **Les segments passant par le genou ne concordent pas** (estampe 3,5 cm pour genou-pied, plats 2,9 à 3,2 cm). Sur l'estampe, le genou est en partie caché par le drapé, et mon repère n'est sans doute pas le même point que sur les plats. Je ne retiens pas ces segments.

## Marge d'erreur et limites

- **Erreur de mesure.** Environ ± 2,5 % sur les plats d'*Apollon et Pan* (± 3 px sur des images de 570-640 px, ± 0,2 cm sur le diamètre publié) et ± 1 % sur l'estampe. L'écart observé entre les trois témoins (1 %) est inférieur à cette marge. L'écart que prédirait un changement d'échelle proportionnel au plat (12 %) lui est bien supérieur.
- **Non corrigé :** la perspective des photographies et la courbure du bassin du plat. L'effet est faible près du centre, mais il n'est pas chiffré.
- **Biais de l'annotateur.** Un seul annotateur (Claude) a relevé les repères, en connaissant l'hypothèse. Ce n'est pas une annotation à l'aveugle.
- **Un seul motif, trois témoins.** Cela ne dit rien des autres figures. Wilson 1990 signale lui-même des figures agrandies (B. 352, B. 104).
- **Une seule estampe de référence.** C'est un exemplaire du 2ᵉ état. Rien n'établit qu'il ait la taille exacte de la feuille utilisée par Xanto (marges rognées, retrait du papier).

## Suite proposée

1. Faire relever les mêmes repères par deux personnes qui ignorent l'hypothèse.
2. Étendre le test aux figures les plus réemployées selon la table de Rovigo (`../data/emprunts.csv`) : *Martyre de saint Laurent* (B. 104, 52 mentions), *Muses et Piérides* de Caraglio (B. XV 53, 71 mentions), *Enlèvement d'Hélène* (B. 209). Y ajouter les cas où Wilson signale un agrandissement, pour vérifier que la méthode détecte aussi un changement d'échelle quand il existe.
3. Remplacer les repères manuels par un alignement automatique entre la figure de l'estampe et celle du plat, en publiant le facteur d'échelle obtenu.

Les images ne sont pas versionnées : celles du Fitzwilliam et du Met se téléchargent avec `../prototype/scripts/fetch_assets.py`, celle du LACMA est sur la fiche n° 65 du catalogue de Rovigo.
