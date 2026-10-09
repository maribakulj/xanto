#!/usr/bin/env python3
"""Download the three reference images into assets/ and check their SHA-256.

The images are not stored in the repository (museum licences: Met Open Access,
Fitzwilliam CC BY-NC-ND). URLs and expected checksums come from data/corpus.json
and cv/inputs.json.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "Mozilla/5.0 (xanto prototype; research use)"}


def main():
    corpus = json.loads((ROOT / "data/corpus.json").read_text())
    expected = {item["id"]: item["sha256"] for item in json.loads((ROOT / "cv/inputs.json").read_text())["images"]}
    (ROOT / "assets").mkdir(exist_ok=True)
    for item in corpus:
        target = ROOT / item["image"]
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected[item["id"]]:
            print(f"{item['id']}: déjà présent")
            continue
        request = urllib.request.Request(item["image_url"], headers=HEADERS)
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        target.write_bytes(data)
        status = "empreinte conforme" if digest == expected[item["id"]] else f"EMPREINTE DIFFÉRENTE ({digest}) : le musée a pu changer le fichier ; les repères et résultats CV ne s'appliquent plus tels quels"
        print(f"{item['id']}: {target.relative_to(ROOT)} — {status}")


if __name__ == "__main__":
    main()
