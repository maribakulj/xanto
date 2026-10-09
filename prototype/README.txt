MNEMOSYNE — PROTOTYPE LOCAL v0.2
7 octobre 2026

Le prototype calcule des régions similaires à un motif fourni dans le Parnasse de Raimondi et les recherche dans deux œuvres de Xanto, Apollon/Pan et Pâris. DINOv2 produit des descripteurs de patches, comparés par une pyramide spatiale ; un gabarit de gradients sert de comparaison simple. Les cinq candidats sont classés automatiquement, puis évalués séparément. L'utilisateur n'a pas à localiser les reprises à la main pour obtenir les résultats.

La version 0.1 était seulement une visionneuse d'annotations : elle ne répondait pas au besoin de computer vision. Son carnet documentaire (22 observations provisoires, 6 propositions comparées) reste disponible sous les calculs. Les annotations proviennent d'assistants informés du dossier, pas d'une validation historique indépendante.

RÉSULTATS CALCULÉS

Recouvrement du PREMIER candidat avec une référence provisoire, IoU entre 0 et 1 (pas une probabilité ni un taux de réussite) :
                         DINOv2    Gradients    Boîte centrée
  Apollon et Pan          0,707       0,180          0,489
  Jugement de Pâris       0,244       0,000          0,097

Apollon : localisation plausible, avec un avantage limité à ce cas sur une figure déjà centrale. Pâris : mauvaise localisation au premier rang, dont le centre est hors de la référence. Choisir un autre candidat à la main ne corrige pas la prédiction initiale. La meilleure IoU parmi cinq est un diagnostic a posteriori distinct, pas le résultat retenu par la machine. Les scores de gradients sont faibles et proches ; leur classement n'est pas calibré.

Deux cibles, des références approximatives et une conception informée du dossier ne permettent pas de conclure à une capacité générale. Trouver une région humaine ne démontre pas l'identification spécifique de ce motif. Gestes, contacts, identité, transmission historique et invariant G ne sont pas calculés.

OUVRIR

Serveur actuellement lancé : http://127.0.0.1:8767/
Autre possibilité : ouvrir index.html directement dans un navigateur. Les données et images sont locales, sans dépendance à un service distant pour consulter le dossier.

Pour relancer le serveur, dans ce dossier :
  python3 scripts/serve.py
Autre port : python3 scripts/serve.py --port 8768
L'adresse et le PID du serveur sont consignés dans .server.json. Le serveur sert des fichiers en lecture ; il ne reçoit pas les annotations.

RELANCER LE CALCUL

  python3 scripts/run_experiment.py
Ou : npm run compute

Le lanceur exécute localisation DINOv2, gradients, évaluation, contrôles triviaux et reconstruction du bundle affiché. Recharger la page après exécution. Le navigateur affiche les calculs enregistrés ; cliquer une proposition ou modifier le carnet ne relance pas l'inférence.

Sur cette machine, le lanceur réutilise en lecture l'environnement ~/caypollard/.venv et le modèle facebook/dinov2-base déjà en cache, révision f9e44c814b77203eaa57a6bdbbd535f21ede1415. Il n'installe rien et fonctionne hors ligne. Pour un autre environnement :
  python3 scripts/run_experiment.py --python /chemin/vers/python
Les versions utilisées sont dans cv/requirements.txt. Le modèle et son processeur doivent déjà être disponibles dans le cache Hugging Face.

La requête-source est fournie dans cv/inputs.json ; les positions cibles n'y figurent pas. Les localisateurs ne lisent pas cv/references.json ni les annotations. L'évaluateur consulte les références seulement après vérification des fichiers de prédictions. Le contrôle source retrouve la région fournie ; il vérifie l'implémentation, pas la généralisation.

Un rejeu DINOv2 en dossier sans références, annotations ou notices a reproduit les 15 propositions à l'identique, avec les cartes de patches en cache. Il ne constitue ni une conception aveugle ni un contrôle d'isolation système. La baseline a été relue mais n'a pas fait l'objet de ce rejeu isolé. Paramètres et limites détaillés : cv/ALGORITHM-NOTES.txt. Les contrôles de centrage et de boîtes aléatoires ont été ajoutés après observation des résultats ; ils sont descriptifs, pas un test de significativité.

UTILISER LE CARNET

Choisir deux témoins, zoomer et sélectionner une observation pour voir son repère. Le miroir inverse uniquement l'affichage ; un bandeau le signale sur l'image. Les filtres distinguent image, notice et interprétation.
Les notes et degrés de confiance se modifient dans le carnet. Le bouton + ajoute une observation, avec un repère facultatif. Les repères sont des proportions de l'image de référence, pas des mesures physiques.
Exporter les annotations produit un JSON avec les sources originales, les observations courantes, les changements avant/après datés, les empreintes et les éventuels anciens brouillons.

CONSERVATION

Les notes restent dans le navigateur et dépendent de l'adresse utilisée. Le fichier local et l'adresse HTTP n'ont pas le même espace de sauvegarde. L'export conserve une copie transportable ; il n'existe pas encore d'import ou de migration automatique dans l'interface.
Un changement du dossier source n'applique pas silencieusement les anciennes notes : l'ancien brouillon est conservé à part et exportable. Un contenu de stockage corrompu est également conservé brut. Une copie du dossier source accompagne les nouvelles sauvegardes pour en préserver le contexte.
Une réinitialisation demande confirmation et ne supprime pas les fichiers source. L'effacement des données du navigateur par l'utilisateur peut supprimer ses notes ; une copie exportée reste indépendante.

CE QUE LE PREMIER RELEVÉ APPORTE

Les mains hautes, les objets tenus, les orientations des têtes et les relations au partenaire sont relevés séparément. La correspondance main/objet entre source et Pâris est proposée avec prudence ; une orientation sans inversion globale reste une hypothèse comparée. Les contacts fins sur Apollon demeurent indéterminés, faute d'une image suffisante.
L'échelle physique, la fabrication par patrons, l'intention du peintre, la réception et la théorie de la Pathosformel ne sont pas testées. Rome/Modo9 reste un dossier documentaire futur.

FICHIERS

data/corpus.json : objets, reproductions, dimensions, attribution, sources et licences.
data/observations.json : relevés, niveau de preuve, confiance, repères et provenance.
data/comparisons.json : propositions avec références aux observations et entités.
data/bundle.js : version embarquée générée à partir de ces trois JSON.
cv/inputs.json : images, requête-source et paramètres principaux du calcul.
cv/results.json, cv/baseline_results.json : candidats calculés et provenance des exécutions.
cv/references.json, cv/evaluation.json : références provisoires et évaluation séparée.
cv/trivial_controls.json : repères descriptifs de centrage et de positions aléatoires.
cv/isolation-check.json : contrôle de reproduction DINOv2 sans fichiers d'annotations.
data/cv_bundle.js : résultats calculés intégrés à l'interface, distincts du carnet.
assets/ : reproductions institutionnelles conservées sans retouche ; les droits sont indiqués dans corpus.json.
reviews/ : demandes de revue, réponses publiques de Claude, décisions et bilan des corrections.
tests/output/ : captures et résultats de la vérification technique ; l'export de test est une fixture, pas un relevé de recherche supplémentaire.

RECONSTRUIRE ET VÉRIFIER

Après une modification des JSON :
  python3 scripts/build_bundle.py
Le constructeur vérifie notamment les liens entre objets, entités et observations, les repères, les images et leurs empreintes. Une reproduction remplacée exige de réexaminer ses annotations.

Contrôles d'intégrité :
  python3 -m unittest discover -s tests -v

Vérifications de navigateur, serveur lancé et Google Chrome installé :
  npm ci
  npm run test:browser
  npm run test:cv-browser
Playwright sert uniquement à ces tests ; il n'est pas nécessaire pour utiliser le prototype.

Les contrôles automatiques vérifient le fonctionnement et la cohérence des données, pas la justesse des interprétations. Les revues de Claude sont conservées avec leurs réserves et ne doivent pas être prises pour une validation scientifique.

ORIGINE

Projet de recherche affiné dans :
~/Documents/Codex/2026-10-07/dialogue-mnemosyne/PROJET-PILOTE.txt
Travail réalisé par Codex avec trois sous-agents et Claude dans l'onglet 1 comme reviewer. Les deux revues CV, réponses et décisions sont conservées dans reviews/cv/. etude-02 et caypollard n'ont pas été modifiés.
