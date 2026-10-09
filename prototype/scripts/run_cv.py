#!/usr/bin/env python3
"""Local DINOv2 dense-patch search. Reads only cv/inputs.json, images and cache.

The source ROI is supplied, never discovered. No target reference boxes, object
annotations, titles or catalogue descriptions are consumed by this program.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import platform
import numpy as np
from PIL import Image
import torch
import transformers
from transformers import AutoImageProcessor, AutoModel

# Fixed before the first target run, also shared with the baseline author.
HEIGHT_FRACTIONS = [0.18, 0.24, 0.32, 0.42, 0.55, 0.72]
PYRAMID_LEVELS = [1, 2, 3]
NMS_IOU = 0.35
PATCH_SIZE = 14
METHOD = 'dinov2_spatial_pyramid'
ALGORITHM_VERSION = '1.0'


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def resized_dimensions(width, height, max_side):
    scale = max_side / max(width, height)
    return tuple(max(PATCH_SIZE * 2, int(round(v * scale / PATCH_SIZE)) * PATCH_SIZE)
                 for v in (width, height))


def integral_map(features):
    integral = np.zeros((features.shape[0] + 1, features.shape[1] + 1,
                         features.shape[2]), dtype=np.float32)
    integral[1:, 1:] = features.cumsum(0).cumsum(1)
    return integral


def at(integral, x, y):
    """Interpolate cumulative area: exact integration of piecewise-constant patches."""
    x = np.clip(np.asarray(x), 0, integral.shape[1] - 1)
    y = np.clip(np.asarray(y), 0, integral.shape[0] - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    x1 = np.minimum(x0 + 1, integral.shape[1] - 1)
    y1 = np.minimum(y0 + 1, integral.shape[0] - 1)
    wx = (x - x0)[..., None]; wy = (y - y0)[..., None]
    return ((1-wx)*(1-wy)*integral[y0, x0] + wx*(1-wy)*integral[y0, x1]
            + (1-wx)*wy*integral[y1, x0] + wx*wy*integral[y1, x1])


def cell_descriptor(integral, boxes, level, row, col):
    x, y, w, h = np.asarray(boxes, dtype=np.float32).T
    x0 = x + col*w/level; x1 = x + (col+1)*w/level
    y0 = y + row*h/level; y1 = y + (row+1)*h/level
    value = at(integral,x1,y1)-at(integral,x0,y1)-at(integral,x1,y0)+at(integral,x0,y0)
    # Cell area cancels in normalization; stable normalization retains equal-cell weight.
    return value / np.maximum(np.linalg.norm(value, axis=-1, keepdims=True), 1e-12)


def query_descriptor(integral, box):
    return {(level,row,col):cell_descriptor(integral,[box],level,row,col)[0]
            for level in PYRAMID_LEVELS for row in range(level) for col in range(level)}


def score_boxes(integral, boxes, template):
    scores = np.zeros(len(boxes),dtype=np.float32)
    for start in range(0,len(boxes),256):
        batch = boxes[start:start+256]
        result = np.zeros(len(batch),dtype=np.float32)
        for (level,row,col), query_cell in template.items():
            descriptor = cell_descriptor(integral,batch,level,row,col)
            result += (descriptor @ query_cell) / (len(PYRAMID_LEVELS)*level*level)
        scores[start:start+len(batch)] = result
    return np.clip(scores,-1,1)


def windows(width,height,aspect):
    rows=[]; seen=set()
    for fraction in HEIGHT_FRACTIONS:
        h=max(2,int(round(height*fraction/PATCH_SIZE)))
        w=max(2,int(round(h*aspect)))
        if (w,h) in seen or w>width//PATCH_SIZE or h>height//PATCH_SIZE:
            continue
        seen.add((w,h))
        for y in range(height//PATCH_SIZE-h+1):
            for x in range(width//PATCH_SIZE-w+1):
                rows.append((x,y,w,h))
    return np.asarray(rows,dtype=np.float32)


def iou_one(box, others):
    x,y,w,h=box
    intersection=np.maximum(0,np.minimum(x+w,others[:,0]+others[:,2])-np.maximum(x,others[:,0]))
    intersection*=np.maximum(0,np.minimum(y+h,others[:,1]+others[:,3])-np.maximum(y,others[:,1]))
    return intersection/np.maximum(w*h+others[:,2]*others[:,3]-intersection,1e-12)


def top_proposals(boxes,scores,width,height,k):
    order=np.argsort(-scores,kind='stable'); selected=[]
    while len(order) and len(selected)<k:
        chosen=int(order[0]);selected.append(chosen)
        rest=order[1:]
        order=rest[iou_one(boxes[chosen],boxes[rest])<=NMS_IOU]
    return [dict(rank=rank+1,bbox=[float(boxes[i,0]*PATCH_SIZE/width),
                float(boxes[i,1]*PATCH_SIZE/height),float(boxes[i,2]*PATCH_SIZE/width),
                float(boxes[i,3]*PATCH_SIZE/height)],score=float(scores[i]))
            for rank,i in enumerate(selected)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--device',choices=['auto','cpu','mps'],default='auto')
    args=parser.parse_args();root=args.root
    start=time.perf_counter()
    script_sha256=sha256_bytes(Path(__file__).read_bytes())
    input_bytes=(root/'cv/inputs.json').read_bytes();inputs=json.loads(input_bytes)
    settings=inputs['parameters'];torch.manual_seed(settings.get('seed',0));np.random.seed(settings.get('seed',0))
    device=('mps' if torch.backends.mps.is_available() else 'cpu') if args.device=='auto' else args.device
    model_id=settings['model_id'];revision=settings['model_revision'];max_side=settings['max_image_side']
    cache=root/'cv/cache';cache.mkdir(parents=True,exist_ok=True)
    model=None;processor=None;maps={};notes={};metadata={}
    for item in inputs['images']:
        path=root/item['image'];raw=path.read_bytes();digest=sha256_bytes(raw)
        if digest!=item['sha256']:raise ValueError('Image checksum mismatch: '+item['id'])
        with Image.open(path) as picture:
            if picture.size!=(item['width'],item['height']):raise ValueError('Image dimensions mismatch: '+item['id'])
            width,height=resized_dimensions(*picture.size,max_side)
            picture=picture.convert('RGB').resize((width,height),Image.Resampling.BICUBIC)
            key=sha256_bytes(json.dumps(dict(image=digest,model=model_id,revision=revision,
                width=width,height=height,algorithm=ALGORITHM_VERSION,dtype='float32',device=device),sort_keys=True).encode())
            cached=cache/(key+'.npz')
            if cached.exists():
                with np.load(cached,allow_pickle=False) as saved:features=saved['features']
                status='cache hit'
            else:
                if model is None:
                    processor=AutoImageProcessor.from_pretrained(model_id,revision=revision,local_files_only=True)
                    model=AutoModel.from_pretrained(model_id,revision=revision,local_files_only=True).eval().to(device)
                    if model.config.patch_size!=PATCH_SIZE:raise ValueError('Unexpected patch size')
                pixels=processor(images=picture,do_resize=False,do_center_crop=False,return_tensors='pt')['pixel_values'].to(device)
                with torch.inference_mode():
                    output=model(pixel_values=pixels).last_hidden_state[:,1:,:]
                    expected=height//PATCH_SIZE* (width//PATCH_SIZE)
                    if output.shape[1]!=expected:raise ValueError('Unexpected patch-token count')
                    features=output[0].reshape(height//PATCH_SIZE,width//PATCH_SIZE,-1).float().cpu().numpy()
                # Each patch is normalized before spatial averaging; no CLS token is used.
                features/=np.maximum(np.linalg.norm(features,axis=-1,keepdims=True),1e-12)
                np.savez_compressed(cached,features=features)
                status='computed'
                del pixels,output
            maps[item['id']]=integral_map(features)
            metadata[item['id']]=dict(resized_width=width,resized_height=height,patch_grid=[width//PATCH_SIZE,height//PATCH_SIZE],cache_status=status,cache_key=key)
            notes[item['id']]=['Carte de patches spatiaux DINOv2 ; token CLS exclu.',
                'Image entière redimensionnée, sans découpage central ; côtés arrondis aux multiples de 14.',
                'La carte conserve le contexte global de chaque image : ce ne sont pas des descripteurs de crops isolés.']
            print(json.dumps({'image':item['id'],**metadata[item['id']]}),flush=True)
    results=[]
    image_by_id={x['id']:x for x in inputs['images']}
    for query in inputs['queries']:
        source=image_by_id[query['source_id']];source_map=maps[query['source_id']]
        x,y,w,h=query['bbox'];gw=source_map.shape[1]-1;gh=source_map.shape[0]-1
        template=query_descriptor(source_map,[x*gw,y*gh,w*gw,h*gh])
        aspect=(source['width']*w)/(source['height']*h)
        for item in inputs['images']:
            target=item['id'];info=metadata[target];width=info['resized_width'];height=info['resized_height']
            boxes=windows(width,height,aspect)
            scores=score_boxes(maps[target],boxes,template)
            proposals=top_proposals(boxes,scores,width,height,settings['top_k'])
            target_notes=list(notes[target])
            if target==query['source_id']:target_notes.append('Contrôle dans l’image source : la requête fournie sert à construire le gabarit, mais sa boîte exacte n’est pas injectée dans les candidats.')
            results.append(dict(query_id=query['id'],target_id=target,method=METHOD,proposals=proposals,
                candidate_count=len(boxes),heatmap=None,notes=target_notes))
            print(json.dumps({'target':target,'candidate_count':len(boxes),'top1':proposals[0] if proposals else None}),flush=True)
    output=dict(schema_version='1.0',run=dict(method=METHOD,method_label='DINOv2 — recherche spatiale multi-échelle',
        model_id=model_id,model_revision=revision,device=device,generated_at=datetime.now(timezone.utc).isoformat(),
        duration_seconds=round(time.perf_counter()-start,3),input_sha256=sha256_bytes(input_bytes),script_sha256=script_sha256,
        parameters=dict(**settings,algorithm_version=ALGORITHM_VERSION,height_fractions=HEIGHT_FRACTIONS,
          template_levels=PYRAMID_LEVELS,level_weight='equal; each level averages its cell cosine similarities',
          scoring='cosine of concatenated cell descriptors normalized and weighted per level',
          patch_size=PATCH_SIZE,stride_pixels=PATCH_SIZE,min_window_pixels=28,nms_iou=NMS_IOU,
          window_aspect='query bbox pixel aspect ratio, rounded to whole patches',mirror_search=False,
          crop_query_forward=False,feature_layer='last_hidden_state patch tokens excluding CLS',
          pixel_normalization='cached model processor, no automatic resizing or center crop',
          resize='PIL bicubic; max side 728 then each side rounded to 14 pixels',
          precision='float32',images=metadata,python=platform.python_version(),torch=torch.__version__,transformers=transformers.__version__),
        limitations=['Région source fournie par un relevé assisté, pas détectée automatiquement.',
          'Aucune boîte cible, annotation, comparaison ou notice lue par le programme.',
          'Aucun réglage effectué après examen des résultats sur les reprises.',
          'Scores cosinus de descripteurs : ni probabilités ni preuves de filiation historique.',
          'Recherche sur six tailles et une grille de 14 pixels ; régions manquées possibles.',
          'Rapport de forme conservé approximativement ; ni miroir ni déformation articulée recherchés.',
          'Modèle générique ; contexte, couleurs, support et résolution peuvent influer sur les correspondances.',
          'Trois images dont un contrôle source ; aucun benchmark indépendant.',
          'Après le premier calcul, ajout de la seule empreinte du script aux métadonnées, puis réexécution avec les mêmes paramètres et cartes en cache ; aucun réglage des résultats.']),
        queries=inputs['queries'],results=results)
    (root/'cv/results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('Wrote cv/results.json',flush=True)

if __name__=='__main__':main()
