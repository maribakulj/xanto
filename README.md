# xanto — génétique des images, cas Xanto Avelli

Travail de recherche en cours sur la transmission, la transformation et la recombinaison des figures dans la majolique *istoriata* de Francesco Xanto Avelli (Urbino, années 1530), à partir de ses emprunts aux estampes de Marcantonio Raimondi.

**Statut, à lire avant le reste.** Ce dépôt rassemble un pilote documenté, une proposition de recherche, une analyse critique de la littérature et un petit prototype de vision par ordinateur. Rien ici n'est une théorie validée, ni un résultat historique nouveau. Les textes distinguent ce qui est observé, ce qui est publié par d'autres auteurs, et ce qui reste une hypothèse. Ils conservent aussi les hypothèses retirées.

Le travail a été mené le 6 et le 7 octobre 2026 par deux assistants IA (Codex et Claude), qui ont dialogué sous la direction du porteur du projet. Les conversations elles-mêmes ne sont pas publiées.

## Organisation

| Dossier | Contenu |
|---|---|
| `docs/pilote/` | Fiche du pilote (deux dossiers : l'Apollon du *Parnasse* repris en Apollon et en Pâris ; la Rome tirée du neuvième *Modo*), lectures et statut des preuves, décisions et réserves |
| `docs/refondation/` | Proposition de recherche, note formelle (identité, transformations, quotient), positionnement, réemploi du travail. **Il s'agit d'une carte de possibilités, pas d'une architecture validée** |
| `docs/bilan/` | Analyse intellectuelle (Impett et Moretti, *Totentanz* 2017 ; Hess 1999 ; Boutin Vitela 2014 ; Mallet 2007 ; Didi-Huberman 1996 ; Drucker, Lavin), notes de lecture et audit des accès |
| `docs/passation/` | État technique et dernier texte critique de Codex avant passation |
| `prototype/` | Visionneuse locale (HTML sans dépendance) et calcul : recherche DINOv2 par patches, gabarit de gradients, évaluation séparée, contrôles triviaux et rejeu isolé. Voir `prototype/README.txt` |

## Prototype

```sh
cd prototype
python3 scripts/fetch_assets.py   # télécharge les 3 images depuis les musées et vérifie leurs empreintes
python3 scripts/serve.py          # ou ouvrir index.html directement
```

Les images ne sont pas versionnées. La gravure du Met est en Open Access ; les deux assiettes du Fitzwilliam Museum sont © The Fitzwilliam Museum, sous licence CC BY-NC-ND.

Résultat de la v0.2, à lire avec ses limites : la localisation est plausible sur *Apollon et Pan*, mais à peine meilleure qu'une boîte placée au centre ; le premier candidat est faux sur le *Jugement de Pâris*. Les identités, les gestes, les contacts et la filiation ne sont pas calculés.

## Ce qui n'est pas dans ce dépôt

- Les archives des conversations et les messages personnels sont conservés en privé.
- Les sources protégées (PDF d'articles, extractions de texte intégral, captures de pages) sont conservées en privé. Les références et les liens figurent dans `docs/bilan/README.txt`, `docs/bilan/XANTO-LITTERATURE.txt` et `docs/pilote/LECTURES-et-CAS.txt`.
- Certains documents renvoient à des fichiers d'archive (`../reprise-mnemosyne/…`, `dialogue-mnemosyne/…`) qui ne sont pas publiés.

## Questions ouvertes

La formalisation personnelle du porteur du projet (la Pathosformel comme invariant sous l'action d'un groupe) est revendiquée, mais son contenu n'est pas reproduit ici. Aucun texte de ce dépôt ne la remplace. Les textes intégraux de Talvacchia 1994, d'Ekserdjian 2007, de Turner 2004 et du catalogue Mallet 2007 n'ont pas été lus.
