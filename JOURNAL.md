# Journal de travail autonome

## 10/10/2026
- Lancement de la boucle autonome (demande de Marcel : affiner, explorer les autres tests, démo). Plan dans `PLAN.md`.
- Point de départ : table pièce ↔ estampe (374 fiches, 576 références Bartsch) ; test d'échelle pilote sur l'Apollon du *Parnasse* (estampe 9,87 cm ; plats 9,90 et 9,79 cm).
- Démo v0 (`demo/`) : accueil, corpus (frise, estampes les plus reprises, table filtrable), test d'échelle à échelle réelle avec repères ; titres des 28 estampes les plus citées (`data/titres_estampes.csv`). Vérifiée dans Chrome sans erreur.
- Carte de la littérature (`demo/data/litterature.json`) : 39 textes, 11 questions, 81 positions ; intégrée à la démo (onglet « Les débats »), vérifiée sans erreur.
- Test d'échelle Apollon : second annotateur indépendant (instance sans connaissance de l'hypothèse) → 10,10 / 9,70 / 9,92 cm (estampe / C.88 / LACMA) ; écart entre annotateurs ~2 % ; conclusion inchangée. `tests-echelle/reperes_independants.csv`.
- Corpus d'images (privé) : 296 fiches de Rovigo avec image (78 fiches n'en ont aucune, même par l'API WordPress) ; plats du Met en haute définition et domaine public (Camille 1539, 29,7 cm ; Sémiramis 45,4 cm ; Enlèvement d'Hélène 47 cm ; un plat de 49,5 cm).
- Test d'échelle n° 2 lancé : série du *Sauvetage de Camille* (Métabus tiré de la *Bataille entre Romains et Carthaginois* de Marco Dente, B. 420). Cinq plats avec image (26 à 31 cm, 1533-1539), annotés par deux annotateurs indépendants (instances sans l'hypothèse, images anonymisées A-E, diamètres en pixels mesurés par eux aussi).
- Test d'échelle n° 3 préparé : *Enlèvement d'Hélène* copié en entier sur de grands plats (42 à 47 cm) ; en attente de l'estampe B. 209.
