import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'tests/output');
const seed = JSON.parse(await fs.readFile(path.join(root,'data/observations.json'),'utf8'));
const initialPairCount = seed.filter(o=>['parnassus','apollo'].includes(o.object_id)).length;
await fs.mkdir(output, {recursive:true});
const url = process.env.MNEMOSYNE_TEST_URL || 'http://127.0.0.1:8767/';
const browser = await chromium.launch({channel:'chrome',headless:true});
const results = [];
const errors = [];
const context = await browser.newContext({viewport:{width:1512,height:1100},acceptDownloads:true});
const page = await context.newPage();
page.on('pageerror',e=>errors.push(e.message));
const check = (name,condition) => { assert.ok(condition,name); results.push(name); };
const imageReady = async () => page.waitForFunction(()=>[...document.querySelectorAll('.image-stage img')].every(i=>i.complete && i.naturalWidth>0));
const selectObservation = id => page.locator(`.observation-card[data-observation="${id}"]`).click();
const downloadExport = async target => {
  const pending = target.waitForEvent('download');
  await target.locator('#exportButton').click();
  const download = await pending;
  const saved = await download.path();
  return JSON.parse(await fs.readFile(saved,'utf8'));
};

try {
  await page.goto(url,{waitUntil:'networkidle'});
  await imageReady();
  check('Chargement des données et images',Number(await page.locator('#observationCount').innerText())===initialPairCount);
  await page.screenshot({path:path.join(output,'desktop.png')});

  await page.locator('#rightChoice').selectOption('paris');
  await imageReady();
  check('Image haute résolution de Pâris',await page.locator('#rightImage').evaluate(i=>i.naturalWidth)===4851);
  await page.locator('[data-evidence="catalogue"]').click();
  check('Filtre des notices',await page.locator('.observation-card').count()===2);
  await page.locator('[data-evidence="all"]').click();
  await selectObservation('obs-paris-hands');
  const marker = page.locator('#rightMarkers .marker.selected');
  const geometry = await marker.evaluate(node=>{
    const box=node.getBoundingClientRect(), image=document.querySelector('#rightImage').getBoundingClientRect();
    return {x:(box.x-image.x)/image.width,y:(box.y-image.y)/image.height,w:box.width/image.width,h:box.height/image.height};
  });
  check('Repère attaché au cadrage de Pâris',Math.abs(geometry.x-.454)<.003 && Math.abs(geometry.y-.469)<.003 && Math.abs(geometry.w-.192)<.003);

  await page.locator('[data-zoom="in"][data-side="right"]').click();
  check('Zoom de la paire', (await page.locator('#rightZoomLabel').innerText()).includes('1,5'));
  await page.locator('#rightMirror').click();
  check('Miroir image et repères',await page.locator('#rightStage').evaluate(n=>n.classList.contains('mirrored')));
  check('Miroir signalé dans la zone image',await page.locator('#rightMirrorRibbon').isVisible());
  const mirrored = await marker.evaluate(node=>{
    const box=node.getBoundingClientRect(), image=document.querySelector('#rightImage').getBoundingClientRect();
    return (box.x-image.x)/image.width;
  });
  check('Coordonnées de repère après miroir',Math.abs(mirrored-(1-.454-.192))<.003);
  await page.evaluate(()=>scrollTo(0,280));
  await page.screenshot({path:path.join(output,'mirror.png')});
  await page.locator('#rightMirror').click();
  await page.locator('[data-zoom="fit"][data-side="right"]').click();
  await page.locator('#showMarkers').uncheck();
  check('Masquage des repères',await page.locator('#rightMarkers').isHidden());
  await page.locator('#showMarkers').check();

  const note = 'Vérification locale <img src=x onerror="window.bad=true"> — contact à discuter.';
  await page.locator('#editNote').fill(note);
  await page.locator('#editCertainty').selectOption('probable');
  const draftSnapshot=await page.evaluate(()=>JSON.parse(localStorage.getItem('mnemosyne.annotations.v1')).source_snapshot);
  check('Brouillon conserve son état source',draftSnapshot.observations.length===seed.length && draftSnapshot.observations.find(o=>o.id==='obs-paris-hands').note!==note);
  await page.reload({waitUntil:'networkidle'});
  await page.locator('#rightChoice').selectOption('paris');
  await selectObservation('obs-paris-hands');
  check('Notes persistantes après rechargement',await page.locator('#editNote').inputValue()===note);
  check('Confiance persistante',await page.locator('#editCertainty').inputValue()==='probable');
  check('Note traitée comme texte',await page.evaluate(()=>!window.bad));

  await page.locator('#addButton').click();
  await page.locator('#newObject').selectOption('paris');
  await page.locator('#addForm [name="statement"]').fill('Observation de vérification, à ne pas traiter comme résultat scientifique.');
  await page.locator('#addForm [name="evidence_kind"]').selectOption('interpretation');
  await page.locator('#addForm [name="certainty"]').selectOption('indeterminate');
  await page.locator('#addForm button[type="submit"]').click();
  check('Ajout au carnet',await page.locator('#addDialog').isHidden());
  let payload = await downloadExport(page);
  check('Export avec source intacte',payload.source_original.observations.length===seed.length && payload.observations.length===seed.length+1);
  check('Empreinte du dossier exportée',/^[a-f0-9]{64}$/.test(payload.dataset_hash));
  const edited = payload.observations.find(o=>o.id==='obs-paris-hands');
  const source = payload.source_original.observations.find(o=>o.id==='obs-paris-hands');
  check('Original et modification séparés',edited.note===note && source.note!==note && source.certainty==='clear');
  check('Journal avant/après daté',payload.changes.some(c=>c.observation_id==='obs-paris-hands' && c.field==='certainty' && c.before==='clear' && c.after==='probable' && c.author && c.changed_at));
  const added = payload.observations.find(o=>o.origin==='local');
  check('Nouvelle annotation rattachée à son image',added.image==='assets/paris-front-high.jpg' && added.image_width===4851 && /^[a-f0-9]{64}$/.test(added.image_sha256) && added.created);
  await fs.writeFile(path.join(output,'export-tested.json'),JSON.stringify(payload,null,2));

  page.once('dialog',d=>d.dismiss());
  await page.locator('#resetButton').click();
  payload = await downloadExport(page);
  check('Annuler la réinitialisation conserve les notes',payload.observations.length===seed.length+1);
  page.once('dialog',d=>d.accept());
  await page.locator('#resetButton').click();
  payload = await downloadExport(page);
  check('Réinitialisation des seules annotations locales',payload.observations.length===seed.length && payload.changes.length===0);

  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
  check('Affichage étroit sans débordement horizontal',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));

  const filePage = await context.newPage();
  filePage.on('pageerror',e=>errors.push(e.message));
  await filePage.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'load'});
  await filePage.waitForFunction(()=>document.querySelector('#leftImage')?.naturalWidth>0);
  check('Fonctionnement sans serveur en fichier local',await filePage.locator('.observation-card').count()===initialPairCount);

  const noStorage = await browser.newContext({acceptDownloads:true});
  await noStorage.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Denied','SecurityError');}}));
  const blocked = await noStorage.newPage();
  blocked.on('pageerror',e=>errors.push(e.message));
  await blocked.goto(url,{waitUntil:'networkidle'});
  await blocked.locator('.observation-card[data-observation="obs-source-pose"]').click();
  await blocked.locator('#editNote').fill('Note avec stockage bloqué.');
  check('Stockage indisponible signalé', (await blocked.locator('#storageStatus').innerText()).includes('indisponible'));
  const rescued=await downloadExport(blocked);
  check('Export disponible même sans stockage',rescued.observations.find(o=>o.id==='obs-source-pose').note==='Note avec stockage bloqué.');
  await noStorage.close();

  const legacyContext = await browser.newContext({acceptDownloads:true});
  const incompatibleDraft={version:1,dataset_id:'mnemosyne-xanto-a-v0.1',dataset_hash:'old-version',overrides:{'obs-source-pose':{note:'Ancienne note à préserver.'}},added:[],changes:[]};
  await legacyContext.addInitScript(draft=>localStorage.setItem('mnemosyne.annotations.v1',JSON.stringify(draft)),incompatibleDraft);
  const legacy=await legacyContext.newPage();
  await legacy.goto(url,{waitUntil:'networkidle'});
  const legacyExport=await downloadExport(legacy);
  check('Ancien brouillon conservé séparément',legacyExport.unapplied_previous_draft.overrides['obs-source-pose'].note==='Ancienne note à préserver.');
  check('Ancien brouillon non appliqué silencieusement',legacyExport.observations.find(o=>o.id==='obs-source-pose').note!=='Ancienne note à préserver.');
  await legacy.locator('.observation-card[data-observation="obs-source-pose"]').click();
  await legacy.locator('#editNote').fill('Nouvelle note, ancien brouillon toujours conservé.');
  check('Avis de brouillon permanent après édition',await legacy.locator('#draftNotice').isVisible());
  await legacyContext.close();

  const corruptedContext = await browser.newContext({acceptDownloads:true});
  const broken='{"version":1,"overrides":{"obs-source-pose":{"note":"note sauvegardée tronquée';
  await corruptedContext.addInitScript(raw=>localStorage.setItem('mnemosyne.annotations.v1',raw),broken);
  const corrupted=await corruptedContext.newPage();
  await corrupted.goto(url,{waitUntil:'networkidle'});
  await corrupted.locator('.observation-card[data-observation="obs-source-pose"]').click();
  await corrupted.locator('#editNote').fill('Nouvelle note après erreur.');
  const recovered=await downloadExport(corrupted);
  check('Brouillon corrompu préservé après nouvelle édition',recovered.unapplied_previous_draft.raw===broken);
  const pendingRaw=corrupted.waitForEvent('download');
  await corrupted.locator('#exportPreviousDraft').click();
  const rawDownload=await pendingRaw;
  check('Export dédié du brouillon brut',await fs.readFile(await rawDownload.path(),'utf8')===broken);
  await corruptedContext.close();
  check('Aucune erreur JavaScript',errors.length===0);
  await fs.writeFile(path.join(output,'browser-results.json'),JSON.stringify({passed:results.length,results,errors},null,2));
  console.log(JSON.stringify({passed:results.length,results,errors},null,2));
} finally {
  await browser.close();
}
