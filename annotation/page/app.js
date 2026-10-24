'use strict';
/* Annotation Xanto : page autonome (aucun serveur, aucune ressource externe).
   Les réponses sont gardées dans le navigateur (localStorage) et exportées en JSON / CSV.
   Les coordonnées des rectangles sont exportées en pixels de l'image ORIGINALE. */

const KEY = 'xanto_annotation_v1';
const NS = 'http://www.w3.org/2000/svg';
const $ = (s, r) => (r || document).querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

/* ---------- stockage ---------- */
let store = {annotateurs: {}, courant: '', prefs: {cacherIA: true}, pos: {}};
try { const s = localStorage.getItem(KEY); if (s) { const o = JSON.parse(s); store = Object.assign(store, o); store.prefs = Object.assign({cacherIA: true}, o.prefs || {}); } } catch (e) {}
let sauve_ok = true;
function persist() {
  try { localStorage.setItem(KEY, JSON.stringify(store)); sauve_ok = true; }
  catch (e) { sauve_ok = false; }
  const h = new Date().toTimeString().slice(0, 5);
  $('#etat').textContent = sauve_ok ? 'Enregistré dans ce navigateur à ' + h + ' (pensez à exporter)' : 'Sauvegarde automatique impossible : exportez régulièrement';
}
function bucket() { const n = store.courant; return store.annotateurs[n] || (store.annotateurs[n] = {rep: {}}); }
function rec(k) { return bucket().rep[k]; }
function maj(k, patch) {
  const r = Object.assign({}, rec(k) || {}, patch, {annotateur: store.courant, date: new Date().toISOString()});
  bucket().rep[k] = r; persist(); return r;
}

/* ---------- visionneuse : zoom (molette), déplacement, miroir, rectangle ---------- */
class Viewer {
  constructor(el, opt) {
    this.el = el; this.opt = opt || {}; el.classList.add('viewer');
    this.stage = document.createElement('div'); this.stage.className = 'stage';
    this.flip = document.createElement('div'); this.flip.className = 'flip';
    this.img = new Image(); this.img.draggable = false;
    this.svg = document.createElementNS(NS, 'svg'); this.svg.setAttribute('class', 'ov');
    this.flip.append(this.img, this.svg); this.stage.append(this.flip); el.append(this.stage);
    this.s = 1; this.tx = 0; this.ty = 0; this.mir = false; this.box = null; this.hints = []; this.heat = null; this.pick = null; this.tool = 'draw'; this.drag = null; this.inf = null;
    const tb = document.createElement('div'); tb.className = 'tb';
    const mk = (t, title, f) => { const b = document.createElement('button'); b.textContent = t; b.title = title; b.onclick = f; b.onpointerdown = e => e.stopPropagation(); tb.append(b); return b; };
    mk('Miroir', 'Retourner l\'image (touche M). N\'affecte pas les coordonnées enregistrées.', () => this.setMirror(!this.mir));
    mk('+', 'Agrandir', () => this.zoomAt(1.4, this.el.clientWidth / 2, this.el.clientHeight / 2));
    mk('−', 'Réduire', () => this.zoomAt(1 / 1.4, this.el.clientWidth / 2, this.el.clientHeight / 2));
    mk('Ajuster', 'Image entière (ou double-clic)', () => this.fit());
    if (this.opt.editable) {
      this.bTool = mk('Tracer', 'Basculer entre tracer un rectangle et déplacer l\'image (astuce : Maj + glisser déplace toujours l\'image)', () => this.setTool(this.tool === 'draw' ? 'pan' : 'draw'));
      mk('Effacer', 'Effacer le rectangle', () => { this.box = null; this.draw(); this.emit(); });
    }
    el.append(tb);
    el.addEventListener('wheel', e => { e.preventDefault(); const r = el.getBoundingClientRect(); this.zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top); }, {passive: false});
    el.addEventListener('pointerdown', e => this.down(e));
    el.addEventListener('pointermove', e => this.move(e));
    el.addEventListener('pointerup', e => this.up(e));
    el.addEventListener('pointercancel', e => this.up(e));
    el.addEventListener('dblclick', () => this.fit());
    el.addEventListener('contextmenu', e => e.preventDefault());
    this.ro = new ResizeObserver(() => { if (this.inf && this.autofit) this.fit(); });
    this.ro.observe(el);
  }
  setTool(t) { this.tool = t; if (this.bTool) { this.bTool.textContent = t === 'draw' ? 'Tracer' : 'Déplacer'; this.bTool.classList.toggle('on', t === 'pan'); } this.el.style.cursor = t === 'draw' && this.opt.editable ? 'crosshair' : 'grab'; }
  setImage(inf, mirror) {
    this.inf = inf; this.mir = !!mirror; this.box = null; this.heat = null; this.hints = [];
    this.img.src = inf.src; this.img.width = inf.tw; this.img.height = inf.th;
    for (const e of [this.stage, this.flip]) { e.style.width = inf.tw + 'px'; e.style.height = inf.th + 'px'; }
    this.svg.setAttribute('width', inf.tw); this.svg.setAttribute('height', inf.th); this.svg.setAttribute('viewBox', `0 0 ${inf.tw} ${inf.th}`);
    this.setTool('draw'); this.fit();
  }
  setMirror(m) { this.mir = m; this.apply(); }
  fit() {
    const W = this.el.clientWidth, H = this.el.clientHeight, i = this.inf; if (!i || !W || !H) return;
    this.s = Math.min(W / i.tw, H / i.th) * 0.98; this.fs = this.s; this.tx = (W - i.tw * this.s) / 2; this.ty = (H - i.th * this.s) / 2; this.autofit = true; this.apply();
  }
  apply() { this.stage.style.transform = `translate(${this.tx}px,${this.ty}px) scale(${this.s})`; this.flip.style.transform = this.mir ? 'scaleX(-1)' : ''; this.draw(); }
  zoomAt(f, cx, cy) {
    const ns = Math.max(this.fs * 0.5, Math.min(14, this.s * f)); f = ns / this.s;
    this.tx = cx - (cx - this.tx) * f; this.ty = cy - (cy - this.ty) * f; this.s = ns; this.autofit = false; this.apply();
  }
  /* boîte en pixels de l'image originale <-> pixels de la vignette */
  setBox(b) { const i = this.inf; this.box = b ? [b[0] * i.tw / i.ow, b[1] * i.th / i.oh, b[2] * i.tw / i.ow, b[3] * i.th / i.oh] : null; this.draw(); }
  setHints(hs) { this.hints = hs.filter(Boolean).map(b => { const i = this.inf; return [b[0] * i.tw / i.ow, b[1] * i.th / i.oh, b[2] * i.tw / i.ow, b[3] * i.th / i.oh]; }); this.draw(); }
  getBox() {
    if (!this.box) return null; const i = this.inf, b = this.norm(this.box);
    return [Math.round(b[0] * i.ow / i.tw), Math.round(b[1] * i.oh / i.th), Math.round(b[2] * i.ow / i.tw), Math.round(b[3] * i.oh / i.th)];
  }
  norm(b) { return [Math.min(b[0], b[2]), Math.min(b[1], b[3]), Math.max(b[0], b[2]), Math.max(b[1], b[3])]; }
  emit() { if (this.opt.onbox) this.opt.onbox(this.getBox()); }
  rect(b, cls) { const r = document.createElementNS(NS, 'rect'); r.setAttribute('class', cls); const n = this.norm(b); r.setAttribute('x', n[0]); r.setAttribute('y', n[1]); r.setAttribute('width', n[2] - n[0]); r.setAttribute('height', n[3] - n[1]); this.svg.append(r); return r; }
  setHeat(url) { this.heat = url; this.draw(); }
  pickOnce(cb) { this.pick = cb; this.el.style.cursor = 'cell'; }
  draw() {
    this.svg.textContent = '';
    if (this.heat) { const h = document.createElementNS(NS, 'image'); h.setAttribute('href', this.heat); h.setAttribute('width', this.inf.tw); h.setAttribute('height', this.inf.th); h.setAttribute('preserveAspectRatio', 'none'); h.setAttribute('class', 'heat'); this.svg.append(h); }
    for (const h of this.hints) this.rect(h, 'ia');
    if (!this.box) return;
    const b = this.norm(this.box); this.rect(b, 'main');
    if (!this.opt.editable) return;
    const z = 11 / this.s, cx = [b[0], b[2]], cy = [b[1], b[3]];
    [['nw', 0, 0], ['ne', 1, 0], ['sw', 0, 1], ['se', 1, 1]].forEach(([n, a, c]) => {
      const r = document.createElementNS(NS, 'rect'); r.setAttribute('class', 'h'); r.dataset.h = n;
      r.setAttribute('x', cx[a] - z / 2); r.setAttribute('y', cy[c] - z / 2); r.setAttribute('width', z); r.setAttribute('height', z);
      r.style.pointerEvents = 'all'; r.style.cursor = (n === 'nw' || n === 'se') ? 'nwse-resize' : 'nesw-resize'; this.svg.append(r);
    });
  }
  loc(e) {
    const r = this.el.getBoundingClientRect(); let x = (e.clientX - r.left - this.tx) / this.s; const y = (e.clientY - r.top - this.ty) / this.s;
    if (this.mir) x = this.inf.tw - x; return [x, y];
  }
  clamp(x, y) { return [Math.max(0, Math.min(this.inf.tw, x)), Math.max(0, Math.min(this.inf.th, y))]; }
  down(e) {
    if (!this.inf) return;
    try { this.el.setPointerCapture(e.pointerId); } catch (_) {}
    if (this.pick && e.button === 0 && !e.shiftKey) {
      const [x, y] = this.clamp(...this.loc(e)), i = this.inf, cb = this.pick; this.pick = null; this.setTool(this.tool);
      cb([Math.round(x * i.ow / i.tw), Math.round(y * i.oh / i.th)]); return;
    }
    const pan = e.button === 1 || e.button === 2 || e.shiftKey || this.tool === 'pan' || !this.opt.editable;
    if (pan) { this.drag = {k: 'pan', sx: e.clientX, sy: e.clientY, tx: this.tx, ty: this.ty}; this.el.style.cursor = 'grabbing'; return; }
    const [x, y] = this.loc(e), h = e.target.dataset && e.target.dataset.h;
    if (h && this.box) { const b = this.norm(this.box); this.box = b; this.drag = {k: 'resize', h}; }
    else if (this.box && this.inside(x, y)) { this.drag = {k: 'move', ox: x, oy: y, b0: this.norm(this.box)}; }
    else { this.drag = {k: 'new', x, y, prev: this.box, moved: false}; }
  }
  inside(x, y) { const b = this.norm(this.box); return x >= b[0] && x <= b[2] && y >= b[1] && y <= b[3]; }
  move(e) {
    const d = this.drag; if (!d) return;
    if (d.k === 'pan') { this.tx = d.tx + e.clientX - d.sx; this.ty = d.ty + e.clientY - d.sy; this.autofit = false; this.apply(); return; }
    const [x, y] = this.clamp(...this.loc(e));
    if (d.k === 'new') { d.moved = true; this.box = [...this.clamp(d.x, d.y), x, y]; }
    else if (d.k === 'resize') { const b = this.box; if (d.h.includes('w')) b[0] = x; else b[2] = x; if (d.h.includes('n')) b[1] = y; else b[3] = y; }
    else if (d.k === 'move') {
      const b = d.b0, w = b[2] - b[0], h = b[3] - b[1];
      let nx = b[0] + x - d.ox, ny = b[1] + y - d.oy; nx = Math.max(0, Math.min(this.inf.tw - w, nx)); ny = Math.max(0, Math.min(this.inf.th - h, ny));
      this.box = [nx, ny, nx + w, ny + h];
    }
    this.draw();
  }
  up(e) {
    const d = this.drag; this.drag = null; if (!d) return;
    this.el.style.cursor = this.tool === 'draw' && this.opt.editable ? 'crosshair' : 'grab';
    if (d.k === 'pan') return;
    if (d.k === 'new') {
      const b = this.box && this.norm(this.box);
      if (!d.moved || !b || (b[2] - b[0]) * this.s < 6 || (b[3] - b[1]) * this.s < 6) { this.box = d.prev; this.draw(); return; }
    }
    if (this.box) this.box = this.norm(this.box);
    this.draw(); this.emit();
  }
  destroy() { this.ro.disconnect(); }
}

/* ---------- données et filtres ---------- */
const ONGLETS = {
  paires: {items: DATA.paires, lotLabel: 'Lot', lot: p => p.lot, aide: 'plat connu ↔ estampe citée'},
  sources: {items: DATA.sources, lotLabel: 'Groupe', lot: p => p.groupe},
  absences: {items: DATA.sources, lotLabel: 'Groupe', lot: p => p.groupe}
};
const ui = {tab: store.pos.tab || 'paires', cur: Object.assign({}, store.pos.cur || {}), cand: 0, filtre: {etat: '', lot: '', plat: ''}, iaVue: {}};
let viewers = [];

function estFait(tab, it) {
  if (tab === 'paires') return !!(rec('P|' + it.id) || {}).statut;
  if (tab === 'absences') return !!(rec('A|' + it.id) || {}).verdict;
  return it.cands.length > 0 && it.cands.every(c => (rec('S|' + it.id + '|' + c.id) || {}).jugement);
}
function liste() {
  const f = ui.filtre;
  return ONGLETS[ui.tab].items.filter(it => (!f.lot || ONGLETS[ui.tab].lot(it) === f.lot) && (!f.plat || String(it.plat) === f.plat.trim()) &&
    (!f.etat || (f.etat === 'fait') === estFait(ui.tab, it)));
}
function courant(l) {
  l = l || liste(); if (!l.length) return null;
  const i = l.findIndex(it => it.id === ui.cur[ui.tab]);
  return i >= 0 ? l[i] : l[0];
}

function peindreEntete() {
  const T = ONGLETS[ui.tab], tous = T.items, faits = tous.filter(it => estFait(ui.tab, it)).length, l = liste(), c = courant(l);
  $('#progression').textContent = `${faits} / ${tous.length} faits (${Math.round(100 * faits / tous.length)} %)` + (l.length !== tous.length ? ` · ${l.length} affichés` : '') + (c ? ` · n° ${l.indexOf(c) + 1}/${l.length}` : '');
  const sel = $('#f-aller'); sel.innerHTML = l.map(it => `<option value="${esc(it.id)}">${estFait(ui.tab, it) ? '✓' : '·'} ${esc(it.id)} (plat ${esc(it.plat)})</option>`).join('');
  if (c) sel.value = c.id;
  document.querySelectorAll('#onglets button').forEach(b => b.classList.toggle('on', b.dataset.t === ui.tab));
  const nom = store.courant || '(aucun)'; $('#b-nom').textContent = 'Annotateur : ' + nom;
}
function peindreFiltres() {
  const T = ONGLETS[ui.tab], lots = [...new Set(T.items.map(T.lot))].sort();
  $('#t-lot').textContent = T.lotLabel;
  $('#f-lot').innerHTML = '<option value="">tous</option>' + lots.map(l => `<option>${esc(l)}</option>`).join('');
  $('#f-lot').value = ui.filtre.lot; $('#f-etat').value = ui.filtre.etat; $('#f-plat').value = ui.filtre.plat;
}

function aller(id) { ui.cur[ui.tab] = id; ui.cand = 0; store.pos = {tab: ui.tab, cur: ui.cur}; persist(); vue(); }
function pas(d) {
  const l = liste(), c = courant(l); if (!c) return; const i = l.indexOf(c) + d;
  if (i >= 0 && i < l.length) aller(l[i].id);
}

/* ---------- vues ---------- */
function nettoyer() { viewers.forEach(v => v.destroy()); viewers = []; }
function vue() {
  nettoyer(); peindreEntete();
  const it = courant(), m = $('#vue');
  if (!it) { m.innerHTML = '<p>Aucun élément avec ces filtres.</p>'; return; }
  ui.cur[ui.tab] = it.id;
  ({paires: vuePaires, sources: vueSources, absences: vueAbsences})[ui.tab](it, m);
}
function liens(it) { return it.fiche ? `<a href="${esc(it.fiche)}" target="_blank" rel="noopener">fiche Rovigo (plat ${esc(it.plat)})</a>` : `plat ${esc(it.plat)}`; }
function boutons(vals, cur, attr) {
  return vals.map(([v, t, k]) => `<button data-${attr}="${v}" data-v="${v}" class="${cur === v ? 'on' : ''}" title="touche ${k}">${k ? k + ' · ' : ''}${t}</button>`).join('');
}
function relie(m, attr, f) { m.querySelectorAll(`button[data-${attr}]`).forEach(b => b.onclick = () => f(b.dataset[attr])); }

/* ---------- mode assistant (seulement si la page est servie par annotation/assistant.py) ---------- */
let AIDE = null;
async function api(nom, corps) {
  const r = await fetch('api/' + nom, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(corps)});
  const o = await r.json(); if (!r.ok) throw new Error(o.erreur || r.status); return o;
}
/* c = {vp, ve, plat, estampe(), boxPlat(), boxEst(), phrase, noter(type, detail)} */
function panneauAide(m, c) {
  if (!AIDE) return;
  const d = document.createElement('div'); d.className = 'aide';
  d.innerHTML = `<b>Assistant</b> <span class="mut">chaque usage est inscrit dans votre réponse</span>
   <button data-a="carte" title="Calcul local : où la figure tracée sur le plat apparaît probablement dans l'estampe">Où est la figure ?</button>
   <button data-a="clic-plat" title="Calcul local : cliquez ensuite sur la figure dans le plat">Encadrer d'un clic (plat)</button>
   <button data-a="clic-est" title="Calcul local : cliquez ensuite sur la figure dans l'estampe">Encadrer d'un clic (estampe)</button>
   <input type="text" id="q-claude" placeholder="Question à Claude (facultatif)">
   <button data-a="claude" title="Envoie les deux découpes et la phrase de la fiche à Claude (Anthropic)">Demander à Claude</button>
   <div id="aide-sortie" class="mut"></div>`;
  m.querySelector('.form').before(d);
  const out = d.querySelector('#aide-sortie'), dire = (t, err) => { out.innerHTML = t; out.classList.toggle('err', !!err); };
  const occupe = async (t, f) => { d.querySelectorAll('button').forEach(b => b.disabled = true); dire(t + '…'); try { await f(); } catch (e) { dire('Échec : ' + esc(e.message), true); } d.querySelectorAll('button').forEach(b => b.disabled = false); };
  const proposer = (v, props, quoi) => {
    if (!props.length) { dire('Aucun objet trouvé à cet endroit.'); return; }
    let i = 0; const mettre = () => { v.setBox(props[i].box); v.emit(); };
    mettre();
    dire(`Rectangle proposé sur ${quoi} (à corriger si besoin). ` + (props.length > 1 ? props.map((p, k) => `<button data-p="${k}">${k === 0 ? 'proposition' : 'autre'} ${k + 1}</button>`).join(' ') : ''));
    out.querySelectorAll('button[data-p]').forEach(b => b.onclick = () => { i = +b.dataset.p; mettre(); });
  };
  const clic = (v, inf, quoi) => { dire(`Cliquez sur la figure dans ${quoi}.`); v.pickOnce(pt => occupe('Découpe en cours', async () => {
    const o = await api('encadrer', {image: inf, point: pt}); c.noter('encadrer_' + (quoi === 'le plat' ? 'plat' : 'estampe'));
    proposer(v, o.propositions, quoi); })); };
  d.querySelector('[data-a=clic-plat]').onclick = () => clic(c.vp, c.plat, 'le plat');
  d.querySelector('[data-a=clic-est]').onclick = () => { if (c.estampe()) clic(c.ve, c.estampe(), "l'estampe"); };
  d.querySelector('[data-a=carte]').onclick = () => {
    const b = c.boxPlat(); if (!b) { dire("Tracez d'abord la figure sur le plat."); return; }
    occupe('Calcul de la carte (quelques secondes, plus au premier appel)', async () => {
      const o = await api('carte', {plat: c.plat, estampe: c.estampe(), box_plat: b}); c.noter('carte', o.sens);
      c.ve.setHeat(o.carte); c.ve.setHints([o.box]);
      dire(`Zones chaudes = parties de l'estampe qui ressemblent le plus à la figure (meilleur sens : ${esc(o.sens)}). Pointillé : ${esc(o.note)}. <button id="b-prendre">Utiliser ce rectangle</button> <button id="b-sans">Masquer la carte</button>`);
      $('#b-prendre').onclick = () => { c.ve.setBox(o.box); c.ve.emit(); };
      $('#b-sans').onclick = () => { c.ve.setHeat(null); c.ve.setHints([]); };
    });
  };
  d.querySelector('[data-a=claude]').onclick = () => occupe('Claude réfléchit (de 20 s à 1 min)', async () => {
    const question = $('#q-claude').value.trim();
    const o = await api('claude', {plat: c.plat, estampe: c.estampe(), box_plat: c.boxPlat(), box_estampe: c.boxEst(), phrase: c.phrase || '', question});
    c.noter('claude', question); dire('<div class="claude">' + esc(o.texte).replace(/\n/g, '<br>') + '</div>');
  });
}
function noterAide(k, base, type, detail) {
  const r = rec(k) || {}; maj(k, Object.assign({}, base(), {aides: (r.aides || []).concat([{type, detail: detail || '', date: new Date().toISOString()}])}));
}

/* --- onglet 1 --- */
function vuePaires(p, m) {
  const k = 'P|' + p.id, r0 = rec(k) || {};
  let ep = p.epreuves.find(e => e.id === r0.epreuve) || p.epreuves[0], boxes = Object.assign({}, r0.boites_epreuves || {});
  ui.iaVue[p.id] = ui.iaVue[p.id] || !store.prefs.cacherIA || !!r0.ia_vue;
  m.innerHTML = `
  <div class="entete"><span class="id">${esc(p.id)}</span><span>${esc(p.titre)} ${p.date ? '(' + esc(p.date) + ')' : ''}</span><span class="mut">lot ${esc(p.lot)} · Bartsch ${esc(p.bartsch)}</span><span>${liens(p)}</span>
  <label class="mut"><input type="checkbox" id="c-ia" ${store.prefs.cacherIA ? 'checked' : ''}> ne pas voir la proposition de l'IA</label></div>
  ${p.phrase ? `<div class="phrase">${esc(p.phrase)}</div>` : ''}
  <div class="duo">
   <section class="pane"><h3>Plat — rectangle autour de la figure <span class="mut" id="s-plat"></span></h3><div id="vp"></div></section>
   <section class="pane"><h3>Estampe Bartsch ${esc(p.bartsch)} <span id="l-ep"></span><span class="mut" id="s-est"></span></h3><div class="eps" id="eps"></div><div id="ve"></div></section>
  </div>
  <div class="form">
   <fieldset class="choix"><legend>Figure</legend>${boutons([['trouve', 'trouvée', 1], ['incertain', 'incertaine', 2], ['introuvable', 'introuvable', 3]], r0.statut, 'st')}</fieldset>
   <fieldset class="choix"><legend>Inversée</legend>${boutons([['oui', 'oui'], ['non', 'non']], r0.inverse, 'inv')}</fieldset>
   <fieldset><legend>Type</legend><select id="f-type"><option value="">—</option><option value="figure">figure</option><option value="groupe">groupe</option><option value="composition">composition</option></select></fieldset>
   <fieldset><legend>Parties reprises</legend><input type="text" id="f-parties" placeholder="ex. torse, bras droit, drapé"></fieldset>
   <fieldset><legend>Commentaire</legend><textarea id="f-com"></textarea></fieldset>
   <div class="sig" id="sig"></div>
  </div>`;
  const vp = new Viewer($('#vp'), {editable: true, onbox: b => sauver({box_plat: b})});
  const ve = new Viewer($('#ve'), {editable: true, onbox: b => { boxes[ep.id] = b; sauver({box_estampe: b}); }});
  viewers.push(vp, ve);
  vp.setImage(p.photo); vp.setBox(r0.box_plat || null);
  const majIA = () => { vp.setHints(store.prefs.cacherIA ? [] : [p.ia]); if (!store.prefs.cacherIA) ui.iaVue[p.id] = true; };
  majIA();
  $('#c-ia').onchange = e => { store.prefs.cacherIA = e.target.checked; persist(); majIA(); };
  function montrerEp() {
    $('#eps').innerHTML = p.epreuves.length ? p.epreuves.map((e, i) => `<button data-ep="${esc(e.id)}" class="${e === ep ? 'on' : ''}" title="${esc(e.musee)}">épreuve ${i + 1}/${p.epreuves.length} · ${esc(e.musee)}</button>`).join('') : '<span class="mut">aucune épreuve disponible</span>';
    $('#l-ep').innerHTML = ep && ep.lien ? `<a href="${esc(ep.lien)}" target="_blank" rel="noopener">notice du musée (${esc(ep.musee)})</a>` : '';
    relie($('#eps'), 'ep', id => choisirEp(p.epreuves.find(e => e.id === id)));
    if (ep) { ve.setImage(ep); ve.setBox(boxes[ep.id] || null); }
  }
  function choisirEp(e) { if (!e || e === ep) return; ep = e; montrerEp(); sauver({box_estampe: boxes[ep.id] || null}, true); }
  window.__epSuivante = d => { const i = p.epreuves.indexOf(ep) + d; if (i >= 0 && i < p.epreuves.length) choisirEp(p.epreuves[i]); };
  window.__mirroir = () => ve.setMirror(!ve.mir);
  montrerEp();
  const dims = () => { $('#s-plat').textContent = vp.inf ? `(${vp.inf.ow}×${vp.inf.oh} px)` : ''; $('#s-est').textContent = ep ? `(${ep.ow}×${ep.oh} px)` : ''; };
  dims();
  $('#f-type').value = r0.type || ''; $('#f-parties').value = r0.parties || ''; $('#f-com').value = r0.commentaire || '';
  function sauver(patch, silencieux) {
    const old = rec(k) || {};
    const r = maj(k, Object.assign({
      requete: p.id, plat: p.plat, bartsch: p.bartsch, image_plat: p.photo_nom, epreuve: ep ? ep.id : '', boites_epreuves: boxes,
      box_plat: vp.getBox(), box_estampe: ve.getBox(), taille_plat: [p.photo.ow, p.photo.oh], taille_estampe: ep ? [ep.ow, ep.oh] : null,
      ia_plat: p.ia, ia_trouve: p.ia_trouve, ia_vue: !!(old.ia_vue || ui.iaVue[p.id])
    }, patch));
    montrerSig(r); peindreEntete();
  }
  function montrerSig(r) { $('#sig').textContent = r && r.date ? `Enregistré par ${r.annotateur} le ${r.date.slice(0, 16).replace('T', ' ')}` : 'Pas encore de réponse'; }
  montrerSig(r0);
  panneauAide(m, {vp, ve, plat: p.photo, estampe: () => ep, boxPlat: () => vp.getBox(), boxEst: () => ve.getBox(), phrase: p.phrase,
    noter: (t, d) => { noterAide(k, () => ({}), t, d); sauver({}); }});
  relie(m, 'st', v => { const r = rec(k) || {}; sauver({statut: r.statut === v ? '' : v}); vue(); });
  relie(m, 'inv', v => { const r = rec(k) || {}; sauver({inverse: r.inverse === v ? '' : v}); vue(); });
  $('#f-type').onchange = e => sauver({type: e.target.value});
  $('#f-parties').oninput = e => sauver({parties: e.target.value});
  $('#f-com').oninput = e => sauver({commentaire: e.target.value});
}

/* --- onglet 2 --- */
function vueSources(q, m) {
  const c = q.cands[Math.min(ui.cand, q.cands.length - 1)];
  const kc = c ? 'S|' + q.id + '|' + c.id : '', r0 = rec(kc) || {};
  m.innerHTML = `
  <div class="entete"><span class="id">${esc(q.id)}</span><span>${esc(q.titre)}</span><span class="mut">${esc(q.groupe)} · ${esc(q.type)}</span><span>${liens(q)}</span></div>
  <div class="duo">
   <section class="pane"><h3>Plat — figure à rapprocher (rectangle rouge) <span class="mut">${q.type === 'composition' ? '(scène entière)' : ''}</span></h3><div id="vp"></div></section>
   <section class="pane"><h3>${c ? `Estampe proposée ${c.rang}/${q.cands.length} : ${c.lien ? `<a href="${esc(c.lien)}" target="_blank" rel="noopener">${esc(c.titre)}</a>` : esc(c.titre)}` : 'Aucune proposition'}
     <span class="mut">${c ? esc([c.artiste, c.date, c.musee].filter(Boolean).join(' · ')) : ''}</span></h3><div id="ve"></div></section>
  </div>
  <div class="strip" id="strip">${q.cands.map((x, i) => { const j = (rec('S|' + q.id + '|' + x.id) || {}).jugement || ''; return `<div class="card ${x === c ? 'sel' : ''}" data-i="${i}" title="${esc(x.titre)}"><img src="${esc(x.src)}" loading="lazy"><span>${x.rang}</span> <span class="v ${j}">${j ? j.replace('-', ' ') : '·'}</span></div>`; }).join('')}</div>
  <div class="form">
   <fieldset class="choix"><legend>Cette estampe</legend>${boutons([['oui', 'oui', 1], ['peut-etre', 'peut-être', 2], ['non', 'non', 3]], r0.jugement, 'j')}</fieldset>
   <fieldset><legend>Commentaire</legend><textarea id="f-com"></textarea></fieldset>
   <div class="sig" id="sig"></div>
   <div class="sig"><b>oui</b> = même figure, même pose, au moins un détail non nécessaire repris · <b>peut-être</b> = même pose générale sans détail probant · <b>non</b> = autre chose. Facultatif : tracez la figure correspondante sur l'estampe.
   ${c && c.sens === 'miroir' ? '<br>Cette estampe est présentée retournée (miroir) parce que le rapprochement a été trouvé ainsi ; le bouton Miroir permet de la remettre à l\'endroit.' : ''}</div>
  </div>`;
  const vp = new Viewer($('#vp'), {editable: false}); viewers.push(vp);
  vp.setImage(q.photo); vp.setBox(q.box);
  if (!c) return;
  const ve = new Viewer($('#ve'), {editable: true, onbox: b => sauver({box_estampe: b})}); viewers.push(ve);
  ve.setImage(c, c.sens === 'miroir'); ve.setBox(r0.box_estampe || null); ve.setHints([c.region]);
  window.__mirroir = () => ve.setMirror(!ve.mir);
  $('#f-com').value = r0.commentaire || '';
  const sig = r => { $('#sig').textContent = r && r.date ? `Enregistré par ${r.annotateur} le ${r.date.slice(0, 16).replace('T', ' ')}` : 'Pas encore de réponse'; }; sig(r0);
  function sauver(patch) {
    const r = maj(kc, Object.assign({requete: q.id, plat: q.plat, image_plat: q.photo_nom, estampe: c.id, rang: c.rang, box_plat: q.box,
      box_estampe: ve.getBox(), taille_plat: [q.photo.ow, q.photo.oh], taille_estampe: [c.ow, c.oh]}, patch));
    sig(r); peindreEntete(); return r;
  }
  window.__jugerCandidat = v => {
    const r = rec(kc) || {}; sauver({jugement: r.jugement === v ? '' : v});
    if (r.jugement !== v && ui.cand < q.cands.length - 1) ui.cand++;
    vue();
  };
  relie(m, 'j', v => window.__jugerCandidat(v));
  panneauAide(m, {vp, ve, plat: q.photo, estampe: () => c, boxPlat: () => q.box, boxEst: () => ve.getBox(), phrase: '',
    noter: (t, d) => { noterAide(kc, () => ({}), t, d); sauver({}); }});
  $('#f-com').oninput = e => sauver({commentaire: e.target.value});
  m.querySelectorAll('.card').forEach(el => el.onclick = () => { ui.cand = +el.dataset.i; vue(); });
  const s = $('.card.sel'); if (s) s.scrollIntoView({inline: 'center', block: 'nearest'});
  window.__candidat = d => { const i = ui.cand + d; if (i >= 0 && i < q.cands.length) { ui.cand = i; vue(); } };
}

/* --- onglet 3 --- */
function vueAbsences(q, m) {
  const k = 'A|' + q.id, r0 = rec(k) || {};
  m.innerHTML = `
  <div class="entete"><span class="id">${esc(q.id)}</span><span>${esc(q.titre)}</span><span class="mut">${esc(q.groupe)} · ${esc(q.type)}</span><span>${liens(q)}</span></div>
  <div class="duo">
   <section class="pane"><h3>Plat — figure concernée <span class="mut">(vous pouvez corriger le rectangle)</span></h3><div id="vp"></div></section>
   <section class="pane"><h3>Les ${q.cands.length} estampes proposées <span class="mut">(cliquer : les examiner dans l'onglet 2)</span></h3><div class="strip" id="strip" style="flex-wrap:wrap;overflow:auto">${q.cands.map((x, i) => { const j = (rec('S|' + q.id + '|' + x.id) || {}).jugement || ''; return `<div class="card" data-i="${i}" title="${esc(x.titre)}"><img src="${esc(x.src)}" loading="lazy"><span>${x.rang}</span> <span class="v ${j}">${j ? j.replace('-', ' ') : '·'}</span></div>`; }).join('')}</div></section>
  </div>
  <div class="form">
   <fieldset class="choix"><legend>Cette figure</legend>${boutons([['absence', 'n\'a vraisemblablement pas de source dans la galerie', 1], ['ailleurs', 'a une source hors galerie ou déjà repérée', 2], ['incertain', 'on ne peut pas dire', 3]], r0.verdict, 'v')}</fieldset>
   <fieldset><legend>Commentaire</legend><textarea id="f-com"></textarea></fieldset>
   <div class="sig" id="sig"></div>
  </div>`;
  const vp = new Viewer($('#vp'), {editable: true, onbox: b => sauver({box_plat: b})}); viewers.push(vp);
  vp.setImage(q.photo); vp.setBox(r0.box_plat || q.box);
  $('#f-com').value = r0.commentaire || '';
  const sig = r => { $('#sig').textContent = r && r.date ? `Enregistré par ${r.annotateur} le ${r.date.slice(0, 16).replace('T', ' ')}` : 'Pas encore de réponse'; }; sig(r0);
  function sauver(patch) {
    const r = maj(k, Object.assign({requete: q.id, plat: q.plat, image_plat: q.photo_nom, groupe: q.groupe, box_plat: vp.getBox(), box_figure_initiale: q.box, taille_plat: [q.photo.ow, q.photo.oh]}, patch));
    sig(r); peindreEntete();
  }
  window.__verdict = v => { const r = rec(k) || {}; sauver({verdict: r.verdict === v ? '' : v}); vue(); };
  relie(m, 'v', v => window.__verdict(v));
  window.__mirroir = () => vp.setMirror(!vp.mir);
  $('#f-com').oninput = e => sauver({commentaire: e.target.value});
  m.querySelectorAll('.card').forEach(el => el.onclick = () => { ui.tab = 'sources'; ui.cand = +el.dataset.i; ui.cur.sources = q.id; ui.filtre = {etat: '', lot: '', plat: ''}; peindreFiltres(); vue(); });
}

/* ---------- export / import ---------- */
function telecharger(nom, texte, type) {
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([texte], {type})); a.download = nom; document.body.append(a); a.click(); a.remove();
}
function horodatage() { return new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-'); }
function nomSur() { return (store.courant || 'anonyme').replace(/[^\w.-]+/g, '_'); }
function exporterJSON() {
  const o = {format: 'xanto-annotation', version: 1, annotateur: store.courant, exporte_le: new Date().toISOString(), reponses: bucket().rep};
  telecharger(`annotations_${nomSur()}_${horodatage()}.json`, JSON.stringify(o, null, 1), 'application/json');
}
const COLS = ['tache', 'cle', 'requete', 'plat', 'estampe', 'statut_ou_jugement', 'inverse', 'type', 'parties', 'x0_plat', 'y0_plat', 'x1_plat', 'y1_plat', 'x0_estampe', 'y0_estampe', 'x1_estampe', 'y1_estampe', 'commentaire', 'ia_vue', 'aides', 'annotateur', 'date'];
function exporterCSV() {
  const q = v => { v = v == null ? '' : String(v); return /[",\n;]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
  const rows = [COLS.join(',')];
  for (const [k, r] of Object.entries(bucket().rep)) {
    const t = k[0] === 'P' ? 'paires' : k[0] === 'S' ? 'sources' : 'absences', bp = r.box_plat || [], be = r.box_estampe || [];
    rows.push([t, k, r.requete, r.plat, r.estampe || r.epreuve || '', r.statut || r.jugement || r.verdict || '', r.inverse, r.type, r.parties, bp[0], bp[1], bp[2], bp[3], be[0], be[1], be[2], be[3], r.commentaire, r.ia_vue, (r.aides || []).map(a => a.type).join(' '), r.annotateur, r.date].map(q).join(','));
  }
  telecharger(`annotations_${nomSur()}_${horodatage()}.csv`, '﻿' + rows.join('\n'), 'text/csv');
}
function importer(fichier) {
  const fr = new FileReader();
  fr.onload = () => {
    let o; try { o = JSON.parse(fr.result); } catch (e) { alert('Fichier illisible : ce n\'est pas un export JSON.'); return; }
    if (!o || o.format !== 'xanto-annotation' || !o.reponses) { alert('Ce fichier n\'est pas un export de cette page.'); return; }
    const nom = o.annotateur || 'anonyme', b = store.annotateurs[nom] || (store.annotateurs[nom] = {rep: {}});
    let nouv = 0, maj_ = 0, gard = 0;
    for (const [k, r] of Object.entries(o.reponses)) {
      const a = b.rep[k];
      if (!a) { b.rep[k] = r; nouv++; } else if ((r.date || '') > (a.date || '')) { b.rep[k] = r; maj_++; } else gard++;
    }
    persist(); peindreEntete(); vue();
    alert(`Import de « ${nom} » : ${nouv} nouvelles réponses, ${maj_} mises à jour, ${gard} déjà plus récentes ici.` +
      (nom !== store.courant ? `\nElles sont rangées sous le nom « ${nom} » ; vous annotez toujours sous « ${store.courant} » (bouton Annotateur pour changer).` : ''));
  };
  fr.readAsText(fichier);
}

/* ---------- nom de l'annotateur, aide ---------- */
function demanderNom() {
  const d = $('#d-nom'); $('#i-nom').value = store.courant || '';
  $('#l-noms').innerHTML = Object.keys(store.annotateurs).map(n => `<option value="${esc(n)}">`).join('');
  const fin = () => { const n = $('#i-nom').value.trim(); if (!n) return false; store.courant = n; bucket(); persist(); peindreEntete(); vue(); return true; };
  $('#ok-nom').onclick = e => { if (!fin()) e.preventDefault(); };
  d.oncancel = e => { if (!store.courant) e.preventDefault(); };
  if (d.showModal) d.showModal(); else { const n = prompt('Votre nom :'); if (n) { $('#i-nom').value = n; fin(); } }
}
$('#aide-texte').innerHTML = `
<p>Trois tâches, en onglets. Tout est enregistré automatiquement dans ce navigateur ; <b>exportez régulièrement</b> (JSON) et envoyez le fichier.</p>
<ul>
<li><b>Tracer un rectangle</b> : glisser sur l'image. Les coins permettent de l'ajuster, l'intérieur de le déplacer. <kbd>Maj</kbd> + glisser (ou clic droit) déplace l'image ; la molette zoome ; double-clic = image entière.</li>
<li><kbd>←</kbd> <kbd>→</kbd> : élément précédent / suivant. <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> : réponse (onglet 1 : trouvée / incertaine / introuvable ; onglet 2 : oui / peut-être / non ; onglet 3 : absence / ailleurs / incertain).</li>
<li><kbd>↑</kbd> <kbd>↓</kbd> : épreuve suivante (onglet 1) ou estampe proposée suivante (onglet 2). <kbd>M</kbd> : miroir.</li>
<li>Onglet 1 : la case « ne pas voir la proposition de l'IA » est cochée par défaut, pour une annotation indépendante ; la décocher affiche la boîte de l'IA en pointillé orange (et le signale dans la réponse).</li>
<li>Mode assistant (page ouverte par <code>annotation/assistant.py</code>) : carte « où est la figure », encadrement d'un clic, question à Claude. Chaque usage est inscrit dans la réponse (champ <code>aides</code>).</li>
<li>Importer un export précédent permet de reprendre le travail ou de rassembler deux annotateurs (chaque annotateur reste distinct).</li>
</ul>`;
$('#ok-aide').onclick = () => $('#d-aide').close();

/* ---------- branchements ---------- */
document.querySelectorAll('#onglets button').forEach(b => b.onclick = () => { ui.tab = b.dataset.t; ui.filtre = {etat: '', lot: '', plat: ''}; ui.cand = 0; store.pos = {tab: ui.tab, cur: ui.cur}; persist(); peindreFiltres(); vue(); });
$('#f-etat').onchange = e => { ui.filtre.etat = e.target.value; vue(); };
$('#f-lot').onchange = e => { ui.filtre.lot = e.target.value; vue(); };
$('#f-plat').oninput = e => { ui.filtre.plat = e.target.value; vue(); };
$('#f-aller').onchange = e => aller(e.target.value);
$('#b-nom').onclick = demanderNom;
$('#b-json').onclick = exporterJSON;
$('#b-csv').onclick = exporterCSV;
$('#b-imp').onclick = () => $('#f-imp').click();
$('#f-imp').onchange = e => { if (e.target.files[0]) importer(e.target.files[0]); e.target.value = ''; };
$('#b-aide').onclick = () => $('#d-aide').showModal();
document.addEventListener('keydown', e => {
  const t = e.target.tagName; if (/INPUT|TEXTAREA|SELECT/.test(t) || e.ctrlKey || e.metaKey || e.altKey || $('#d-nom').open || $('#d-aide').open) return;
  const T = ui.tab;
  if (e.key === 'ArrowRight') pas(1);
  else if (e.key === 'ArrowLeft') pas(-1);
  else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    const d = e.key === 'ArrowDown' ? 1 : -1; e.preventDefault();
    if (T === 'paires' && window.__epSuivante) window.__epSuivante(d); else if (T === 'sources' && window.__candidat) window.__candidat(d);
  }
  else if (e.key === 'm' || e.key === 'M') { if (window.__mirroir) window.__mirroir(); }
  else if (/^[123]$/.test(e.key)) {
    const i = +e.key - 1;
    if (T === 'paires') { const b = document.querySelectorAll('button[data-st]')[i]; if (b) b.click(); }
    else if (T === 'sources' && window.__jugerCandidat) window.__jugerCandidat(['oui', 'peut-etre', 'non'][i]);
    else if (T === 'absences' && window.__verdict) window.__verdict(['absence', 'ailleurs', 'incertain'][i]);
  } else return;
  e.preventDefault();
});
$('#bas').textContent = 'Raccourcis : ← → naviguer · 1 2 3 répondre · ↑ ↓ épreuve / estampe · M miroir · molette zoom · Maj+glisser déplacer · ? aide';
peindreFiltres(); peindreEntete(); vue(); persist();
if (location.protocol.startsWith('http')) fetch('api/etat').then(r => r.ok ? r.json() : null).then(o => { if (o) { AIDE = o; vue(); } }).catch(() => {});
if (!store.courant) demanderNom();
