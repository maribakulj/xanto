import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'tests/output');
const dino=JSON.parse(await fs.readFile(path.join(root,'cv/results.json'),'utf8'));
const baseline=JSON.parse(await fs.readFile(path.join(root,'cv/baseline_results.json'),'utf8'));
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1512,height:1100}});
const page=await context.newPage(), errors=[], results=[];
page.on('pageerror',error=>errors.push(error.message));
const check=(name,condition)=>{assert.ok(condition,name);results.push(name);};
const row=(data,target)=>data.results.find(item=>item.target_id===target);
const scoreText=value=>value.toLocaleString('fr-FR',{minimumFractionDigits:3,maximumFractionDigits:3});
const imagesReady=()=>page.waitForFunction(()=>['cvQueryImage','cvTargetImage'].every(id=>document.getElementById(id)?.naturalWidth>0));
const candidateGeometry=()=>page.locator('#cvCandidateMarkers [data-cv-rank="1"]').evaluate(node=>{
  const a=node.getBoundingClientRect(),b=document.getElementById('cvTargetImage').getBoundingClientRect();
  return [(a.x-b.x)/b.width,(a.y-b.y)/b.height,a.width/b.width,a.height/b.height];
});

try {
  await fs.mkdir(output,{recursive:true});
  await page.goto(process.env.XANTO_TEST_URL||'http://127.0.0.1:8767/',{waitUntil:'networkidle'});
  await imagesReady();
  check('Cinq propositions calculées dès le chargement',await page.locator('#cvCandidates [data-cv-rank]').count()===5);
  check('Scores affichés issus des résultats DINOv2',JSON.stringify(await page.locator('#cvCandidates .cv-candidate-score').allTextContents())===JSON.stringify(row(dino,'apollo').proposals.map(p=>scoreText(p.score))));
  check('Évaluation accessible sans sélection manuelle',await page.locator('#cvEvaluationSummary').isVisible() && (await page.locator('#cvEvaluationSummary').innerText()).includes('0,707'));
  check('Référence séparée et masquée au chargement',await page.locator('#cvReferenceBox').isHidden());
  const geometry=await candidateGeometry();
  check('Boîte du premier candidat alignée sur ses coordonnées calculées',geometry.every((v,i)=>Math.abs(v-row(dino,'apollo').proposals[0].bbox[i])<.003));

  await page.locator('#cvTarget').selectOption('paris');
  await imagesReady();
  check('Premier choix de Pâris conservé malgré son faible recouvrement',(await page.locator('#cvEvaluationSummary').innerText()).includes('0,244') && (await page.locator('#cvCandidates .selected').getAttribute('data-cv-rank'))==='1');
  await page.locator('#cvShowReference').check();
  check('Référence visible seulement sur demande',await page.locator('#cvReferenceBox').isVisible());
  check('Boîte centrée présente dans l’évaluation',(await page.locator('#cvEvaluationContent').innerText()).includes('centrée'));
  const before=await page.locator('#cvCandidates [data-cv-rank]').evaluateAll(nodes=>nodes.map(n=>n.dataset.cvRank));
  await page.locator('#cvCandidates [data-cv-rank="3"]').click();
  check('Choisir un candidat ne reclasse pas les propositions',JSON.stringify(before)===JSON.stringify(await page.locator('#cvCandidates [data-cv-rank]').evaluateAll(nodes=>nodes.map(n=>n.dataset.cvRank))));
  check('Évaluation reste celle du premier choix après inspection du rang 3',(await page.locator('#cvEvaluationSummary').innerText()).includes('0,244'));
  check('Cadrage du candidat fonctionne',!(await page.locator('#cvZoomStatus').innerText()).includes('Image entière'));
  await page.locator('#cvFit').click();
  check('Retour à l’image entière',await page.locator('#cvZoomStatus').innerText()==='Image entière');
  await page.locator('#cvCandidates [data-cv-rank="1"]').click();
  await page.locator('#cvFit').click();
  await page.locator('#cvSection').screenshot({path:path.join(output,'cv-paris.png')});

  await page.locator('#cvMethodBaseline').check();
  check('Méthode simple affiche ses propres scores',JSON.stringify(await page.locator('#cvCandidates .cv-candidate-score').allTextContents())===JSON.stringify(row(baseline,'paris').proposals.map(p=>scoreText(p.score))));
  check('Erreur de la baseline visible dans le bilan',(await page.locator('#cvEvaluationSummary').innerText()).includes('0,000'));
  await page.locator('#cvMethodDino').check();
  await page.locator('#cvTarget').selectOption('apollo');
  await page.locator('#cvShowReference').uncheck();
  await page.locator('#cvSection').screenshot({path:path.join(output,'cv-apollo.png')});
  await page.setViewportSize({width:390,height:844});
  await page.locator('#cvSection').scrollIntoViewIfNeeded();
  check('Vue mobile sans débordement horizontal',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));
  await page.screenshot({path:path.join(output,'cv-mobile.png')});

  const filePage=await context.newPage();
  filePage.on('pageerror',error=>errors.push(error.message));
  await filePage.goto(pathToFileURL(path.join(root,'index.html')).href,{waitUntil:'load'});
  await filePage.waitForFunction(()=>document.getElementById('cvTargetImage')?.naturalWidth>0);
  check('Résultats calculés consultables sans serveur',await filePage.locator('#cvCandidates [data-cv-rank]').count()===5);
  check('Aucune erreur JavaScript',errors.length===0);
  const report={passed:results.length,results,errors};
  await fs.writeFile(path.join(output,'cv-browser-results.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
} finally {
  await browser.close();
}
