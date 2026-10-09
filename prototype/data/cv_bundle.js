// Calculated CV results, separate from historical annotations.
window.MNEMOSYNE_CV = {
  "inputs": {
    "images": [
      {
        "id": "parnassus",
        "image": "assets/parnasse-high.jpg",
        "width": 3658,
        "height": 2832,
        "sha256": "96f427403d318234aa7155099940147a83e3395667fefa11196fc99f22e345e8"
      },
      {
        "id": "apollo",
        "image": "assets/apollo-pan.jpg",
        "width": 570,
        "height": 740,
        "sha256": "f8c272079c4438ec108ec1604ce73645844b07edb5d2dfee07d9a8f830fef9bf"
      },
      {
        "id": "paris",
        "image": "assets/paris-front-high.jpg",
        "width": 4851,
        "height": 4704,
        "sha256": "a4a9cdcabf506a362dcbec9ae15bdfcc598ec75c23a6e9e15de946a68fa2132b"
      }
    ],
    "queries": [
      {
        "id": "apollo-body",
        "source_id": "parnassus",
        "bbox": [
          0.441,
          0.385,
          0.145,
          0.267
        ],
        "provenance": "R\u00e9gion de requ\u00eate fournie depuis le relev\u00e9 assist\u00e9 pr\u00e9existant obs-source-pose ; cette r\u00e9gion n\u2019est pas d\u00e9tect\u00e9e automatiquement."
      }
    ],
    "parameters": {
      "model_id": "facebook/dinov2-base",
      "model_revision": "f9e44c814b77203eaa57a6bdbbd535f21ede1415",
      "max_image_side": 728,
      "top_k": 5,
      "seed": 0,
      "selection_policy": "Param\u00e8tres fix\u00e9s avant inspection des r\u00e9sultats sur les reprises ; pas de r\u00e9glage sur les bo\u00eetes cibles."
    }
  },
  "dino": {
    "schema_version": "1.0",
    "run": {
      "method": "dinov2_spatial_pyramid",
      "method_label": "DINOv2 \u2014 recherche spatiale multi-\u00e9chelle",
      "model_id": "facebook/dinov2-base",
      "model_revision": "f9e44c814b77203eaa57a6bdbbd535f21ede1415",
      "device": "mps",
      "generated_at": "2026-10-07T10:17:26.214666+00:00",
      "duration_seconds": 3.878,
      "input_sha256": "5647efbe6b7edd28a9242a17028c419db37ca5b0dae89d567a1a32fe8c499902",
      "script_sha256": "19aae9afadb5c036a103872713a685f2155795fc981814175596081a55a78532",
      "parameters": {
        "model_id": "facebook/dinov2-base",
        "model_revision": "f9e44c814b77203eaa57a6bdbbd535f21ede1415",
        "max_image_side": 728,
        "top_k": 5,
        "seed": 0,
        "selection_policy": "Param\u00e8tres fix\u00e9s avant inspection des r\u00e9sultats sur les reprises ; pas de r\u00e9glage sur les bo\u00eetes cibles.",
        "algorithm_version": "1.0",
        "height_fractions": [
          0.18,
          0.24,
          0.32,
          0.42,
          0.55,
          0.72
        ],
        "template_levels": [
          1,
          2,
          3
        ],
        "level_weight": "equal; each level averages its cell cosine similarities",
        "scoring": "cosine of concatenated cell descriptors normalized and weighted per level",
        "patch_size": 14,
        "stride_pixels": 14,
        "min_window_pixels": 28,
        "nms_iou": 0.35,
        "window_aspect": "query bbox pixel aspect ratio, rounded to whole patches",
        "mirror_search": false,
        "crop_query_forward": false,
        "feature_layer": "last_hidden_state patch tokens excluding CLS",
        "pixel_normalization": "cached model processor, no automatic resizing or center crop",
        "resize": "PIL bicubic; max side 728 then each side rounded to 14 pixels",
        "precision": "float32",
        "images": {
          "parnassus": {
            "resized_width": 728,
            "resized_height": 560,
            "patch_grid": [
              52,
              40
            ],
            "cache_status": "cache hit",
            "cache_key": "58ff878137fbb069853292d95234c77015336bff21005af890b9d79a394939c7"
          },
          "apollo": {
            "resized_width": 560,
            "resized_height": 728,
            "patch_grid": [
              40,
              52
            ],
            "cache_status": "cache hit",
            "cache_key": "3cc1c6384b43e96e6e61b94377ef73fc50b4be0cb1810c383bbffa3113933d95"
          },
          "paris": {
            "resized_width": 728,
            "resized_height": 700,
            "patch_grid": [
              52,
              50
            ],
            "cache_status": "cache hit",
            "cache_key": "670b2536d6ee9c38fe1fbc8713325f435634ab57dd33c89e4f2c9feb0015f37f"
          }
        },
        "python": "3.12.13",
        "torch": "2.14.0",
        "transformers": "5.17.0"
      },
      "limitations": [
        "R\u00e9gion source fournie par un relev\u00e9 assist\u00e9, pas d\u00e9tect\u00e9e automatiquement.",
        "Aucune bo\u00eete cible, annotation, comparaison ou notice lue par le programme.",
        "Aucun r\u00e9glage effectu\u00e9 apr\u00e8s examen des r\u00e9sultats sur les reprises.",
        "Scores cosinus de descripteurs : ni probabilit\u00e9s ni preuves de filiation historique.",
        "Recherche sur six tailles et une grille de 14 pixels ; r\u00e9gions manqu\u00e9es possibles.",
        "Rapport de forme conserv\u00e9 approximativement ; ni miroir ni d\u00e9formation articul\u00e9e recherch\u00e9s.",
        "Mod\u00e8le g\u00e9n\u00e9rique ; contexte, couleurs, support et r\u00e9solution peuvent influer sur les correspondances.",
        "Trois images dont un contr\u00f4le source ; aucun benchmark ind\u00e9pendant.",
        "Apr\u00e8s le premier calcul, ajout de la seule empreinte du script aux m\u00e9tadonn\u00e9es, puis r\u00e9ex\u00e9cution avec les m\u00eames param\u00e8tres et cartes en cache ; aucun r\u00e9glage des r\u00e9sultats."
      ]
    },
    "queries": [
      {
        "id": "apollo-body",
        "source_id": "parnassus",
        "bbox": [
          0.441,
          0.385,
          0.145,
          0.267
        ],
        "provenance": "R\u00e9gion de requ\u00eate fournie depuis le relev\u00e9 assist\u00e9 pr\u00e9existant obs-source-pose ; cette r\u00e9gion n\u2019est pas d\u00e9tect\u00e9e automatiquement."
      }
    ],
    "results": [
      {
        "query_id": "apollo-body",
        "target_id": "parnassus",
        "method": "dinov2_spatial_pyramid",
        "proposals": [
          {
            "rank": 1,
            "bbox": [
              0.4423076808452606,
              0.4000000059604645,
              0.13461539149284363,
              0.25
            ],
            "score": 0.992074728012085
          },
          {
            "rank": 2,
            "bbox": [
              0.38461539149284363,
              0.30000001192092896,
              0.23076923191547394,
              0.42500001192092896
            ],
            "score": 0.9205498695373535
          },
          {
            "rank": 3,
            "bbox": [
              0.5,
              0.375,
              0.13461539149284363,
              0.25
            ],
            "score": 0.8940215706825256
          },
          {
            "rank": 4,
            "bbox": [
              0.38461539149284363,
              0.42500001192092896,
              0.13461539149284363,
              0.25
            ],
            "score": 0.8936010003089905
          },
          {
            "rank": 5,
            "bbox": [
              0.4038461446762085,
              0.32499998807907104,
              0.13461539149284363,
              0.25
            ],
            "score": 0.8168971538543701
          }
        ],
        "candidate_count": 6392,
        "heatmap": null,
        "notes": [
          "Carte de patches spatiaux DINOv2 ; token CLS exclu.",
          "Image enti\u00e8re redimensionn\u00e9e, sans d\u00e9coupage central ; c\u00f4t\u00e9s arrondis aux multiples de 14.",
          "La carte conserve le contexte global de chaque image : ce ne sont pas des descripteurs de crops isol\u00e9s.",
          "Contr\u00f4le dans l\u2019image source : la requ\u00eate fournie sert \u00e0 construire le gabarit, mais sa bo\u00eete exacte n\u2019est pas inject\u00e9e dans les candidats."
        ]
      },
      {
        "query_id": "apollo-body",
        "target_id": "apollo",
        "method": "dinov2_spatial_pyramid",
        "proposals": [
          {
            "rank": 1,
            "bbox": [
              0.42500001192092896,
              0.36538460850715637,
              0.20000000298023224,
              0.23076923191547394
            ],
            "score": 0.7683719396591187
          },
          {
            "rank": 2,
            "bbox": [
              0.2750000059604645,
              0.32692307233810425,
              0.375,
              0.42307692766189575
            ],
            "score": 0.6804711818695068
          },
          {
            "rank": 3,
            "bbox": [
              0.4000000059604645,
              0.4615384638309479,
              0.15000000596046448,
              0.17307692766189575
            ],
            "score": 0.6649157404899597
          },
          {
            "rank": 4,
            "bbox": [
              0.44999998807907104,
              0.38461539149284363,
              0.30000001192092896,
              0.32692307233810425
            ],
            "score": 0.6601108908653259
          },
          {
            "rank": 5,
            "bbox": [
              0.44999998807907104,
              0.5,
              0.15000000596046448,
              0.17307692766189575
            ],
            "score": 0.618490993976593
          }
        ],
        "candidate_count": 5487,
        "heatmap": null,
        "notes": [
          "Carte de patches spatiaux DINOv2 ; token CLS exclu.",
          "Image enti\u00e8re redimensionn\u00e9e, sans d\u00e9coupage central ; c\u00f4t\u00e9s arrondis aux multiples de 14.",
          "La carte conserve le contexte global de chaque image : ce ne sont pas des descripteurs de crops isol\u00e9s."
        ]
      },
      {
        "query_id": "apollo-body",
        "target_id": "paris",
        "method": "dinov2_spatial_pyramid",
        "proposals": [
          {
            "rank": 1,
            "bbox": [
              0.3461538553237915,
              0.36000001430511475,
              0.2884615361690521,
              0.41999998688697815
            ],
            "score": 0.6844222545623779
          },
          {
            "rank": 2,
            "bbox": [
              0.36538460850715637,
              0.4399999976158142,
              0.1538461595773697,
              0.23999999463558197
            ],
            "score": 0.6531528830528259
          },
          {
            "rank": 3,
            "bbox": [
              0.5961538553237915,
              0.47999998927116394,
              0.1538461595773697,
              0.23999999463558197
            ],
            "score": 0.626111626625061
          },
          {
            "rank": 4,
            "bbox": [
              0.42307692766189575,
              0.5,
              0.1538461595773697,
              0.23999999463558197
            ],
            "score": 0.6232500076293945
          },
          {
            "rank": 5,
            "bbox": [
              0.21153846383094788,
              0.3799999952316284,
              0.2884615361690521,
              0.41999998688697815
            ],
            "score": 0.5991687774658203
          }
        ],
        "candidate_count": 7518,
        "heatmap": null,
        "notes": [
          "Carte de patches spatiaux DINOv2 ; token CLS exclu.",
          "Image enti\u00e8re redimensionn\u00e9e, sans d\u00e9coupage central ; c\u00f4t\u00e9s arrondis aux multiples de 14.",
          "La carte conserve le contexte global de chaque image : ce ne sont pas des descripteurs de crops isol\u00e9s."
        ]
      }
    ]
  },
  "baseline": {
    "schema_version": "1.0",
    "run": {
      "method": "gradient_ncc",
      "method_label": "Gabarit multiechelle : NCC gris et magnitude des gradients",
      "model_id": "none",
      "model_revision": "not-applicable",
      "device": "cpu",
      "generated_at": "2026-10-07T10:16:03.720386+00:00",
      "duration_seconds": 1.272,
      "input_sha256": "5647efbe6b7edd28a9242a17028c419db37ca5b0dae89d567a1a32fe8c499902",
      "script_sha256": "c68775ce7ddc05668abe782bd8819b8c48f000f9705d69a1875055c7b48f3b34",
      "library_versions": {
        "numpy": "2.5.3",
        "scipy": "1.18.1",
        "Pillow": "12.3.0"
      },
      "parameters": {
        "max_image_side": 728,
        "top_k": 5,
        "height_fractions": [
          0.18,
          0.24,
          0.32,
          0.42,
          0.55,
          0.72
        ],
        "stride_pixels": 14,
        "window_quantization_pixels": 14,
        "min_window_side": 28,
        "nms_iou_threshold": 0.35,
        "grayscale_weight": 0.25,
        "sobel_magnitude_weight": 0.75,
        "resize_policy": "Preserve image aspect ratio; round dimensions to pixels, not to patches. This differs slightly from DINO patch-grid resizing.",
        "score_unit": "Weighted normalized cross correlation in [-1, 1]; similarity, not probability.",
        "selection_policy": "Param\u00e8tres fix\u00e9s avant inspection des r\u00e9sultats sur les reprises ; pas de r\u00e9glage sur les bo\u00eetes cibles.",
        "actual_search_grids": {
          "apollo-body:parnassus": {
            "working_size": [
              728,
              564
            ],
            "windows": [
              {
                "requested_height_fraction": 0.18,
                "width": 70,
                "height": 98,
                "positions": 1632
              },
              {
                "requested_height_fraction": 0.24,
                "width": 98,
                "height": 140,
                "positions": 1426
              },
              {
                "requested_height_fraction": 0.32,
                "width": 126,
                "height": 182,
                "positions": 1232
              },
              {
                "requested_height_fraction": 0.42,
                "width": 168,
                "height": 238,
                "positions": 984
              },
              {
                "requested_height_fraction": 0.55,
                "width": 210,
                "height": 308,
                "positions": 722
              },
              {
                "requested_height_fraction": 0.72,
                "width": 280,
                "height": 406,
                "positions": 396
              }
            ]
          },
          "apollo-body:apollo": {
            "working_size": [
              561,
              728
            ],
            "windows": [
              {
                "requested_height_fraction": 0.18,
                "width": 84,
                "height": 126,
                "positions": 1540
              },
              {
                "requested_height_fraction": 0.24,
                "width": 112,
                "height": 168,
                "positions": 1353
              },
              {
                "requested_height_fraction": 0.32,
                "width": 168,
                "height": 238,
                "positions": 1044
              },
              {
                "requested_height_fraction": 0.42,
                "width": 210,
                "height": 308,
                "positions": 806
              },
              {
                "requested_height_fraction": 0.55,
                "width": 280,
                "height": 406,
                "positions": 504
              },
              {
                "requested_height_fraction": 0.72,
                "width": 364,
                "height": 518,
                "positions": 240
              }
            ]
          },
          "apollo-body:paris": {
            "working_size": [
              728,
              706
            ],
            "windows": [
              {
                "requested_height_fraction": 0.18,
                "width": 84,
                "height": 126,
                "positions": 1974
              },
              {
                "requested_height_fraction": 0.24,
                "width": 112,
                "height": 168,
                "positions": 1755
              },
              {
                "requested_height_fraction": 0.32,
                "width": 154,
                "height": 224,
                "positions": 1470
              },
              {
                "requested_height_fraction": 0.42,
                "width": 210,
                "height": 294,
                "positions": 1140
              },
              {
                "requested_height_fraction": 0.55,
                "width": 280,
                "height": 392,
                "positions": 759
              },
              {
                "requested_height_fraction": 0.72,
                "width": 350,
                "height": 504,
                "positions": 420
              }
            ]
          }
        }
      },
      "limitations": [
        "Appearance baseline sensitive to medium, pose, illumination and framing changes.",
        "Aspect ratio follows query, rounded to the fixed 14-pixel grid.",
        "Not a model of body articulation, narrative meaning or historical transmission.",
        "No fitting or parameter selection using target references."
      ]
    },
    "queries": [
      {
        "id": "apollo-body",
        "source_id": "parnassus",
        "bbox": [
          0.441,
          0.385,
          0.145,
          0.267
        ],
        "provenance": "R\u00e9gion de requ\u00eate fournie depuis le relev\u00e9 assist\u00e9 pr\u00e9existant obs-source-pose ; cette r\u00e9gion n\u2019est pas d\u00e9tect\u00e9e automatiquement."
      }
    ],
    "results": [
      {
        "query_id": "apollo-body",
        "target_id": "parnassus",
        "method": "gradient_ncc",
        "proposals": [
          {
            "bbox": [
              0.4423076923076923,
              0.3971631205673759,
              0.1346153846153846,
              0.24822695035460993
            ],
            "score": 0.1682925589459817,
            "rank": 1
          },
          {
            "bbox": [
              0.5576923076923077,
              0.3723404255319149,
              0.28846153846153844,
              0.5460992907801419
            ],
            "score": 0.07873794673895346,
            "rank": 2
          },
          {
            "bbox": [
              0.3269230769230769,
              0.4219858156028369,
              0.09615384615384616,
              0.17375886524822695
            ],
            "score": 0.0782489257829371,
            "rank": 3
          },
          {
            "bbox": [
              0.5384615384615384,
              0.4716312056737589,
              0.09615384615384616,
              0.17375886524822695
            ],
            "score": 0.07692825296421657,
            "rank": 4
          },
          {
            "bbox": [
              0.8269230769230769,
              0.0,
              0.09615384615384616,
              0.17375886524822695
            ],
            "score": 0.07666495047089403,
            "rank": 5
          }
        ],
        "candidate_count": 6392,
        "heatmap": null,
        "notes": [
          "NCC similarity, not a probability; all grid candidates searched.",
          "No mirror, rotation or perspective correction.",
          "Source image is a technical control; query box was not inserted among candidates."
        ]
      },
      {
        "query_id": "apollo-body",
        "target_id": "apollo",
        "method": "gradient_ncc",
        "proposals": [
          {
            "bbox": [
              0.5490196078431373,
              0.4423076923076923,
              0.1497326203208556,
              0.17307692307692307
            ],
            "score": 0.07730940664740699,
            "rank": 1
          },
          {
            "bbox": [
              0.3493761140819964,
              0.3076923076923077,
              0.2994652406417112,
              0.3269230769230769
            ],
            "score": 0.07721661196877884,
            "rank": 2
          },
          {
            "bbox": [
              0.37433155080213903,
              0.19230769230769232,
              0.19964349376114082,
              0.23076923076923078
            ],
            "score": 0.07236876210791196,
            "rank": 3
          },
          {
            "bbox": [
              0.3493761140819964,
              0.15384615384615385,
              0.1497326203208556,
              0.17307692307692307
            ],
            "score": 0.07021504147397703,
            "rank": 4
          },
          {
            "bbox": [
              0.6488413547237076,
              0.21153846153846154,
              0.19964349376114082,
              0.23076923076923078
            ],
            "score": 0.06954147853486714,
            "rank": 5
          }
        ],
        "candidate_count": 5487,
        "heatmap": null,
        "notes": [
          "NCC similarity, not a probability; all grid candidates searched.",
          "No mirror, rotation or perspective correction.",
          "Target reference boxes were not read."
        ]
      },
      {
        "query_id": "apollo-body",
        "target_id": "paris",
        "method": "gradient_ncc",
        "proposals": [
          {
            "bbox": [
              0.6923076923076923,
              0.17847025495750707,
              0.11538461538461539,
              0.17847025495750707
            ],
            "score": 0.08342123760060427,
            "rank": 1
          },
          {
            "bbox": [
              0.5961538461538461,
              0.11898016997167139,
              0.15384615384615385,
              0.23796033994334279
            ],
            "score": 0.0796559913782397,
            "rank": 2
          },
          {
            "bbox": [
              0.5576923076923077,
              0.45609065155807366,
              0.21153846153846154,
              0.31728045325779036
            ],
            "score": 0.07793208660312956,
            "rank": 3
          },
          {
            "bbox": [
              0.4807692307692308,
              0.07932011331444759,
              0.11538461538461539,
              0.17847025495750707
            ],
            "score": 0.07387589019266952,
            "rank": 4
          },
          {
            "bbox": [
              0.5576923076923077,
              0.09915014164305949,
              0.11538461538461539,
              0.17847025495750707
            ],
            "score": 0.07366144241986188,
            "rank": 5
          }
        ],
        "candidate_count": 7518,
        "heatmap": null,
        "notes": [
          "NCC similarity, not a probability; all grid candidates searched.",
          "No mirror, rotation or perspective correction.",
          "Target reference boxes were not read."
        ]
      }
    ]
  },
  "evaluation": {
    "reference_status": "Bo\u00eetes approximatives pr\u00e9existantes du relev\u00e9 assist\u00e9, non valid\u00e9es par un annotateur humain ind\u00e9pendant.",
    "metrics_definition": {
      "top1_iou": "Area of intersection divided by area of union for the highest-similarity proposal and approximate reference; range 0 to 1.",
      "best_top5_iou": "Maximum IoU among the first five proposals already saved after NMS; evaluation does not reorder predictions.",
      "best_top5_rank": "Original similarity rank of maximum-IoU proposal; first rank wins ties. It does not select a new prediction.",
      "top1_center_inside": "Whether the center of the top similarity proposal lies in the reference rectangle, including its boundary.",
      "input_sha256_verified": "5647efbe6b7edd28a9242a17028c419db37ca5b0dae89d567a1a32fe8c499902",
      "prediction_file_sha256": {
        "baseline_results.json": "467b06f94f1abf29d3ea2dc66421ef3a998b1bb4a3ff3bd23d647127a9975865",
        "results.json": "2430b4f943375ad0c07a113490fa8c31b3e866cad5fdb4309742069c8c64f5ee"
      },
      "reference_file_sha256": "33e30329fcd54c9234b03f520282fb206505d5bcdfb955301bfe9699ba980ddf",
      "evaluation_script_sha256": "50a220d93abf7f87d7d1de6783a15b71cccb3456613c5977f773c98d920b80b8"
    },
    "results": [
      {
        "target_id": "parnassus",
        "method": "gradient_ncc",
        "reference_bbox": [
          0.441,
          0.385,
          0.145,
          0.267
        ],
        "top1_iou": 0.8631064547046308,
        "best_top5_iou": 0.8631064547046308,
        "best_top5_rank": 1,
        "top1_center_inside": true
      },
      {
        "target_id": "apollo",
        "method": "gradient_ncc",
        "reference_bbox": [
          0.395,
          0.331,
          0.241,
          0.271
        ],
        "top1_iou": 0.17960678742038166,
        "best_top5_iou": 0.6671052142857147,
        "best_top5_rank": 2,
        "top1_center_inside": true
      },
      {
        "target_id": "paris",
        "method": "gradient_ncc",
        "reference_bbox": [
          0.518,
          0.438,
          0.239,
          0.343
        ],
        "top1_iou": 0.0,
        "best_top5_iou": 0.7365270719625289,
        "best_top5_rank": 3,
        "top1_center_inside": false
      },
      {
        "target_id": "parnassus",
        "method": "dinov2_spatial_pyramid",
        "reference_bbox": [
          0.441,
          0.385,
          0.145,
          0.267
        ],
        "top1_iou": 0.8692715452204807,
        "best_top5_iou": 0.8692715452204807,
        "best_top5_rank": 1,
        "top1_center_inside": true
      },
      {
        "target_id": "apollo",
        "method": "dinov2_spatial_pyramid",
        "reference_bbox": [
          0.395,
          0.331,
          0.241,
          0.271
        ],
        "top1_iou": 0.7066780032588796,
        "best_top5_iou": 0.7066780032588796,
        "best_top5_rank": 1,
        "top1_center_inside": true
      },
      {
        "target_id": "paris",
        "method": "dinov2_spatial_pyramid",
        "reference_bbox": [
          0.518,
          0.438,
          0.239,
          0.343
        ],
        "top1_iou": 0.24430542385740553,
        "best_top5_iou": 0.4504077664866195,
        "best_top5_rank": 3,
        "top1_center_inside": false
      }
    ],
    "limitations": [
      "Approximate references come from pre-existing assistant-assisted annotation, not an independent human benchmark.",
      "The source control reuses the supplied query; it tests implementation, not generalization.",
      "Only two target works are evaluated. No aggregate accuracy, historical conclusion or model ranking is justified.",
      "Box overlap does not evaluate identity, hand contacts, narrative action or historical transmission.",
      "Similarity scores are not probabilities and are not calibrated across methods.",
      "Both methods use the same six height fractions, 14-pixel window grid and NMS 0.35; image and query preprocessing differ."
    ]
  },
  "controls": {
    "schema_version": "1.0",
    "diagnostic_status": "post_hoc_evaluation_only",
    "reference_status": "Bo\u00eetes approximatives pr\u00e9existantes du relev\u00e9 assist\u00e9, non valid\u00e9es par un annotateur humain ind\u00e9pendant.",
    "run": {
      "generated_at": "2026-10-07T10:21:31.815952+00:00",
      "input_sha256": "5647efbe6b7edd28a9242a17028c419db37ca5b0dae89d567a1a32fe8c499902",
      "reference_sha256": "33e30329fcd54c9234b03f520282fb206505d5bcdfb955301bfe9699ba980ddf",
      "script_sha256": "4ad8c5d23d82d3feef8d921d22f537af38d0ffcadf529d9e88d6ce3db95c45a4",
      "numpy_version": "2.5.3",
      "seed": 0,
      "random_generator": "numpy.default_rng / PCG64",
      "random_draw_count_per_target": 10000,
      "sampling": "Top-left coordinates uniform over [0, 1-width] x [0, 1-height]; same normalized draws reused for every target.",
      "size_policy": "Width and height equal the supplied primary query bbox fractions in each target image; no size fitting to references.",
      "percentile_method": "numpy.percentile, linear"
    },
    "query_id": "apollo-body",
    "source_id": "parnassus",
    "query_bbox": [
      0.441,
      0.385,
      0.145,
      0.267
    ],
    "results": [
      {
        "query_id": "apollo-body",
        "target_id": "parnassus",
        "box": [
          0.4275,
          0.3665,
          0.145,
          0.267
        ],
        "center_iou": 0.7301923366981545,
        "normalized_box_size": [
          0.145,
          0.267
        ],
        "random_draw_count": 10000,
        "random_iou": {
          "p50": 0.0,
          "p90": 0.14720516491396293,
          "p95": 0.28581880930905534,
          "p99": 0.560714822196264,
          "max": 0.9251914447307429
        }
      },
      {
        "query_id": "apollo-body",
        "target_id": "apollo",
        "box": [
          0.4275,
          0.3665,
          0.145,
          0.267
        ],
        "center_iou": 0.4886696194108349,
        "normalized_box_size": [
          0.145,
          0.267
        ],
        "random_draw_count": 10000,
        "random_iou": {
          "p50": 0.0,
          "p90": 0.19419046967373504,
          "p95": 0.31521044799170606,
          "p99": 0.5211668810080916,
          "max": 0.592779164306166
        }
      },
      {
        "query_id": "apollo-body",
        "target_id": "paris",
        "box": [
          0.4275,
          0.3665,
          0.145,
          0.267
        ],
        "center_iou": 0.09682857396018162,
        "normalized_box_size": [
          0.145,
          0.267
        ],
        "random_draw_count": 10000,
        "random_iou": {
          "p50": 0.0,
          "p90": 0.20730233747672638,
          "p95": 0.31969164088508123,
          "p99": 0.47226661136660275,
          "max": 0.47226661136660303
        }
      }
    ],
    "limitations": [
      "Post-hoc descriptive diagnostic using the existing approximate reference boxes; no localization program or prediction is changed.",
      "This is not a p-value or a calibrated significance test.",
      "A single uniform random box is not comparable to selecting the highest-scoring proposal from thousands of searched windows.",
      "The random boxes have one fixed relative size; the localization algorithms search multiple scales and have different image preprocessing.",
      "The empirical maximum is only the largest overlap among these 10000 draws, not a theoretical maximum.",
      "The source reference repeats the query. Two target works and approximate assisted references do not form an independent benchmark."
    ]
  }
};
