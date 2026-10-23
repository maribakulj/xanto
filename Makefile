# Reproductibilité du dépôt. Voir REPRODUIRE.md.
#   make verifier-resultats   rien d'autre que Python 3 (aucune donnée privée, aucun modèle)
#   make verifier-donnees     cohérence des manifestes ; avec XANTO_PRIVE, recalcule aussi les SHA-256 des images
#   make analyses             relance les tests sur les fiches (exige XANTO_PRIVE ; réécrit analyses/resultats.json)
#   make reproduire-evaluation  recalcul COMPLET de l'évaluation (modèles, plusieurs heures ; exige XANTO_PRIVE, SEGSWAP, accès DINOv3)
#   make setup                installe l'environnement Python (.venv) avec les versions de requirements.txt
PY ?= python3
VENV ?= .venv
XANTO_PRIVE ?=
export XANTO_PRIVE
# SEGSWAP : dossier avec transformer.py (corrigé, voir MODELES.md) et hard_mining_neg5.pth
SEGSWAP ?=
# CODE : dossier des scripts à lancer ; version exacte de l'évaluation : voir REPRODUIRE.md (commit a9bb8a7)
CODE ?= recherche-sources
D = $(XANTO_PRIVE)/recherche-sources

.PHONY: setup verifier-donnees verifier-resultats analyses reproduire-evaluation verifier-tout

setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Environnement prêt : utiliser PY=$(VENV)/bin/python make <cible>"

verifier-donnees:
	$(PY) recherche-sources/verifier_donnees.py

verifier-resultats:
	$(PY) recherche-sources/verifier_resultats.py

verifier-tout: verifier-donnees verifier-resultats

analyses:
	@test -n "$(XANTO_PRIVE)" || { echo "XANTO_PRIVE absente : les fiches complètes sont privées (voir REPRODUIRE.md)."; exit 1; }
	$(PY) analyses/tout.py

# Évaluation finale (RESULTAT_EVALUATION.md) : deux calculs lourds, à lancer UN À LA FOIS (Mac 16 Go).
# Étapes : 1) télécharger les images ; 2) vecteurs et chaîne de base ; 3) chaîne candidate (régions) ; 4) comparer aux CSV publiés.
# Les fichiers produits sont écrits dans $(XANTO_PRIVE)/recherche-sources/, jamais dans resultats/.
reproduire-evaluation:
	@test -n "$(XANTO_PRIVE)" || { echo "XANTO_PRIVE absente (dossier de travail pour les images et les calculs)."; exit 1; }
	@test -n "$(SEGSWAP)" || { echo "SEGSWAP absente (voir MODELES.md)."; exit 1; }
	$(PY) recherche-sources/telecharger_donnees.py $(XANTO_PRIVE)
	cp recherche-sources/resultats/oracle_temoins.csv $(D)/oracle_temoins.csv
	$(PY) $(CODE)/aikon.py $(D) $(SEGSWAP) evaluation facebook/dinov3-vitl16-pretrain-lvd1689m 512
	RECLASSE=region $(PY) $(CODE)/regions.py $(D) $(SEGSWAP) evaluation
	$(PY) recherche-sources/comparer.py $(D)/resultats_aikon_evaluation_dinov3-vitl16-pretrain-lvd1689m_512.csv $(D)/resultats_regions_evaluation_reclasse_region.csv
	@echo "Comparer ensuite aux CSV publiés : cmp / diff avec recherche-sources/resultats/evaluation_*.csv (voir REPRODUIRE.md)."
