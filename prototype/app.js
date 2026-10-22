(() => {
  'use strict';
  const data = window.XANTO_DATA || {};
  const corpus = Array.isArray(data.corpus) ? data.corpus : [];
  const original = Array.isArray(data.observations) ? data.observations : [];
  const comparisons = Array.isArray(data.comparisons) ? data.comparisons : [];
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const labels = {evidence:{image:'Image',catalogue:'Notice',interpretation:'Interprétation'}, certainty:{clear:'Claire',probable:'Probable',indeterminate:'Indéterminée'}, type:{POSE:'Configuration corporelle',ATTRIBUTE:'Attribut',RELATION:'Rapport visible',ACTION:'Action interprétée',INSCRIPTION:'Inscription'}, status:{observed_difference:'Différence observée',catalogue_attribution:'Attribution de catalogue',hypothesis:'Hypothèse',indeterminate:'Indéterminé'}};
  const storeKey = 'xanto.annotations.v1';
  let overrides = {}, added = [], changes = [], previousDraft = null, selected = null, evidence = 'all', certainty = 'all';
  const datasetId=data.meta?.dataset_id||'xanto-a-v0.1',datasetHash=data.meta?.dataset_hash||null;
  const sides = {left:{id:corpus[0]?.id || '',zoom:1,mirrored:false},right:{id:corpus[1]?.id || corpus[0]?.id || '',zoom:1,mirrored:false}};
  const object = id => corpus.find(item => item.id === id);
  const observations = () => [...original.map(item => ({...item,...overrides[item.id]})),...added];
  const sourceHref = value => { try { const url = new URL(value); return ['https:','http:'].includes(url.protocol) ? url.href : ''; } catch { return ''; } };
  const link = (url,text) => sourceHref(url) ? `<a href="${esc(sourceHref(url))}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>` : '';
  const status = (text,isError=false) => { $('storageStatus').textContent=text; $('storageStatus').classList.toggle('error',isError); renderDraftNotice(); };
  function renderDraftNotice(){
    $('draftNotice').hidden=!previousDraft;if(!previousDraft)return;
    $('draftNoticeText').textContent=previousDraft.recovery_status==='unparsed_or_incompatible_local_storage'?'Un ancien brouillon illisible reste conservé dans son intégralité. Il n’est pas appliqué au carnet. Vous pouvez exporter son contenu brut.':'Un brouillon lié à un autre état du dossier est conservé séparément. Il n’est pas appliqué aux observations actuelles. La réapplication automatique n’est pas disponible dans cette version ; exportez-le pour examiner vos notes antérieures.';
  }
  function save() {
    try { localStorage.setItem(storeKey,JSON.stringify({version:1,dataset_id:datasetId,dataset_hash:datasetHash,source_snapshot:{meta:data.meta||{},corpus,observations:original,comparisons},overrides,added,changes,previous_draft:previousDraft,updated_at:new Date().toISOString()})); status(previousDraft?'Annotations enregistrées. Le brouillon d’un autre état du dossier est conservé séparément dans l’export.':'Annotations enregistrées dans ce navigateur.'); }
    catch { status('L’enregistrement dans ce navigateur est indisponible. Exportez les annotations pour conserver vos modifications.',true); }
  }
  function load() {
    let raw=null;
    try {
      raw=localStorage.getItem(storeKey); if(!raw)return;
      const saved=JSON.parse(raw); if(saved.version!==1 || !saved.overrides || !Array.isArray(saved.added))throw new Error('format');
      if(saved.dataset_id!==datasetId || saved.dataset_hash!==datasetHash){previousDraft=saved;status('Le dossier source a changé. L’ancien brouillon reste séparé et sera inclus dans l’export ; aucune annotation ancienne n’est appliquée.',true);return;}
      previousDraft=saved.previous_draft||null;
      changes=Array.isArray(saved.changes)?saved.changes:[];
      for(const [id,change] of Object.entries(saved.overrides)) {
        if(!original.some(item=>item.id===id) || !change || typeof change!=='object')continue;
        overrides[id]={};
        if(typeof change.note==='string')overrides[id].note=change.note;
        if(Object.hasOwn(labels.certainty,change.certainty))overrides[id].certainty=change.certainty;
      }
      const ids=new Set(original.map(item=>item.id));
      added=saved.added.filter(item=>item && typeof item.id==='string' && !ids.has(item.id) && typeof item.statement==='string' && object(item.object_id) && Object.hasOwn(labels.evidence,item.evidence_kind) && Object.hasOwn(labels.certainty,item.certainty) && Object.hasOwn(labels.type,item.type) && (ids.add(item.id),true));
      status('Vos annotations locales ont été restaurées.');
    } catch {
      if(raw!==null)previousDraft={recovery_status:'unparsed_or_incompatible_local_storage',storage_key:storeKey,raw,recovered_at:new Date().toISOString()};
      status(raw!==null?'Les annotations locales n’ont pas pu être restaurées. Leur contenu brut est conservé séparément dans l’export, même après une nouvelle modification.':'Le stockage local n’est pas accessible. Les nouvelles modifications pourront être exportées.',true);
    }
  }
  const visible = () => observations().filter(item => (evidence==='all'||item.evidence_kind===evidence) && (certainty==='all'||item.certainty===certainty) && (!$('pairOnly').checked || Object.values(sides).some(side=>side.id===item.object_id)));
  function validBox(box) { return Array.isArray(box)&&box.length===4&&box.every(Number.isFinite)&&box[0]>=0&&box[1]>=0&&box[2]>0&&box[3]>0&&box[0]+box[2]<=1.000001&&box[1]+box[3]<=1.000001; }
  function renderMarkers() {
    const items=observations();const ids=new Set(visible().map(item=>item.id));
    for(const [side,state] of Object.entries(sides)) {
      const container=$(side+'Markers');container.hidden=!$('showMarkers').checked;
      container.innerHTML=items.map((item,index)=>item.object_id===state.id && validBox(item.bbox) && ids.has(item.id) ? `<button type="button" class="marker ${selected===item.id?'selected':''}" data-observation="${esc(item.id)}" style="left:${item.bbox[0]*100}%;top:${item.bbox[1]*100}%;width:${item.bbox[2]*100}%;height:${item.bbox[3]*100}%" aria-label="Observation ${index+1} : ${esc(item.statement)}" title="${esc(item.statement)}"><span>${String(index+1).padStart(2,'0')}</span></button>`:'').join('');
    }
  }
  function layout(side) {
    const state=sides[side], viewport=$(side+'Viewport'), image=$(side+'Image'), stage=$(side+'Stage'), wrap=stage.parentElement;
    const item=object(state.id);const width=image.naturalWidth||Number(item?.image_width)||1, height=image.naturalHeight||Number(item?.image_height)||1;
    const vw=viewport.clientWidth,vh=viewport.clientHeight; if(!vw||!vh)return;
    const fit=Math.min((vw-20)/width,(vh-20)/height);const w=Math.max(1,width*fit*state.zoom),h=Math.max(1,height*fit*state.zoom);
    stage.style.width=w+'px';stage.style.height=h+'px';stage.classList.toggle('mirrored',state.mirrored);if($(side+'MirrorRibbon'))$(side+'MirrorRibbon').hidden=!state.mirrored;wrap.style.width=Math.max(vw,w+20)+'px';wrap.style.height=Math.max(vh,h+20)+'px';
    $(side+'ZoomLabel').textContent=state.zoom===1?'Vue entière':`Zoom ×${state.zoom.toLocaleString('fr-FR')}`;
    document.querySelector(`[data-zoom="out"][data-side="${side}"]`).disabled=state.zoom<=1;
    document.querySelector(`[data-zoom="in"][data-side="${side}"]`).disabled=state.zoom>=4;
  }
  function renderImage(side) {
    const state=sides[side],item=object(state.id),img=$(side+'Image'),stage=$(side+'Stage');
    $(side+'Choice').value=state.id;
    const path=typeof item?.image==='string' && !/^(?:[a-z]+:|\/\/)/i.test(item.image) ? item.image : '';
    img.alt=item ? `${item.title} — ${item.institution || ''}, ${item.inventory || ''}` : '';
    stage.hidden=!path;$(side+'Viewport').querySelector('.image-empty').hidden=!!path;
    if(path){img.onload=()=>{stage.hidden=false;$(side+'Viewport').querySelector('.image-empty').hidden=true;layout(side);};img.onerror=()=>{stage.hidden=true;$(side+'Viewport').querySelector('.image-empty').hidden=false;};img.src=path;}else img.removeAttribute('src');
    $(side+'Caption').innerHTML=item?`<h3>${esc(item.title)}</h3><p>${esc([item.institution,item.inventory,item.date].filter(Boolean).join(' · '))}</p>`:'<p>Aucun témoin chargé.</p>';
    layout(side);renderMarkers();
  }
  function renderList() {
    const items=visible(),all=observations();$('observationCount').textContent=items.length;
    $('observationsList').innerHTML=items.length?items.map(item=>`<button type="button" class="observation-card ${selected===item.id?'selected':''}" data-observation="${esc(item.id)}" aria-pressed="${selected===item.id}"><div class="observation-card-top"><span class="observation-index">${String(all.findIndex(x=>x.id===item.id)+1).padStart(2,'0')} / ${esc(labels.type[item.type]||item.type)}</span><span class="evidence-tag ${esc(item.evidence_kind)}">${esc(labels.evidence[item.evidence_kind]||item.evidence_kind)}</span></div><p>${esc(item.statement)}</p><div class="observation-card-bottom"><span>${esc(object(item.object_id)?.inventory||object(item.object_id)?.title||item.object_id)}${validBox(item.bbox)?' · repère':''}</span><span class="certainty ${esc(item.certainty)}">${esc(labels.certainty[item.certainty]||item.certainty)}</span></div></button>`).join(''):'<p class="empty-state">Aucune observation pour ces filtres.<br>Vous pouvez enrichir le carnet.</p>';
    renderMarkers();
  }
  function renderEditor() {
    const item=observations().find(x=>x.id===selected),editor=$('observationEditor');editor.hidden=!item;if(!item)return;
    editor.innerHTML=`<h3>Note de travail <span class="count">/ ${esc(item.entity_id||'')}</span></h3><div class="editor-source">${link(item.source_url,'Consulter la source')||'Aucune source liée.'}</div><label for="editCertainty">Confiance de cette observation</label><select id="editCertainty">${Object.entries(labels.certainty).map(([value,label])=>`<option value="${value}" ${item.certainty===value?'selected':''}>${label}</option>`).join('')}</select><label for="editNote">Votre note<textarea id="editNote" rows="4" maxlength="10000" placeholder="Préciser, nuancer, consigner un désaccord…">${esc(item.note||'')}</textarea></label><p class="editor-note">${validBox(item.bbox)?'Repère approximatif dans l’image entière.':'Observation sans localisation graphique.'} Les modifications sont conservées localement.</p>`;
    $('editCertainty').addEventListener('change',event=>{update(item.id,{certainty:event.target.value});renderList();});
    $('editNote').addEventListener('input',event=>update(item.id,{note:event.target.value}));
  }
  function update(id,change) {
    const before=observations().find(x=>x.id===id);if(!before)return;
    const now=new Date().toISOString();
    for(const [field,value] of Object.entries(change)){
      if(before[field]===value)continue;
      const last=changes[changes.length-1];
      if(field==='note'&&last?.observation_id===id&&last.field===field&&Date.now()-Date.parse(last.changed_at)<5000){last.after=value;last.changed_at=now;}
      else changes.push({action:'edit',observation_id:id,field,before:before[field]??null,after:value,changed_at:now,author:'Lecteur local non identifié'});
    }
    const local=added.find(x=>x.id===id);if(local)Object.assign(local,change);else overrides[id]={...overrides[id],...change};save();
  }
  function selectObservation(id) {
    const item=observations().find(x=>x.id===id);if(!item)return;selected=id;
    if(!Object.values(sides).some(side=>side.id===item.object_id)){sides.right.id=item.object_id;sides.right.zoom=1;renderImage('right');renderComparisons();}
    if(evidence!=='all'&&evidence!==item.evidence_kind){evidence='all';setEvidenceButtons();}
    if(certainty!=='all'&&certainty!==item.certainty){certainty='all';$('certaintyFilter').value='all';}
    renderList();renderEditor();
    requestAnimationFrame(()=>{const card=[...document.querySelectorAll('.observation-card')].find(node=>node.dataset.observation===id);if(card){const list=$('observationsList');list.scrollTop=Math.max(0,card.offsetTop-list.offsetTop-list.clientHeight/3);}if(validBox(item.bbox)){for(const [side,state]of Object.entries(sides)){if(state.id!==item.object_id)continue;const viewport=$(side+'Viewport'),stage=$(side+'Stage');const cx=item.bbox[0]+item.bbox[2]/2;viewport.scrollTo({left:stage.offsetLeft+(state.mirrored?1-cx:cx)*stage.clientWidth-viewport.clientWidth/2,top:stage.offsetTop+(item.bbox[1]+item.bbox[3]/2)*stage.clientHeight-viewport.clientHeight/2,behavior:'smooth'});}}});
  }
  function renderComparisons() {
    const pair=new Set(Object.values(sides).map(side=>side.id));const items=comparisons.filter(item=>pair.has(item.from_id)&&pair.has(item.to_id));$('comparisonCount').textContent=items.length?`${items.length} proposition${items.length>1?'s':''}`:'';
    $('comparisonsList').innerHTML=items.length?items.map(item=>`<article class="comparison-card"><span class="evidence-tag">${esc(labels.status[item.operation_status]||item.operation_status)}</span><h3>${esc(item.subject)}</h3><p>${esc(item.difference)}</p>${item.interpretation?`<p class="interpretation">${esc(item.interpretation)}</p>`:''}${Array.isArray(item.limitations)&&item.limitations.length?`<ul>${item.limitations.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}<div class="comparison-observations">${(item.observation_ids||[]).map(id=>{const index=observations().findIndex(obs=>obs.id===id);return index<0?'':`<button class="observation-link" data-observation="${esc(id)}">Observation ${String(index+1).padStart(2,'0')} ↗</button>`;}).join('')}</div></article>`).join(''):'<p class="empty-state">Aucune proposition renseignée pour cette paire.<br>Les observations restent consultables.</p>';
  }
  function renderProvenance() {
    const terms={medium:'Technique',physical_dimensions:'Dimensions de l’objet',image_status:'Témoin et image',attribution_note:'Attribution et état de la source'};
    $('provenanceList').innerHTML=corpus.map((item,index)=>`<article class="provenance-card"><span class="small-label">${String(index+1).padStart(2,'0')} / ${esc(item.inventory||item.id)}</span><h3>${esc(item.title)}</h3><p class="identity">${esc([item.institution,item.date].filter(Boolean).join(' · '))}</p><details><summary>Provenance et limites</summary><dl>${Object.entries(terms).filter(([key])=>item[key]).map(([key,label])=>`<dt>${label}</dt><dd>${esc(item[key])}</dd>`).join('')}${item.image_width&&item.image_height?`<dt>Fichier image</dt><dd>${esc(item.image_width)} × ${esc(item.image_height)} pixels ; aucune échelle physique déduite.</dd>`:''}</dl>${Array.isArray(item.limitations)&&item.limitations.length?`<ul>${item.limitations.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}</details><div class="source-links">${link(item.source_url,'Notice de collection')}${link(item.image_url,'Image source')}</div></article>`).join('')||'<p class="empty-state">Le dossier documentaire n’est pas encore chargé.</p>';
  }
  function setEvidenceButtons(){document.querySelectorAll('[data-evidence]').forEach(button=>{const active=button.dataset.evidence===evidence;button.classList.toggle('active',active);button.setAttribute('aria-pressed',active);});}
  load();
  for(const side of Object.keys(sides)) {
    const shell=document.createElement('div');shell.className='viewport-shell';const viewport=$(side+'Viewport');viewport.before(shell);shell.append(viewport);const ribbon=document.createElement('div');ribbon.className='mirror-ribbon';ribbon.id=side+'MirrorRibbon';ribbon.textContent='Affichage inversé · miroir de consultation';ribbon.hidden=true;shell.append(ribbon);
    const mirror=document.createElement('button');mirror.type='button';mirror.className='mirror-button';mirror.id=side+'Mirror';mirror.textContent='Miroir d’affichage';mirror.setAttribute('aria-pressed','false');mirror.title='Retourner l’affichage et ses repères, sans modifier les observations.';
    mirror.addEventListener('click',()=>{sides[side].mirrored=!sides[side].mirrored;mirror.setAttribute('aria-pressed',String(sides[side].mirrored));layout(side);});
    $(side+'Caption').before(mirror);
    $(side+'Choice').innerHTML=corpus.map(item=>`<option value="${esc(item.id)}">${esc(item.title)}</option>`).join('');
    $(side+'Choice').addEventListener('change',event=>{sides[side].id=event.target.value;sides[side].zoom=1;renderImage(side);renderList();renderComparisons();});
    if(window.ResizeObserver)new ResizeObserver(()=>layout(side)).observe($(side+'Viewport'));
    renderImage(side);
  }
  window.addEventListener('resize',()=>Object.keys(sides).forEach(layout));
  $('newObject').innerHTML=corpus.map(item=>`<option value="${esc(item.id)}">${esc(item.title)}</option>`).join('');
  $('addButton').disabled=!corpus.length;
  document.addEventListener('click',event=>{const observation=event.target.closest('[data-observation]');if(observation){selectObservation(observation.dataset.observation);return;}const button=event.target.closest('[data-zoom]');if(button){const side=button.dataset.side;const viewport=$(side+'Viewport');const old=sides[side].zoom;const centerX=(viewport.scrollLeft+viewport.clientWidth/2)/Math.max(1,viewport.scrollWidth),centerY=(viewport.scrollTop+viewport.clientHeight/2)/Math.max(1,viewport.scrollHeight);sides[side].zoom=button.dataset.zoom==='fit'?1:Math.max(1,Math.min(4,old+(button.dataset.zoom==='in'?.5:-.5)));layout(side);viewport.scrollTo({left:Math.max(0,centerX*viewport.scrollWidth-viewport.clientWidth/2),top:Math.max(0,centerY*viewport.scrollHeight-viewport.clientHeight/2)});}});
  document.querySelectorAll('[data-evidence]').forEach(button=>button.addEventListener('click',()=>{evidence=button.dataset.evidence;setEvidenceButtons();renderList();}));
  $('certaintyFilter').addEventListener('change',event=>{certainty=event.target.value;renderList();});
  $('pairOnly').addEventListener('change',renderList);$('showMarkers').addEventListener('change',renderMarkers);
  $('addButton').addEventListener('click',()=>{$('addForm').reset();$('newObject').value=sides.right.id;$('formError').textContent='';$('addDialog').showModal();});
  $('closeDialog').addEventListener('click',()=>$('addDialog').close());$('cancelDialog').addEventListener('click',()=>$('addDialog').close());
  $('addForm').addEventListener('submit',event=>{
    event.preventDefault();const form=new FormData(event.target),statement=String(form.get('statement')||'').trim();if(!statement){$('formError').textContent='Saisissez une observation.';return;}
    const raw=['x','y','w','h'].map(key=>String(form.get('bbox_'+key)||'').trim());let bbox=null;
    if(raw.some(Boolean)){bbox=raw.map(value=>Number(value)/100);if(!raw.every(Boolean)||!validBox(bbox)){$('formError').textContent='Le repère demande quatre valeurs et doit rester à l’intérieur de l’image.';return;}}
    const source=String(form.get('source_url')||'').trim();if(source&&!sourceHref(source)){$('formError').textContent='Utilisez une adresse de source commençant par http ou https.';return;}
    const selectedObject=object(form.get('object_id'));if(!selectedObject){$('formError').textContent='Choisissez un témoin du dossier.';return;}
    const id='obs-local-'+(window.crypto?.randomUUID?.()||Date.now()+'-'+Math.random().toString(36).slice(2));
    const created=new Date().toISOString();
    const newObservation={id,object_id:selectedObject.id,entity_id:String(form.get('entity_id')||'E1'),type:form.get('type'),statement,certainty:form.get('certainty'),evidence_kind:form.get('evidence_kind'),source_url:source,bbox,note:String(form.get('note')||''),origin:'local',observer:'Lecteur local non identifié',created,created_at:created,image:selectedObject.image||null,image_width:selectedObject.image_width||null,image_height:selectedObject.image_height||null,image_sha256:data.meta?.asset_hashes?.[selectedObject.id]||null,dataset_id:datasetId,dataset_hash:datasetHash};
    added.push(newObservation);changes.push({action:'create',observation_id:id,before:null,after:{...newObservation},changed_at:newObservation.created_at,author:'Lecteur local non identifié'});
    save();$('addDialog').close();selectObservation(id);
  });
  $('exportButton').addEventListener('click',()=>{
    const payload={schema_version:'1.0',exported_at:new Date().toISOString(),project:'xanto',dataset_id:datasetId,dataset_hash:datasetHash,source_original:{meta:data.meta||{},corpus,observations:original,comparisons},observations:observations(),comparisons,changes,local_changes:{overrides,added_ids:added.map(item=>item.id)},unapplied_previous_draft:previousDraft,scope_note:'Observations et interprétations de travail ; localisations approximatives, aucune mesure physique ni validation scientifique. Le miroir et le zoom sont des états d’affichage, pas des opérations historiques.'};
    try{const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json;charset=utf-8'});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download='xanto-annotations-'+new Date().toISOString().slice(0,10)+'.json';document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch{status('L’export n’a pas pu être créé par ce navigateur. Vos observations restent affichées.',true);}
  });
  $('exportPreviousDraft').addEventListener('click',()=>{
    if(!previousDraft)return;
    try{const raw=typeof previousDraft.raw==='string'?previousDraft.raw:JSON.stringify(previousDraft,null,2);const isRaw=typeof previousDraft.raw==='string';const blob=new Blob([raw],{type:isRaw?'text/plain;charset=utf-8':'application/json;charset=utf-8'});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download='xanto-ancien-brouillon-'+new Date().toISOString().slice(0,10)+(isRaw?'.txt':'.json');document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch{status('L’ancien brouillon reste conservé, mais son téléchargement a échoué dans ce navigateur.',true);}
  });
  $('resetButton').addEventListener('click',()=>{if(!window.confirm('Supprimer vos notes, changements de confiance, observations ajoutées et anciens brouillons dans ce navigateur ? Le dossier d’origine sera conservé. Exportez d’abord si vous souhaitez garder une copie.'))return;try{localStorage.removeItem(storeKey);overrides={};added=[];changes=[];previousDraft=null;selected=null;status('Le carnet d’origine a été restauré.');renderList();renderEditor();renderComparisons();}catch{status('La remise à zéro du stockage a échoué. Vos annotations sont conservées.',true);}});
  renderList();renderComparisons();renderProvenance();
  if(!corpus.length)status('Le dossier est en préparation. Les images et observations apparaîtront une fois les données disponibles.');
})();
