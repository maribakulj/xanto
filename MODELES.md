# Modèles utilisés

Aucun poids n'est publié dans ce dépôt. Les révisions ci-dessous sont celles du cache Hugging Face de la machine qui a produit les résultats (fichier `refs/main` au 23/10/2026). Pour les retrouver exactement : `from_pretrained("<modèle>", revision="<révision>")`, ou `hf download <modèle> --revision <révision>`.

| Modèle | Rôle | Révision | Licence | Scripts |
|---|---|---|---|---|
| `facebook/dinov3-vitl16-pretrain-lvd1689m` (DINOv3 ViT-L/16) | **modèle de l'évaluation finale** : vecteurs de l'image entière (512 px) et des régions (384 px) | `ea8dc2863c51be0a264bab82070e3e8836b02d51` | licence DINOv3 de Meta (« dinov3-license ») ; accès restreint | `chercher.py`, `regions.py`, `galerie_plus_vecteurs.py`, `aikon.py` |
| `facebook/dinov3-vitb16-pretrain-lvd1689m` (DINOv3 ViT-B/16) | comparaison de mise au point (`RESULTAT_DINOV3.md`) | `5931719e67bbdb9737e363e781fb0c67687896bc` | idem | `aikon.py` |
| `facebook/dinov2-base` | premières étapes et comparaisons de mise au point | `f9e44c814b77203eaa57a6bdbbd535f21ede1415` | Apache 2.0 | `recherche.py`, `etape2.py`, `aikon.py` |
| `IDEA-Research/grounding-dino-base` | détection des « personnes » dans les estampes (régions candidates) | `12bdfa3120f3e7ec7b434d90674b3396eccf88eb` | Apache 2.0 | `oracle_detection.py`, `galerie_plus_vecteurs.py` |
| SegSwap, poids `hard_mining_neg5.pth` | reclassement des 20 premières candidates | pas de révision : fichier de 43 380 993 octets, SHA-256 `0ed5c99917ab11d579833f18f7e1c3885e711398452148e8ae4f48580fbec690` | MIT | `aikon.py`, `regions.py`, `chercher.py` |

## Comment les obtenir

**DINOv3.** Les poids sont à accès restreint : il faut un compte Hugging Face, ouvrir la page du modèle (`https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m`), lire et accepter soi-même la licence de Meta, puis se connecter (`hf auth login`) avant de télécharger. Ne pas les redistribuer, ni les copier dans le dépôt, ni les verser dans un jeu de données partagé.

**DINOv2 et Grounding DINO.** Accès libre : téléchargement automatique par `transformers` au premier lancement.

**SegSwap.** Code et poids viennent du dépôt d'origine `XiSHEN0220/SegSwap` (MIT) ; les poids utilisés sont `hard_mining_neg5.pth` (vérifier l'empreinte ci-dessus). Les scripts attendent un dossier contenant `transformer.py` et `hard_mining_neg5.pth` (argument `<dossier_segswap>`). Le `transformer.py` d'origine appelle `torch.cuda.BoolTensor`, ce qui échoue sans carte NVIDIA : nous l'avons modifié (quatre lignes, sans changer le calcul). La modification est fournie sous forme de correctif :

```
cp SegSwap/transformer.py <dossier_segswap>/transformer.py     # fichier d'origine (SHA-256 4f09b234f4e1d988db13b5f6e9659e640e6af2cb4f8b828f69f3dbfc33b26611)
cd <dossier_segswap> && patch -p1 < <depot>/recherche-sources/segswap_transformer.patch
cp SegSwap/hard_mining_neg5.pth <dossier_segswap>/
```

## Environnement

Python 3.12.13 ; versions des bibliothèques dans `requirements.txt`. Calcul sur Mac (puce Apple, 16 Go, GPU « mps ») : les scores peuvent différer très légèrement d'un matériel ou d'une version de PyTorch à l'autre ; les rangs publiés dans `resultats/*.csv` sont ceux de cette machine. Le script `verifier_resultats.py` ne contrôle que les CSV publiés, pas un recalcul.
