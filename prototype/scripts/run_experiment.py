"""Execute both localization methods, then evaluate and package their predictions."""
import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def default_python():
    if importlib.util.find_spec("torch") and importlib.util.find_spec("PIL"):
        return sys.executable
    existing = ROOT.parent / "caypollard" / ".venv" / "bin" / "python"
    return str(existing) if existing.is_file() else sys.executable


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=default_python(), help="Python disposant de torch, transformers, numpy, scipy et Pillow")
    args = parser.parse_args()
    environment = dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    for script in ("run_cv.py", "cv_baseline.py", "evaluate_cv.py", "trivial_controls.py", "build_cv_bundle.py"):
        print(f"Exécution : {script}", flush=True)
        subprocess.run([args.python, str(ROOT / "scripts" / script)], cwd=ROOT, env=environment, check=True)
    print("Résultats calculés, évalués et intégrés. Rechargez la page locale.")
