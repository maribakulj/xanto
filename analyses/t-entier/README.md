# T-whole (E1, Briend) — estampe copiée en entier ou découpée ?

**Statut : extraction automatique (text-mining) des fiches du catalogue de Rovigo. À vérifier sur les fiches.**

## Thèse discutée

Briend 1992 : les estampes de Caraglio seraient copiées en entier, celles de Marcantonio découpées en motifs, à cause de l'échelle des figures.

## Méthode (`../t_entier.py`)

On lit ce qui précède chaque référence dans la fiche. On décide dans cet ordre :

1. **composition entière** : « l'intera composizione », « l'intera scena », « la scena è tratta / ripresa », « la composizione è derivata », « interamente », « citazione letterale » dite de la composition ;
2. **partie de figure** : « le gambe », « la parte superiore », « il resto del corpo »… ;
3. **groupe** : sujet au pluriel avant le verbe (« il gruppo », « la coppia », « le due figure », « sono riprese ») ;
4. **figure isolée** : sujet au singulier ;
5. **non classé** : simple liste de sources.

Seul le sujet placé avant le verbe est lu. Sans cette précaution, le titre « Contesa tra le Muse » faisait classer « groupe » toute figure tirée de cette estampe. Une seconde mesure regroupe « composition entière » et « groupe ». Test Caraglio contre Marcantonio : permutation des graveurs entre pièces.

## Résultats

| Graveur | Références | Entière | Groupe | Figure | Partie | Non classé | Part entière* | Part entière ou groupe* |
|---|---|---|---|---|---|---|---|---|
| Marcantonio | 303 | 10 | 58 | 172 | 7 | 56 | 4,0 % | 27,5 % |
| Caraglio | 132 | 8 | 44 | 62 | 0 | 18 | 7,0 % | 45,6 % |
| Marco Dente | 90 | 2 | 15 | 60 | 0 | 13 | 2,6 % | 22,1 % |
| Agostino Veneziano | 32 | 2 | 1 | 21 | 0 | 8 | 8,3 % | 12,5 % |
| *Modi* (Marcantonio, sans numéro) | 40 | 0 | 8 | 23 | 0 | 9 | 0 % | 25,8 % |

\* parmi les références classées.

- Sur l'ensemble, la composition entière est **rare** : 22 références sur 472 classées (4,7 %). Liste des pièces : 112, 116, 339, 446, 461, 489, 590, 756, 760, 820, 827, 925, 939, 950, 1000, 1101, 1129, 1131, 1152, 1257, 1263, 1344.
- Caraglio contre Marcantonio, part « entière » : +3,1 points, **non significatif** (p = 0,22). Part « entière ou groupe » : +10 points (p = 0,06).
- Caraglio **sans la *Contesa*** (B28.53) : 8 compositions entières sur 52 références classées (15 %). Ce sont la *Fuga di Enea* (461, 827, 1257), les *Nozze di Alessandro e Rossana* (489, 760, 939) et l'*Adorazione dei pastori* (1101, 1263). La *Contesa*, estampe de Caraglio la plus employée (71 références), n'est jamais copiée en entier : on en tire des figures et des groupes.

Données du graphique : `entier_par_graveur.csv` (barres empilées par graveur), `resultats.json` → `par_estampe`.

## Ce que cela dit de la thèse

**Pas de conclusion nette, avec des nuances.** Ce n'est pas Caraglio en général qui est copié en entier, mais certaines estampes narratives de Caraglio (*Enea*, *Alessandro e Rossana*, *Adorazione*). Son estampe la plus utilisée est découpée comme celles de Marcantonio. Les emprunts à Caraglio sont un peu plus souvent des groupes. Cela va dans le sens de l'argument d'échelle, sans être significatif au seuil habituel.

## Limites

- Le classement dépend des formules du rédacteur. « La scena è tratta da… » peut désigner une adaptation libre.
- 104 références sont des listes de sources sans verbe, donc non classées.
- L'échelle des figures n'est pas mesurée ici. Le dossier `../../tests-echelle` contient un premier test sur image.

## Fichiers

`entier_par_reference.csv`, `entier_par_graveur.csv`, `resultats.json`.
