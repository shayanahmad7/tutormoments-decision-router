"""Independent structural and arithmetic audit. Offline only."""
from pathlib import Path
import collections,csv,hashlib,json,sys
H=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 cfg=read(H/'frozen.json');cases=cfg['cases'];assert len(cases)==32
 assert len({c['student_id'] for c in cases})==32
 assert collections.Counter(c['reference'] for c in cases)=={'rigor':16,'scaffolding':16}
 checks=collections.Counter();failures=[]
 for c in cases:
  route=read(H/'traces'/f'route-{c["index"]}.json')
  assert route['payload_sha256']==digest(route['payload'])
  assert route['response']['model']=='jev-1.14.0';checks['routes']+=1
  lr=read(H/'traces'/f'llmroute-{c["index"]}.json')
  assert lr['status']=='complete' and json.loads(lr['text'])['decision'] in ['scaffolding','rigor'];checks['llm_routes']+=1
  for model in cfg['models']:
   short=model.split('/')[-1];jp=H/'ratings'/f'judge1-{c["index"]}-{short}.json'
   if not jp.exists():failures.append(str(jp.name));continue
   j=read(jp);assert set(j['mapping'].values())==set(cfg['arms'])
   assert len(j['ratings'])==5 and {r['id'] for r in j['ratings']}==set(j['mapping']);checks['judge_batches']+=1
   j2=read(H/'ratings'/f'judge2-{c["index"]}-{short}.json')
   assert set(j2['mapping'].values())==set(cfg['arms']) and len(j2['ratings'])==5
   assert {r['id'] for r in j2['ratings']}==set(j2['mapping']);checks['second_judge_batches']+=1
   for arm in cfg['arms']:
    r=read(H/'traces'/f'gen-{c["index"]}-{short}-{arm}.json')
    assert r['status']=='complete';assert r['payload_sha256']==digest(r['payload'])
    assert r['payload']['model']==model and r['provider']=='DeepInfra'
    assert r['returned_model']==model
    assert not r.get('reasoning_text','').strip()
    assert r['payload']['max_tokens']==384 and r['payload']['temperature']==0
    assert r['payload']['messages'][-1]['content'].endswith('/no_think')
    assert r['elapsed_ms']>=r['first_answer_ms']>=0;checks['replies']+=1
 if failures:
  print(json.dumps({'complete':False,'counts':dict(checks),'missing':failures}));sys.exit(1)
 assert checks=={'routes':32,'llm_routes':32,'judge_batches':64,'second_judge_batches':64,'replies':320}
 rr=list(csv.DictReader((H/'case-results.csv').open()));summary=read(H/'results.json')
 assert len(rr)==32*2*10
 raw=list(csv.DictReader((H/'replies-and-ratings.csv').open()));assert len(raw)==320
 assert all(r['secondary_pass'] in ['True','False'] for r in raw)
 math_ids=set(read(H/'domain-screen.json')['math_indices'])
 for model,scopes in summary['secondary_judge_analysis'].items():
  for scope,detail in scopes.items():
   for cond,stats in detail['conditions'].items():
    rows=[r for r in rr if r['model']==model and r['condition']==cond and (scope=='all' or int(r['index']) in math_ids)]
    scores=[next(x['secondary_pass']=='True' for x in raw if x['index']==r['index'] and x['model']==model and x['arm']==r['selected_arm']) for r in rows]
    assert len(scores)==stats['n'] and sum(scores)==stats['strict_pass']
 for model,conditions in summary['conditions'].items():
  for cond,stats in conditions.items():
   rows=[r for r in rr if r['model']==model and r['condition']==cond]
   assert len(rows)==stats['n']==32
   assert sum(r['strict_pass']=='True' for r in rows)==stats['strict_pass']
 for r in rr:
  matching=[x for x in rr if x['index']==r['index'] and x['model']==r['model'] and x['selected_arm']==r['selected_arm']]
  assert len({x['strict_pass'] for x in matching})==1
  if r['condition']=='teacher_detailed':assert r['selected_arm']=='force_'+r['reference']
  if r['condition']=='jev_detailed':assert r['selected_arm']=='force_'+r['route']
  if r['condition']=='llm_detailed':assert r['selected_arm']=='force_'+r['route']
 assert summary['spending_including_setup_and_failed_reservations_usd']<=5
 manifest=H/'archive-manifest.json'
 if manifest.exists():
  for name,expected in read(manifest)['files'].items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==expected,name
 print(json.dumps({'complete':True,'checks':dict(checks),'condition_rows':len(rr),'reported_counts_recomputed':True},indent=2))
if __name__=='__main__':main()
