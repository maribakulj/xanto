(() => {
  'use strict';
  const bundle=window.MNEMOSYNE_CV||{}, inputs=bundle.inputs||{};
  const images=Array.isArray(inputs.images)?inputs.images:[];
  const catalogue=Array.isArray(window.MNEMOSYNE_DATA?.corpus)?window.MNEMOSYNE_DATA.corpus:[];
  const $=id=>document.getElementById(id);
  if(!$('cvSection'))return;
  const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const query=(Array.isArray(inputs.queries)?inputs.queries:[])[0]||(Array.isArray(bundle.dino?.queries)?bundle.dino.queries:[])[0]||(Array.isArray(bundle.baseline?.queries)?bundle.baseline.queries:[])[0]||null;
  const image=id=>images.find(item=>item.id===id);
  const title=id=>catalogue.find(item=>item.id===id)?.title||id||'Témoin non renseigné';
  const shortTitle=id=>({parnassus:'Parnasse — contrôle source',apollo:'Apollon et Pan — reprise',paris:'Jugement de Pâris — reprise'}[id]||title(id));
  const number=value=>Number.isFinite(value)?value.toLocaleString('fr-FR',{minimumFractionDigits:3,maximumFractionDigits:3}):'—';
  const validBox=box=>Array.isArray(box)&&box.length===4&&box.every(Number.isFinite)&&box[0]>=0&&box[1]>=0&&box[2]>0&&box[3]>0&&box[0]+box[2]<=1.00001&&box[1]+box[3]<=1.00001;
  const safeImage=value=>typeof value==='string'&&!/^(?:[a-z]+:|\/\/)/i.test(value)?value:'';
  let method='dino',target=images.find(item=>item.id!==query?.source_id)?.id||images[0]?.id||'',selectedRank=1,zoom=1;
  const output=()=>bundle[method]||null;
  const result=()=>Array.isArray(output()?.results)?output().results.find(item=>item.query_id===query?.id&&item.target_id===target)||null:null;
  const proposals=()=>Array.isArray(result()?.proposals)?result().proposals.filter(item=>validBox(item.bbox)).slice(0,5):[];
  const activeProposal=()=>proposals().find(item=>item.rank===selectedRank)||proposals()[0]||null;
  const control=()=>(Array.isArray(bundle.controls?.results)?bundle.controls.results:[]).find(item=>item.target_id===target&&(!item.query_id||item.query_id===query?.id))||null;
  const metric=(key=method)=>{
    const out=bundle[key];const res=Array.isArray(out?.results)?out.results.find(item=>item.target_id===target&&item.query_id===query?.id):null;
    const name=res?.method||out?.run?.method;
    return (Array.isArray(bundle.evaluation?.results)?bundle.evaluation.results:[]).find(item=>item.target_id===target&&(item.method===name||item.method===key))||null;
  };
  function positionBox(element,box){element.style.left=box[0]*100+'%';element.style.top=box[1]*100+'%';element.style.width=box[2]*100+'%';element.style.height=box[3]*100+'%';}
  function layout(){
    const viewport=$('cvTargetViewport'),stage=$('cvTargetStage'),wrap=$('cvTargetWrap'),img=$('cvTargetImage'),item=image(target);
    const width=img.naturalWidth||item?.width||1,height=img.naturalHeight||item?.height||1,vw=viewport.clientWidth,vh=viewport.clientHeight;
    const fit=Math.min((vw-20)/width,(vh-20)/height),w=Math.max(1,width*fit*zoom),h=Math.max(1,height*fit*zoom);
    stage.style.width=w+'px';stage.style.height=h+'px';wrap.style.width=Math.max(vw,w+20)+'px';wrap.style.height=Math.max(vh,h+20)+'px';
    $('cvZoomStatus').textContent=zoom===1?'Image entière':`Vue cadrée · ×${zoom.toLocaleString('fr-FR',{maximumFractionDigits:1})}`;
  }
  function focusCandidate(){
    const item=activeProposal();if(!item)return;
    const source=image(target),img=$('cvTargetImage'),vw=$('cvTargetViewport').clientWidth,vh=$('cvTargetViewport').clientHeight;
    const width=img.naturalWidth||source?.width||1,height=img.naturalHeight||source?.height||1;
    const fit=Math.min((vw-20)/width,(vh-20)/height);
    zoom=Math.max(1,Math.min(10,Math.min((vw-50)/(width*fit*item.bbox[2]),(vh-50)/(height*fit*item.bbox[3]))));layout();
    const viewport=$('cvTargetViewport'),stage=$('cvTargetStage');
    viewport.scrollTo({left:stage.offsetLeft+(item.bbox[0]+item.bbox[2]/2)*stage.clientWidth-viewport.clientWidth/2,top:stage.offsetTop+(item.bbox[1]+item.bbox[3]/2)*stage.clientHeight-viewport.clientHeight/2,behavior:'smooth'});
  }
  function renderMarkers(){
    $('cvCandidateMarkers').innerHTML=proposals().map(item=>`<button type="button" class="cv-candidate-marker ${item.rank===activeProposal()?.rank?'selected':''}" data-cv-rank="${Number(item.rank)}" aria-label="Cadrer le candidat ${Number(item.rank)}" style="left:${item.bbox[0]*100}%;top:${item.bbox[1]*100}%;width:${item.bbox[2]*100}%;height:${item.bbox[3]*100}%"><span>${item.rank===activeProposal()?.rank?'Candidat ':''}${Number(item.rank)}</span></button>`).join('');
    const reference=metric()?.reference_bbox,show=$('cvShowReference').checked&&validBox(reference);$('cvReferenceBox').hidden=!show;if(show)positionBox($('cvReferenceBox'),reference);
  }
  function renderCandidates(){
    const items=proposals(),res=result();
    $('cvCandidates').innerHTML=items.length?items.map(item=>`<button type="button" class="cv-candidate ${item.rank===activeProposal()?.rank?'selected':''}" data-cv-rank="${Number(item.rank)}" aria-pressed="${item.rank===activeProposal()?.rank}"><span class="cv-candidate-rank">${Number(item.rank)}</span><span class="cv-candidate-description"><strong>Candidat ${Number(item.rank)}</strong>Région calculée</span><span class="cv-candidate-score">${number(item.score)}</span></button>`).join(''):`<p class="cv-empty-results">${res?'Aucune proposition enregistrée pour cette cible.':'Aucun résultat enregistré pour cette méthode et cette cible.'}</p>`;
    $('cvCandidateCount').textContent=res?`${items.length} candidat${items.length>1?'s':''} présenté${items.length>1?'s':''}${Number.isFinite(res.candidate_count)?` · ${res.candidate_count.toLocaleString('fr-FR')} positions évaluées`:''}`:'';
    const first=items.find(item=>item.rank===1),fifth=items.find(item=>item.rank===5);
    $('cvScoreSpread').textContent=Number.isFinite(first?.score)&&Number.isFinite(fifth?.score)?`Écart de score entre les rangs 1 et 5 : ${number(first.score-fifth.score)}. Aucun seuil de fiabilité n’est calibré pour cet écart.`:'';
    $('cvScoreDefinition').textContent=method==='dino'?'Similarité cosinus · pas une probabilité':'Similarité du gabarit · pas une probabilité';
    $('cvFocusCandidate').disabled=!items.length;renderMarkers();
  }
  function renderEvaluation(){
    const active=metric(),center=control(),methodLabel=method==='dino'?'DINOv2':'Gabarit de gradients';
    if(active&&Number.isFinite(active.top1_iou)){
      let location=active.top1_iou===0?'Le premier candidat ne recouvre pas le repère provisoire.':typeof active.top1_center_inside==='boolean'?`Le centre du premier candidat se situe ${active.top1_center_inside?'dans':'hors du'} repère provisoire.`:'';
      if(target==='paris'&&active.top1_center_inside===false)location='Pâris : mauvaise localisation au premier rang ; le centre du candidat est hors du repère provisoire.'+(active.top1_iou===0?' Aucun recouvrement.':'');
      if(target==='apollo'&&method==='dino'&&active.top1_center_inside===true)location='Apollon : localisation plausible dans ce pilote, avec le centre du premier candidat dans le repère provisoire.';
      const centered=Number.isFinite(center?.center_iou)?`Une boîte simplement centrée obtient une IoU de ${number(center.center_iou)} (dimensions relatives de la requête, contrôle a posteriori).`:'';
      $('cvEvaluationSummary').innerHTML=`<div class="cv-summary-value"><span>${esc(methodLabel)} · premier candidat</span><strong>IoU ${number(active.top1_iou)}</strong></div><div class="cv-summary-explanation"><p>${esc(location)} ${esc(centered)}</p><p class="cv-small">IoU : surface commune aux deux boîtes divisée par leur surface réunie, de 0 (aucun recouvrement) à 1 (boîtes identiques). Référence assistée approximative, pas une probabilité ni un benchmark indépendant. Le meilleur des cinq est un diagnostic a posteriori, pas un remplacement du premier résultat.${target===query?.source_id?' Le contrôle source réutilise la requête et ne mesure pas la généralisation.':''}</p></div>`;
    }else $('cvEvaluationSummary').innerHTML='<p class="cv-small">Premier candidat : aucune mesure de recouvrement disponible pour cette méthode et cette cible. Les propositions calculées, si présentes, restent consultables.</p>';
    const enabled=$('cvShowReference').checked;$('cvEvaluation').hidden=!enabled;if(!enabled){renderMarkers();return;}
    const rows=['dino','baseline'].map(key=>({key,value:metric(key)})).filter(item=>item.value);
    $('cvEvaluationContent').innerHTML=rows.length?`<table id="cvFirstResultTable"><caption>Premier candidat et boîte centrée — ${esc(shortTitle(target))}</caption><thead><tr><th>Méthode ou contrôle</th><th>IoU (0 à 1)</th></tr></thead><tbody>${rows.map(({key,value})=>`<tr><td>${key==='dino'?'DINOv2 · premier candidat':'Gradients · premier candidat'}</td><td>${number(value.top1_iou)}</td></tr>`).join('')}${Number.isFinite(center?.center_iou)?`<tr><td>Boîte centrée · contrôle a posteriori</td><td>${number(center.center_iou)}</td></tr>`:''}</tbody></table><p class="cv-evaluation-note">La boîte centrée reprend les dimensions relatives de la requête, sans ajustement à la référence.${target===query?.source_id?' Le contrôle source réutilise la région fournie : il ne mesure pas la généralisation.':' Les références cibles sont évaluées après le calcul et ne servent pas à proposer les régions.'}</p><details id="cvPostHocDiagnostics" class="cv-posthoc"><summary>Diagnostic a posteriori — ne remplace pas le premier résultat</summary><table><caption>Meilleur recouvrement parmi les cinq propositions déjà classées</caption><thead><tr><th>Méthode</th><th>Meilleur des 5</th><th>Rang d’origine</th></tr></thead><tbody>${rows.map(({key,value})=>`<tr><td>${key==='dino'?'DINOv2':'Gradients'}</td><td>${number(value.best_top5_iou)}</td><td>${Number.isFinite(value.best_top5_rank)?value.best_top5_rank:'—'}</td></tr>`).join('')}</tbody></table><p>Le meilleur recouvrement est choisi après comparaison à la référence. Il ne réordonne pas les prédictions et ne constitue pas un nouveau premier résultat.</p></details>${bundle.evaluation?.reference_status?`<p class="cv-evaluation-note">${esc(bundle.evaluation.reference_status)}</p>`:''}`:'<p class="cv-metric-missing">Aucune évaluation séparée n’est disponible pour cette image.</p>';
    renderMarkers();
  }
  function renderRun(){
    const out=output(),run=out?.run,res=result();$('cvRunStatus').textContent=res?'Calcul enregistré · résultats consultables':run?'Exécution disponible · cible sans résultat':'Sortie de calcul non disponible';$('cvRunStatus').classList.toggle('pending',!res);
    if(!run){$('cvRunDetails').innerHTML='<p class="cv-empty-results">Le programme de calcul n’a pas encore fourni de sortie pour cette méthode. Aucune annotation du carnet n’est utilisée comme résultat de remplacement.</p>';return;}
    const fields=[['Méthode',run.method_label||run.method],['Modèle',run.model_id],['Révision',run.model_revision],['Appareil de calcul',run.device],['Enregistré le',run.generated_at],['Durée',Number.isFinite(run.duration_seconds)?run.duration_seconds.toLocaleString('fr-FR',{maximumFractionDigits:1})+' s':null],['Empreinte des entrées',run.input_sha256]];
    $('cvRunDetails').innerHTML=`<dl>${fields.filter(([,value])=>value!==undefined&&value!==null).map(([label,value])=>`<dt>${label}</dt><dd>${esc(value)}</dd>`).join('')}</dl><p>Paramètres enregistrés avec l’exécution</p><pre>${esc(JSON.stringify(run.parameters||{},null,2))}</pre>${Array.isArray(run.limitations)&&run.limitations.length?`<ul>${run.limitations.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}${Array.isArray(res?.notes)&&res.notes.length?`<ul>${res.notes.map(text=>`<li>${esc(text)}</li>`).join('')}</ul>`:''}<p class="cv-small">Même un score élevé n’établit ni une copie historique, ni une identité iconographique, ni une intention de l’artiste. Le fichier d’Apollon, large de 570 pixels, limite les détails accessibles.</p>`;
  }
  function renderTarget(){
    const item=image(target),img=$('cvTargetImage'),path=safeImage(item?.image);zoom=1;selectedRank=1;$('cvTarget').value=target;
    $('cvTargetRole').textContent=target===query?.source_id?'Contrôle technique':'Reprise à rechercher';
    $('cvTargetCaption').textContent=title(target)+(item?.width&&item?.height?` · ${item.width.toLocaleString('fr-FR')} × ${item.height.toLocaleString('fr-FR')} pixels`:'');
    img.hidden=!path;$('cvImageEmpty').hidden=!!path;
    img.onload=()=>{img.hidden=false;$('cvImageEmpty').hidden=true;layout();};img.onerror=()=>{img.hidden=true;$('cvImageEmpty').hidden=false;};img.alt='Régions candidates calculées dans '+title(target);
    if(path)img.src=path;else img.removeAttribute('src');
    renderCandidates();renderEvaluation();renderRun();layout();$('cvTargetViewport').scrollTo({left:0,top:0});
  }
  function renderQuery(){
    const item=image(query?.source_id),path=safeImage(item?.image),crop=$('cvQueryCrop');
    $('cvQueryTitle').textContent=title(query?.source_id);$('cvQueryProvenance').textContent=query?.provenance||'Aucune région-source fournie dans les entrées disponibles.';
    if(!path||!validBox(query?.bbox)){crop.style.aspectRatio='0.7';return;}
    const box=query.bbox,img=$('cvQueryImage'),full=$('cvSourceImage');
    crop.style.aspectRatio=(item.width*box[2])/(item.height*box[3]);
    img.src=path;img.hidden=false;img.style.width=100/box[2]+'%';img.style.height=100/box[3]+'%';img.style.left=-box[0]/box[2]*100+'%';img.style.top=-box[1]/box[3]*100+'%';
    img.onerror=()=>{img.hidden=true;};full.src=path;full.hidden=false;full.onerror=()=>{full.hidden=true;$('cvSourceBox').hidden=true;};$('cvSourceBox').hidden=false;positionBox($('cvSourceBox'),box);
  }
  $('cvTarget').innerHTML=images.map(item=>`<option value="${esc(item.id)}">${esc(shortTitle(item.id))}</option>`).join('');$('cvTarget').disabled=!images.length;
  $('cvTarget').addEventListener('change',event=>{target=event.target.value;renderTarget();});
  document.querySelectorAll('input[name="cvMethod"]').forEach(input=>input.addEventListener('change',event=>{method=event.target.value;selectedRank=1;zoom=1;layout();renderCandidates();renderEvaluation();renderRun();}));
  $('cvCandidates').addEventListener('click',event=>{const item=event.target.closest('[data-cv-rank]');if(!item)return;selectedRank=Number(item.dataset.cvRank);renderCandidates();focusCandidate();});
  $('cvCandidateMarkers').addEventListener('click',event=>{const item=event.target.closest('[data-cv-rank]');if(!item)return;selectedRank=Number(item.dataset.cvRank);renderCandidates();focusCandidate();});
  $('cvFit').addEventListener('click',()=>{zoom=1;layout();$('cvTargetViewport').scrollTo({left:0,top:0});});$('cvFocusCandidate').addEventListener('click',focusCandidate);
  $('cvShowReference').addEventListener('change',renderEvaluation);
  if(window.ResizeObserver)new ResizeObserver(layout).observe($('cvTargetViewport'));window.addEventListener('resize',layout);
  renderQuery();renderTarget();
})();
