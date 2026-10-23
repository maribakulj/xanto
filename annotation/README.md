# Annotation humaine (référence) — outil local

Une page web qui fonctionne **hors ligne**, sans serveur ni service en ligne, pour constituer une référence humaine :
1. **Paires connues** : tracer la figure sur le plat et sur l'estampe citée, dire trouvée / incertaine / introuvable ;
2. **Sources proposées** : juger oui / peut-être / non les 10 estampes proposées pour une figure sans source ;
3. **Absences** : noter qu'une figure n'a vraisemblablement pas de source dans la galerie.

Le dépôt ne contient que le code. Le paquet généré contient des photos de plats et des estampes : il reste **privé**.

## Générer le paquet

```
~/caypollard/.venv/bin/python annotation/preparer.py <dossier_donnees_prive> <dossier_sortie>
```

`<dossier_donnees_prive>` est le dossier des images (par ex. `~/Documents/Codex/2026-10-08-continuation-claude`) ;
`<dossier_sortie>` reçoit `index.html`, `app.js`, `style.css`, `data.js` et `img/` (vignettes JPEG de 1600 px au plus, environ 140 Mo).
Déposer ce dossier sur le Drive privé (ne jamais le copier dans le dépôt).

## Utiliser

Ouvrir `index.html` dans Chrome, Firefox ou Safari (double-clic depuis le dossier, y compris synchronisé par Google Drive).
Saisir son nom à l'ouverture : il est inscrit avec la date dans chaque réponse.
Glisser pour tracer un rectangle (coins pour l'ajuster), molette pour zoomer, Maj + glisser pour déplacer l'image, bouton « Miroir »,
flèches gauche/droite pour naviguer, touches 1 2 3 pour répondre (le bouton « ? » rappelle les raccourcis).
Dans l'onglet 1 la proposition de l'IA est masquée par défaut (annotation indépendante) ; la rendre visible est signalé dans la réponse.
La sauvegarde est automatique dans le navigateur, mais elle dépend de ce navigateur et de cet ordinateur : **exporter régulièrement**.

## Renvoyer son travail

Bouton « Exporter (JSON) » : le fichier `annotations_<nom>_<date>.json` contient toutes les réponses (rectangles en pixels
de l'image originale). Le CSV est une version à plat pour un tableur. Envoyer le JSON.
« Importer… » relit un export (pour reprendre sur une autre machine ou rassembler plusieurs annotateurs ; en cas de doublon, la réponse la plus récente est gardée).

## Comparer deux annotateurs

```
python3 annotation/comparer.py annotations_A.json annotations_B.json [--csv detail.csv]
```

Donne l'accord (pourcentage, kappa de Cohen) sur trouvée/incertaine/introuvable, oui/peut-être/non et absences,
l'IoU des rectangles, et l'accord de chacun avec les boîtes de l'IA.

## Limites

- Les boîtes de l'IA sont dans `data.js` : la page les masque, elle ne les cache pas techniquement.
- Une seule boîte par estampe et par épreuve ; pour une figure à plusieurs endroits, utiliser le commentaire.
- Seules les estampes de la galerie des compositions citées (`galerie.csv`) servent d'épreuves dans l'onglet 1.
