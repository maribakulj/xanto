#!/usr/bin/env python3
"""Mode assistant de la page d'annotation : sert le paquet sur http://127.0.0.1:8765 et ajoute trois aides.

Usage :
  ~/caypollard/.venv/bin/python annotation/assistant.py <dossier_du_paquet> [--port 8765]

Aides (chaque recours est inscrit dans la réponse de l'annotateur, champ « aides ») :
  /api/carte    : où la figure du plat se trouve probablement dans l'estampe (DINOv3-B, correspondance des
                  vecteurs de patchs, figure prise telle quelle et retournée ; calcul local) ;
  /api/encadrer : rectangle autour de l'objet cliqué (SlimSAM, calcul local) ;
  /api/claude   : question à Claude (commande `claude -p`, compte déjà connecté dans le terminal, aucune clé) ;
                  envoie les deux découpes et la phrase de la fiche à Anthropic.
Les modèles ne sont chargés qu'au premier appel. Le serveur n'écoute que sur 127.0.0.1."""
import argparse, base64, io, json, os, subprocess, sys, tempfile, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ap = argparse.ArgumentParser(); ap.add_argument("paquet"); ap.add_argument("--port", type=int, default=8765)
A = ap.parse_args()
P = Path(A.paquet).expanduser().resolve()
if not (P / "index.html").exists() or not (P / "data.js").exists():
    sys.exit(f"{P} ne contient pas de paquet (index.html, data.js) : lancer d'abord annotation/preparer.py")
DEV = os.environ.get("DEV", "cpu")
PAGE = Path(__file__).resolve().parent / "page"
VERROU = threading.Lock(); M = {}


def image(src):
    """Vignette du paquet (chemin relatif img/…), refusée hors du paquet."""
    f = (P / src).resolve()
    if P not in f.parents or not f.is_file():
        raise ValueError("image hors du paquet")
    return Image.open(f).convert("RGB")


def vers_vignette(box, inf):
    """Rectangle en pixels de l'image originale -> pixels de la vignette."""
    sx, sy = inf["tw"] / inf["ow"], inf["th"] / inf["oh"]
    return [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy]


def vers_original(box, inf):
    sx, sy = inf["ow"] / inf["tw"], inf["oh"] / inf["th"]
    return [round(box[0] * sx), round(box[1] * sy), round(box[2] * sx), round(box[3] * sy)]


def png64(im):
    b = io.BytesIO(); im.save(b, "PNG"); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


# ---- carte : correspondance des patchs DINOv3
def dino():
    if "dino" not in M:
        import torch
        from transformers import AutoModel
        M["torch"] = torch
        M["dino"] = AutoModel.from_pretrained("facebook/dinov3-vitb16-pretrain-lvd1689m").to(DEV).eval()
    return M["dino"], M["torch"]


def patchs(im, cote):
    """Vecteurs normalisés des patchs 16 px, image réduite pour que son grand côté fasse `cote` px."""
    model, torch = dino()
    s = cote / max(im.size); w, h = max(16, round(im.width * s / 16) * 16), max(16, round(im.height * s / 16) * 16)
    x = (np.asarray(im.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    x = torch.from_numpy(x.transpose(2, 0, 1)[None].astype(np.float32)).to(DEV)
    with torch.no_grad():
        t = model(pixel_values=x).last_hidden_state[0, 1 + model.config.num_register_tokens:]
    return torch.nn.functional.normalize(t, dim=-1).cpu().numpy(), h // 16, w // 16


def carte(q):
    plat, est = image(q["plat"]["src"]), image(q["estampe"]["src"])
    b = vers_vignette(q["box_plat"], q["plat"]); fig = plat.crop(tuple(int(v) for v in b))
    E, gh, gw = patchs(est, 768)
    meilleur = None
    for sens, f in (("tel quel", fig), ("miroir", ImageOps.mirror(fig))):
        F, _, _ = patchs(f, 384)
        s = E @ F.T                                       # patchs de l'estampe x patchs de la figure
        # pour chaque patch de la figure, son meilleur patch dans l'estampe vote ; plus un léger fond (max par patch)
        votes = np.zeros(len(E)); np.add.at(votes, s.argmax(0), s.max(0))
        m = 0.5 * votes / (votes.max() + 1e-9) + 0.5 * np.clip((s.max(1) - 0.2) / 0.5, 0, 1)
        m = m.reshape(gh, gw)
        qualite = float(s.max(0).mean())                  # ressemblance moyenne de chaque patch de la figure à son meilleur patch
        if meilleur is None or qualite > meilleur[2]:
            meilleur = (sens, m, qualite)
    sens, m, _ = meilleur
    from scipy.ndimage import gaussian_filter
    m = gaussian_filter(m, 1.0); m = (m - m.min()) / (m.max() - m.min() + 1e-9)
    # rectangle proposé : zone chaude d'un seul tenant (carte > 0,7) qui contient le maximum
    from scipy.ndimage import label
    lab, _ = label(m > 0.7); ys, xs = np.nonzero(lab == lab[np.unravel_index(m.argmax(), m.shape)])
    sx, sy = est.width / gw, est.height / gh
    box = [xs.min() * sx, ys.min() * sy, (xs.max() + 1) * sx, (ys.max() + 1) * sy]
    rgba = np.zeros((gh, gw, 4), np.uint8); rgba[..., 0] = 255; rgba[..., 1] = (60 + 140 * (1 - m)).astype(np.uint8)
    rgba[..., 3] = (200 * np.clip((m - 0.35) / 0.65, 0, 1)).astype(np.uint8)
    return {"carte": png64(Image.fromarray(rgba, "RGBA")), "sens": sens,
            "box": vers_original(box, q["estampe"]), "note": "contour de la zone la plus chaude"}


# ---- encadrer d'un clic : SlimSAM
def encadrer(q):
    if "sam" not in M:
        from transformers import SamModel, SamProcessor
        M["samp"] = SamProcessor.from_pretrained("Zigeng/SlimSAM-uniform-77")
        M["sam"] = SamModel.from_pretrained("Zigeng/SlimSAM-uniform-77").to(DEV).eval()
    import torch
    im = image(q["image"]["src"]); x, y = q["point"][0] * im.width / q["image"]["ow"], q["point"][1] * im.height / q["image"]["oh"]
    inp = M["samp"](im, input_points=[[[x, y]]], return_tensors="pt").to(DEV)
    with torch.no_grad():
        out = M["sam"](**inp)
    masks = M["samp"].image_processor.post_process_masks(out.pred_masks.cpu(), inp["original_sizes"].cpu(), inp["reshaped_input_sizes"].cpu())[0][0]
    scores = out.iou_scores[0, 0].cpu().numpy()
    props = []
    for k in np.argsort(-scores):
        ys, xs = np.nonzero(masks[k].numpy())
        if len(xs) < 20: continue
        props.append({"box": vers_original([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1], q["image"]), "score": round(float(scores[k]), 2)})
    return {"propositions": props}


# ---- question à Claude
CONSIGNE = """Tu aides un historien de l'art à annoter des emprunts de Xanto Avelli (majolique d'Urbino) aux estampes.
Lis les images {plat} (figure découpée sur le plat) et {est} (estampe{sens}).
{phrase}
Question de l'annotateur : {question}
Réponds en français, en 5 lignes au plus : quelle figure de l'estampe correspond (position dans l'image : gauche/centre/droite,
haut/bas), est-elle inversée, quelles parties sont reprises, et ce qui reste incertain. Ne devine pas : si ce n'est pas la même figure, dis-le."""


def claude(q):
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); plat, est = image(q["plat"]["src"]), image(q["estampe"]["src"])
        if q.get("box_plat"): plat = plat.crop(tuple(int(v) for v in vers_vignette(q["box_plat"], q["plat"])))
        if q.get("box_estampe"): est = est.crop(tuple(int(v) for v in vers_vignette(q["box_estampe"], q["estampe"])))
        plat.save(t / "plat.jpg", quality=88); est.save(t / "estampe.jpg", quality=88)
        txt = CONSIGNE.format(plat=t / "plat.jpg", est=t / "estampe.jpg", sens=", zone tracée par l'annotateur" if q.get("box_estampe") else " entière",
                              phrase=f"La fiche du catalogue dit : « {q['phrase']} »" if q.get("phrase") else "",
                              question=q.get("question") or "à quelle figure de l'estampe correspond la figure du plat ?")
        r = subprocess.run(["claude", "-p", txt, "--model", "sonnet", "--allowedTools", "Read", "--add-dir", str(t), "--output-format", "json"],
                           capture_output=True, text=True, timeout=300, cwd=t)
    if r.returncode:
        raise RuntimeError("claude -p a échoué : " + (r.stderr or r.stdout)[-400:])
    return {"texte": json.loads(r.stdout).get("result", "").strip()}


API = {"/api/carte": carte, "/api/encadrer": encadrer, "/api/claude": claude}


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(P), **k)
    def translate_path(self, path):
        # la page (index.html, app.js, style.css) vient du dépôt, pour profiter des mises à jour sans regénérer le paquet
        nom = path.split("?")[0].lstrip("/") or "index.html"
        return str(PAGE / nom) if (PAGE / nom).is_file() and "/" not in nom else super().translate_path(path)
    def log_message(self, fmt, *a):
        if "/api/" in (a[0] if a else ""): sys.stderr.write(fmt % a + "\n")
    def envoyer(self, code, o):
        b = json.dumps(o, ensure_ascii=False).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == "/api/etat":
            return self.envoyer(200, {"aides": ["carte", "encadrer", "claude"]})
        return super().do_GET()
    def do_POST(self):
        f = API.get(self.path)
        if not f or self.headers.get("Origin", f"http://127.0.0.1:{A.port}") not in (f"http://127.0.0.1:{A.port}", f"http://localhost:{A.port}"):
            return self.envoyer(404, {"erreur": "inconnu"})
        try:
            q = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if f is claude: r = f(q)                       # n'utilise pas la mémoire du Mac, pas besoin d'attendre
            else:
                with VERROU: r = f(q)                       # un seul calcul local à la fois
            self.envoyer(200, r)
        except Exception as e:
            self.envoyer(500, {"erreur": f"{type(e).__name__} : {e}"})


print(f"Assistant prêt : ouvrir http://127.0.0.1:{A.port}/  (Ctrl+C pour arrêter)")
ThreadingHTTPServer(("127.0.0.1", A.port), H).serve_forever()
