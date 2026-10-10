(() => {
  "use strict";
  const D = window.XANTO || {};
  const $ = (s) => document.querySelector(s);
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pieces = D.pieces || [], emprunts = D.emprunts || [];
  const byId = Object.fromEntries(pieces.map((p) => [p.id, p]));
  const annee = (p) => { const m = String(p.data || "").match(/1[45]\d\d/); return m ? +m[0] : null; };
  const nomEstampe = (v, n) => {
    const t = (D.titres || []).find((x) => x.tib_vol === v && x.tib_n === n);
    if (t) return `${t.titre} (${t.graveur})`;
    const e = (D.estampes || []).find((x) => x.tib_vol === v && x.tib_n === n);
    return e ? `${e.title} (${e.engraver || ""})` : `TIB ${v}, n° ${n}`;
  };

  // Navigation
  document.querySelectorAll("#nav button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll("#nav button").forEach((x) => x.classList.toggle("actif", x === b));
    document.querySelectorAll(".vue").forEach((v) => v.classList.toggle("actif", v.id === b.dataset.vue));
    if (b.dataset.vue === "echelle") dessinerEchelle();
  }));
  const modale = (html) => { $("#contenu-modale").innerHTML = html; $("#modale").hidden = false; };
  $("#fermer").onclick = () => ($("#modale").hidden = true);
  $("#modale").onclick = (e) => { if (e.target.id === "modale") $("#modale").hidden = true; };

  // Accueil
  const datees = pieces.filter(annee).length;
  const nEstampes = new Set(emprunts.map((e) => e.bartsch_vol + "/" + e.bartsch_n)).size;
  $("#chiffres").innerHTML = [
    [pieces.length, "pièces au catalogue de Rovigo"], [emprunts.length, "références à des estampes"],
    [nEstampes, "estampes distinctes citées"], [datees, "pièces avec une année"],
    [(D.litterature?.questions || []).length, "questions débattues"],
  ].map(([n, t]) => `<div class="chiffre"><b>${n}</b><span>${t}</span></div>`).join("");

  // Débats
  const L = D.litterature || { questions: [], auteurs: [] };
  const auteur = (id) => (L.auteurs || []).find((a) => a.id === id) || { nom: id };
  const badgeDes = (d) => d === "publié" ? '<span class="badge publie">désaccord publié</span>' : d === "implicite" ? '<span class="badge implicite">désaccord implicite</span>' : d ? `<span class="badge">${esc(d)}</span>` : "";
  const badgeStat = (s) => `<span class="badge ${s === "lu" || s === "lu en partie" ? "lu" : s === "indirect" ? "indirect" : "inference"}">${esc(s)}</span>`;
  $("#questions").innerHTML = (L.questions || []).map((q, i) => `
    <div class="carte" data-q="${i}">${badgeDes(q.desaccord)}<h4>${esc(q.titre)}</h4><p>${esc(q.explication)}</p></div>`).join("") || "<p>Carte de la littérature non chargée.</p>";
  document.querySelectorAll(".carte").forEach((c) => c.addEventListener("click", () => {
    const q = L.questions[+c.dataset.q];
    modale(`<h2>${esc(q.titre)}</h2><p>${esc(q.explication)}</p>${badgeDes(q.desaccord)}
      ${(q.positions || []).map((p) => { const a = auteur(p.auteur_id); return `<div class="position"><span class="auteur">${esc(a.nom)} ${esc(a.annee || "")}</span> ${badgeStat(p.statut)}<div>${esc(p.these)}</div>${p.citation ? `<q>${esc(p.citation)}</q>` : ""}</div>`; }).join("")}
      <h3>Ce que le calcul peut dire</h3><p>${esc(q.ce_que_le_calcul_peut_dire || "")}</p>
      <h3>Ce qu'il ne peut pas dire</h3><p>${esc(q.ce_qu_il_ne_peut_pas_dire || "")}</p>`);
  }));
  $("#auteurs").innerHTML = (L.auteurs || []).length ? `<h3>Textes mobilisés</h3><table><tr><th>Auteur</th><th>Référence</th><th>Lecture</th></tr>${L.auteurs.map((a) => `<tr><td>${esc(a.nom)} ${esc(a.annee || "")}</td><td>${a.lien ? `<a href="${esc(a.lien)}" target="_blank" rel="noopener">${esc(a.reference)}</a>` : esc(a.reference)}</td><td>${badgeStat(a.statut_lecture)}</td></tr>`).join("")}</table>` : "";

  // Corpus : frise
  const parAn = {};
  pieces.forEach((p) => { const a = annee(p); if (a && a >= 1520 && a <= 1545) parAn[a] = (parAn[a] || 0) + 1; });
  const ans = Object.keys(parAn).map(Number).sort((a, b) => a - b);
  const svgBarres = (labels, vals, w = 560, h = 220, onClick) => {
    const max = Math.max(...vals, 1), bw = (w - 40) / labels.length;
    return `<svg viewBox="0 0 ${w} ${h + 44}" width="100%"><g transform="translate(0,14)">${labels.map((l, i) => {
      const bh = (vals[i] / max) * h; return `<rect class="barre" x="${30 + i * bw + 2}" y="${h - bh + 4}" width="${bw - 4}" height="${bh}"><title>${l} : ${vals[i]}</title></rect>
      <text class="axe" x="${30 + i * bw + bw / 2}" y="${h + 20}" text-anchor="middle">${String(l).slice(-2)}</text><text class="axe" x="${30 + i * bw + bw / 2}" y="${h - bh}" text-anchor="middle">${vals[i]}</text>`;
    }).join("")}</g></svg>`;
  };
  $("#frise").innerHTML = svgBarres(ans, ans.map((a) => parAn[a]));

  // Corpus : classement des estampes
  const compte = {};
  emprunts.forEach((e) => { const k = e.bartsch_vol + "/" + e.bartsch_n; (compte[k] = compte[k] || new Set()).add(e.id); });
  const top = Object.entries(compte).map(([k, s]) => [k, s.size]).sort((a, b) => b[1] - a[1]).slice(0, 20);
  const maxTop = top[0]?.[1] || 1;
  $("#classement").innerHTML = top.map(([k, n]) => { const [v, num] = k.split("/"); return `<div class="classement-ligne" data-k="${k}"><span style="width:240px">${esc(nomEstampe(v, num))}</span><div class="bar" style="width:${(n / maxTop) * 180}px"></div><b>${n}</b></div>`; }).join("");
  document.querySelectorAll(".classement-ligne").forEach((l) => l.addEventListener("click", () => {
    const [v, n] = l.dataset.k.split("/");
    const ps = [...compte[l.dataset.k]].map((id) => byId[id]).filter(Boolean).sort((a, b) => (annee(a) || 9999) - (annee(b) || 9999));
    $("#detail-estampe").innerHTML = `<h3>${esc(nomEstampe(v, n))} — ${ps.length} pièces</h3><div class="tablewrap"><table><tr><th></th><th>Année</th><th>Titre</th><th>Lieu</th><th>Diamètre</th></tr>${ps.map((p) => ligne(p)).join("")}</table></div>`;
  }));

  // Corpus : frise des estampes (Gantt)
  if (D.reemploi) {
    const rows = D.reemploi.filter((e) => e.n_pieces >= 4).slice(0, 22), A0 = 1522, A1 = 1543, W = 900, LW = 250, RH = 22;
    const X = (a) => LW + ((a - A0) / (A1 - A0)) * (W - LW - 20);
    let svg = `<svg viewBox="0 0 ${W} ${rows.length * RH + 40}" width="100%" style="max-width:1000px">`;
    for (let a = A0; a <= A1; a += 2) svg += `<line x1="${X(a)}" x2="${X(a)}" y1="0" y2="${rows.length * RH + 8}" stroke="var(--ligne)"/><text class="axe" x="${X(a)}" y="${rows.length * RH + 24}" text-anchor="middle">${a}</text>`;
    rows.forEach((e, i) => {
      const y = i * RH + 14, [v, n] = e.estampe.replace("B", "").split(".");
      svg += `<text class="axe" x="0" y="${y + 4}" style="font-size:12px;fill:var(--encre)">${esc(nomEstampe(v, n).slice(0, 44))}</text>`;
      const ys = e.pieces.filter((p) => p.annee).map((p) => p.annee);
      if (ys.length) svg += `<line x1="${X(Math.min(...ys))}" x2="${X(Math.max(...ys))}" y1="${y}" y2="${y}" stroke="var(--bleu)" stroke-opacity=".35" stroke-width="6" stroke-linecap="round"/>`;
      const seen = {};
      e.pieces.filter((p) => p.annee).forEach((p) => {
        const k = p.annee; seen[k] = (seen[k] || 0) + 1; const dx = ((seen[k] - 1) % 3) * 4 - 4;
        const piece = byId[String(p.id)] || {};
        svg += `<a href="${esc(p.link)}" target="_blank"><circle cx="${X(p.annee) + dx}" cy="${y}" r="3.6" fill="${p.source_date === "inscription" ? "var(--ocre)" : "var(--blanc)"}" stroke="var(--ocre)" stroke-width="1.4"><title>${esc(piece.titolo || p.id)} (${p.annee}${p.source_date === "inscription" ? ", date inscrite" : ", date du catalogue"})</title></circle></a>`;
      });
    });
    $("#gantt").innerHTML = svg + "</svg>";
  }

  // Corpus : table
  const vign = D.vignettes || {};
  const ligne = (p) => `<tr><td>${vign[p.id] ? `<img loading="lazy" src="assets/${esc(vign[p.id])}" alt="">` : ""}</td><td>${esc(annee(p) || p.data)}</td><td><a href="${esc(p.link)}" target="_blank" rel="noopener">${esc(p.titolo)}</a></td><td>${esc(p.luogo)}</td><td>${p.diametro_cm ? esc(p.diametro_cm) + " cm" : ""}</td></tr>`;
  const refsPar = {};
  emprunts.forEach((e) => (refsPar[e.id] = (refsPar[e.id] || []).concat(`B ${e.bartsch_vol}/${e.bartsch_n}`)));
  const rendreTable = (f) => {
    const t = f.toLowerCase();
    const ps = pieces.filter((p) => !t || [p.titolo, p.luogo, p.data, p.iscrizione, (refsPar[p.id] || []).join(" ")].join(" ").toLowerCase().includes(t));
    $("#table-pieces").innerHTML = `<p class="aide">${ps.length} pièces</p><div class="tablewrap"><table><tr><th></th><th>Année</th><th>Titre</th><th>Lieu</th><th>Diamètre</th></tr>${ps.map(ligne).join("")}</table></div>`;
  };
  $("#filtre").addEventListener("input", (e) => rendreTable(e.target.value));
  rendreTable("");

  // Échelle
  let echelleFaite = false;
  function dessinerEchelle() {
    if (echelleFaite) return; echelleFaite = true;
    const E = D.echelle;
    if (!E) { $("#cas-echelle").innerHTML = "<p>Aucun cas chargé.</p>"; return; }
    const PXCM = 26; // pixels d'écran par centimètre réel
    $("#cas-echelle").innerHTML = E.cas.map((c, ci) => `<div class="cas"><h3>${esc(c.titre || c.id)}</h3>${c.resume ? `<p>${esc(c.resume)}</p>` : ""}
      <div class="temoins">${c.temoins.map((t, ti) => `<div class="temoin ${t.comparable ? "" : "non-comparable"}"><canvas id="cv-${ci}-${ti}"></canvas><div class="h">${t.hauteur_cm ?? "–"} cm</div>${t.hauteur_cm_independant ? `<div class="leg">second annotateur : ${t.hauteur_cm_independant} cm</div>` : ""}<div class="leg">${esc(t.objet)}${t.reference_cm ? `<br>${t.type === "plat" ? "diamètre" : "largeur de feuille"} ${t.reference_cm} cm` : ""}${t.prediction_proportionnelle_cm ? `<br>si adapté au plat : ${t.prediction_proportionnelle_cm} cm` : ""}${t.comparable ? "" : "<br><i>non comparable (figure redessinée)</i>"}</div></div>`).join("")}</div>
      <div id="graph-${ci}"></div></div>`).join("");
    E.cas.forEach((c, ci) => {
      c.temoins.forEach((t, ti) => {
        const cv = document.getElementById(`cv-${ci}-${ti}`), [x0, y0, x1, y1] = t.crop;
        const k = t.cm_par_px * PXCM; // pixels d'écran par pixel d'image
        cv.width = Math.round((x1 - x0) * k) + 30; cv.height = Math.round((y1 - y0) * k);
        const ctx = cv.getContext("2d"), img = new Image();
        img.onload = () => {
          ctx.drawImage(img, x0, y0, x1 - x0, y1 - y0, 30, 0, cv.width - 30, cv.height);
          ctx.fillStyle = "#fff8"; ctx.fillRect(0, 0, 28, cv.height); ctx.fillStyle = "#333"; ctx.font = "10px sans-serif";
          for (let cm = 0; cm * PXCM <= cv.height; cm++) { const y = cm * PXCM; ctx.fillRect(18, y, 10, 1); if (cm % 2 === 0) ctx.fillText(cm, 2, y + 9); }
          const P = (n) => t.reperes[n] && [30 + (t.reperes[n][0] - x0) * k, (t.reperes[n][1] - y0) * k];
          const a = P("tete"), b = P("pied_tendu");
          ctx.strokeStyle = "#e0402a"; ctx.lineWidth = 2;
          if (a && b) { ctx.beginPath(); ctx.moveTo(...a); ctx.lineTo(...b); ctx.stroke(); }
          ctx.fillStyle = "#e0402a"; [a, b, P("genou_tendu")].forEach((p) => p && (ctx.beginPath(), ctx.arc(p[0], p[1], 4, 0, 7), ctx.fill()));
        };
        img.onerror = () => { ctx.fillStyle = "#999"; ctx.fillText("image non disponible (voir build_data.py)", 34, 20); };
        img.src = "assets/" + t.image.split("/").pop();
      });
      const vals = c.temoins.filter((t) => t.hauteur_cm), max = Math.max(...vals.map((t) => Math.max(t.hauteur_cm, t.prediction_proportionnelle_cm || 0)));
      document.getElementById(`graph-${ci}`).innerHTML = `<h3>Hauteur mesurée (barre) et hauteur attendue si la figure était adaptée au plat (trait)</h3><svg viewBox="0 0 640 ${vals.length * 34 + 10}" width="100%">${vals.map((t, i) => {
        const w = (v) => (v / max) * 380; return `<text class="axe" x="0" y="${i * 34 + 20}">${esc(t.objet.slice(0, 38))}</text><rect class="barre" x="250" y="${i * 34 + 8}" width="${w(t.hauteur_cm)}" height="16" opacity="${t.comparable ? 1 : .4}"></rect><text class="axe" x="${255 + w(t.hauteur_cm)}" y="${i * 34 + 20}">${t.hauteur_cm} cm</text>${t.prediction_proportionnelle_cm ? `<line x1="${250 + w(t.prediction_proportionnelle_cm)}" x2="${250 + w(t.prediction_proportionnelle_cm)}" y1="${i * 34 + 4}" y2="${i * 34 + 28}" stroke="var(--bleu)" stroke-width="3"></line>` : ""}`;
      }).join("")}</svg>${c.conclusion ? `<p><b>Lecture :</b> ${esc(c.conclusion)}</p>` : ""}${c.limites ? `<p class="aide"><b>Limites :</b> ${esc(c.limites)}</p>` : ""}`;
    });
  }

  // Autres tests
  const A = D.analyses;
  const rendreValeur = (v) => {
    if (v && Array.isArray(v.labels) && Array.isArray(v.valeurs)) return svgBarres(v.labels, v.valeurs, 560, 160);
    if (v && Array.isArray(v.colonnes) && Array.isArray(v.lignes)) return `<div class="tablewrap"><table><tr>${v.colonnes.map((c) => `<th>${esc(c)}</th>`).join("")}</tr>${v.lignes.map((l) => `<tr>${l.map((x) => `<td>${esc(x)}</td>`).join("")}</tr>`).join("")}</table></div>`;
    return "";
  };
  $("#resultats").innerHTML = A && Array.isArray(A.tests) ? A.tests.map((t) => `<div class="res"><h3>${esc(t.titre)}</h3>${t.verdict ? `<span class="verdict">${esc(t.verdict)}</span>` : ""}<p><b>Thèse visée :</b> ${esc(t.these || "")}</p><p>${esc(t.resultat || "")}</p>${(t.graphiques || []).map((g) => `<h4>${esc(g.titre || "")}</h4>${rendreValeur(g)}`).join("")}${t.limites ? `<p class="aide"><b>Limites :</b> ${esc(t.limites)}</p>` : ""}</div>`).join("") : "<p>Résultats des tests non chargés.</p>";
})();
