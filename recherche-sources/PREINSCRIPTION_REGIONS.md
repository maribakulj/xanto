# Étape 3 du plan : des régions côté estampe, sans déformation (règle écrite avant calcul)

Date : 15/10/2026, avant tout calcul de rang avec des régions. Base : AIKON avec DINOv3 large à 512 px (`RESULTAT_PAIRES.md`), résultats `resultats/paires_dinov3_large_mise_au_point58.csv`. Motif : `DIAGNOSTIC_B211.md` (la figure cherchée est minuscule dans les estampes peuplées ; une découpe à la main, complétée en carré sans déformation, la retrouve) et la littérature (Patchify, WACV 2026 ; MaO, NeurIPS 2025 ; notes privées `research_notes/Améliorer la recherche DINOv3/`).

## Méthode (`regions.py`)

- **Régions de chaque image de la galerie** (1 604 images) :
  - une grille sans recouvrement de 2 × 2 et de 3 × 3 morceaux (13 régions) ;
  - les boîtes « person » de Grounding DINO déjà calculées pour le test de l'oracle (`oracle_temoins.csv`, seuil 0,30), bornées à l'image et agrandies de 10 % de chaque côté ; les boîtes de moins de 32 px de côté sont ignorées.
- **Sans déformation** : chaque région, et la figure du plat, est complétée en carré par une bordure du gris moyen de l'image, puis réduite à **384 × 384** (choix fixé par le temps de calcul : 0,4 s par région sur le Mac, contre 0,75 s à 512) ; vecteur de classe normalisé de DINOv3 large.
- **Score d'une estampe** = le plus grand de : son score dans la base (image entière, 512 px, inchangé) et le meilleur score de ses régions, la figure étant prise à l'endroit et en miroir. Le sens retenu est celui du meilleur score.
- **Reclassement** : les 20 premières sont reclassées par SegSwap exactement comme dans la base (images entières, sens retenu).
- Seule vérification faite avant calcul : l'affichage des boîtes « person » sur la *Bataille au coutelas* (3 combattants détectés sur plusieurs dizaines, dont le soldat tombé) ; c'est ce qui a motivé l'ajout de la grille.

## Règle

Sur les **58 requêtes de mise au point**, comparaison requête par requête avec la base (rang final de la vraie estampe) :

- les régions **gagnent** si elles font monter la vraie estampe **au moins six fois de plus** qu'elles ne la font descendre, avec **p < 0,05** au test du signe exact (égalités exclues), **et** si elles ne placent pas moins de requêtes dans les 50 premières ;
- contrôle publié, sans valeur de verdict : le même test agrégé par estampe (une voix par estampe) ;
- descriptif, sans verdict : les rangs avant SegSwap, la grille seule, les personnes seules, et les 9 requêtes de la *Bataille au coutelas* ; le test « source absente ».

Le lot d'évaluation (105 requêtes) n'est pas calculé.
