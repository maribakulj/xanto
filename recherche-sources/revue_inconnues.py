#!/usr/bin/env python3
"""Page de revue privée (PROTOCOLE_INCONNUES.md) : pour chaque requête, la figure du plat et les 10 estampes proposées,
avec la région qui a fait remonter l'estampe ; boutons oui / peut-être / non gardés dans le navigateur, export CSV.
Vignettes dans le dossier <sortie>_images à côté de la page ; elles contiennent des photos de plats, à garder en privé (Drive).
Usage : revue_inconnues.py <dossier_prive> <candidats.csv> <requetes.csv> <sortie.html>"""
import csv, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
D = Path(sys.argv[1]).resolve(); Image.MAX_IMAGE_PIXELS = None
cands = list(csv.DictReader(open(sys.argv[2]))); reqs = list(csv.DictReader(open(sys.argv[3])))
meta = {f"met:{r['object_id']}": r for r in csv.DictReader(open(D / "recherche-sources" / "galerie_met.csv"))}
OUT = Path(sys.argv[4]).resolve(); IMG = OUT.parent / (OUT.stem + "_images"); IMG.mkdir(parents=True, exist_ok=True); NIMG = [0]
def b64(im, side):
    """Enregistre une vignette à côté de la page et renvoie son chemin relatif."""
    im = im.convert("RGB"); im.thumbnail((side, side)); NIMG[0] += 1; f = IMG / f"{NIMG[0]:05d}.jpg"; im.save(f, "JPEG", quality=80)
    return f"{IMG.name}/{f.name}"
def gpath(img): p = D / "recherche-sources" / img; return p if p.exists() else D / "recherche-sources" / "connues" / img.split("/")[-1]
data = []
for q in reqs:
    ph = Image.open(D / "corpus-images" / "rovigo" / q["photo"])
    box = tuple(int(float(q[k])) for k in ("x0", "y0", "x1", "y1"))
    item = {"id": q["requete"], "groupe": q["groupe"], "plat": q["plat_id"], "type": q["type"], "fig": b64(ph.crop(box), 360), "cands": []}
    for c in [c for c in cands if c["requete"] == q["requete"]]:
        g = Image.open(gpath(c["image"])).convert("RGB"); reg = c["region"]
        crop = g.crop(tuple(int(v) for v in reg.split(","))) if reg else g
        if c["sens"] == "miroir": crop = ImageOps.mirror(crop)
        full = g.copy(); full.thumbnail((360, 360))
        if reg:
            s = full.width / g.width; d = ImageDraw.Draw(full)
            d.rectangle([int(v) * s for v in reg.split(",")], outline=(220, 30, 30), width=3)
        m = meta.get(c["composition"], {}); oid = c["composition"].split(":")[1] if c["composition"].startswith("met:") else ""
        item["cands"].append({"rang": c["rang"], "comp": c["composition"], "score": c["score_segswap"], "sens": c["sens"],
                              "titre": m.get("titre", c["image"].split("/")[-1])[:160], "artiste": m.get("artiste", ""), "date": m.get("date", ""),
                              "lien": f"https://www.metmuseum.org/art/collection/search/{oid}" if oid else "",
                              "zoom": b64(crop, 300) if reg else "", "full": b64(full, 360)})
    data.append(item)
page = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revue des sources</title><style>
:root{--bg:#faf8f4;--fg:#222;--mut:#666;--card:#fff;--line:#ddd;--a:#1a4fa0;--oui:#2e7d32;--pe:#b26a00;--non:#999}
@media (prefers-color-scheme:dark){:root{--bg:#1b1a18;--fg:#eee;--mut:#aaa;--card:#262522;--line:#444;--a:#8ab4ff}}
a{color:var(--a)}
body{background:var(--bg);color:var(--fg);font:15px/1.4 system-ui,sans-serif;margin:0;padding:16px}
h1{font-size:20px;margin:0 0 4px} .mut{color:var(--mut);font-size:13px}
.req{border-top:2px solid var(--line);padding:14px 0;display:grid;grid-template-columns:260px 1fr;gap:14px}
.req img.fig{max-width:250px;border:1px solid var(--line)} .cands{display:flex;flex-wrap:wrap;gap:10px}
.c{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px;width:300px}
.c img{max-width:100%;max-height:230px;display:block;margin:2px auto} .c .t{font-size:12px;min-height:32px}
.b button{margin:3px 3px 0 0;padding:4px 9px;border:1px solid var(--line);border-radius:4px;background:transparent;color:var(--fg);cursor:pointer}
.b button.on[data-v=oui]{background:var(--oui);color:#fff}.b button.on[data-v=peut-etre]{background:var(--pe);color:#fff}.b button.on[data-v=non]{background:var(--non);color:#fff}
.bar{position:sticky;top:0;background:var(--bg);padding:6px 0;z-index:2;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
@media (max-width:700px){.req{grid-template-columns:1fr}.c{width:100%}}
</style></head><body>
<h1>Revue des sources proposées</h1>
<div class="mut">Figure du plat à gauche (scène entière si « composition ») ; à droite les 10 estampes proposées : la région qui l'a fait remonter (agrandie, retournée si « miroir »), puis l'estampe entière avec cette région en rouge.
<b>oui</b> = même figure, même pose, au moins un détail non nécessaire repris ; <b>peut-être</b> = même pose générale sans détail probant ; <b>non</b> = autre chose. Les choix restent dans ce navigateur ; « Exporter » les enregistre en CSV.</div>
<div class="bar"><select id="f"><option value="">tous les plats</option><option>sans_source</option><option>invention</option><option>temoin</option></select>
<button id="x">Exporter (CSV)</button><span id="n" class="mut"></span></div><div id="root"></div>
<script>
const DATA=__DATA__;let J={};try{J=JSON.parse(localStorage.getItem('revue_inconnues')||'{}')}catch(e){}
function save(){try{localStorage.setItem('revue_inconnues',JSON.stringify(J))}catch(e){};document.getElementById('n').textContent=Object.keys(J).length+' jugements'}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function draw(){const f=document.getElementById('f').value;document.getElementById('root').innerHTML=DATA.filter(r=>!f||r.groupe==f).map(r=>`<div class="req"><div><b>${r.id}</b> <span class="mut">${r.groupe} · ${r.type}</span><br><img class="fig" src="${r.fig}"></div><div class="cands">${r.cands.map(c=>{const k=r.id+'|'+c.comp;return `<div class="c"><div class="t"><b>${c.rang}.</b> ${c.lien?`<a href="${c.lien}" target="_blank" rel="noopener">${esc(c.titre)}</a>`:esc(c.titre)} <span class="mut">${esc(c.artiste)} ${esc(c.date)} · ${c.sens} · ${c.score}</span></div>${c.zoom?`<img src="${c.zoom}">`:""}<img src="${c.full}"><div class="b">${['oui','peut-etre','non'].map(v=>`<button data-k="${esc(k)}" data-v="${v}" class="${J[k]==v?'on':''}">${v.replace('-',' ')}</button>`).join('')}</div></div>`}).join('')}</div></div>`).join('');save()}
document.addEventListener('click',e=>{const b=e.target.closest('button[data-k]');if(!b)return;const k=b.dataset.k;J[k]=J[k]==b.dataset.v?undefined:b.dataset.v;if(!J[k])delete J[k];b.parentNode.querySelectorAll('button').forEach(x=>x.classList.toggle('on',J[k]==x.dataset.v));save()});
document.getElementById('f').onchange=draw;
document.getElementById('x').onclick=()=>{const rows=['requete,estampe,jugement',...Object.entries(J).map(([k,v])=>k.split('|').concat(v).join(','))];const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\\n')],{type:'text/csv'}));a.download='revue_inconnues.csv';a.click()};
draw();
</script></body></html>"""
Path(sys.argv[4]).write_text(page.replace("__DATA__", json.dumps(data)))
print(len(data), "requêtes,", Path(sys.argv[4]).stat().st_size // 1024, "Ko")
