"""Audit inputs, coverage, blinding, saved ratings and derived counts. No network calls."""
import pathlib,json,csv,importlib.util,collections,hashlib
H=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('finalrun',H/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);cfg,M=r.verified();p=r.p
allgens={};valid=0;truncated=0
for i in range(520):
 allgens[i]={}
 for a in r.ARMS:
  g=p.load(H/'traces'/f'gen-{i}-{a}.json');assert g['status']=='complete';assert g['payload']==r.payload(M[i],a);assert g['payload_sha256']==p.sha(p.enc(g['payload']));assert g['provider']=='DeepInfra';allgens[i][a]=g;truncated+=g['finish_reason']=='length';valid+=bool(g['text'].strip()) and g['finish_reason'] in ['stop','end_turn'] and not g.get('reasoning_text','').strip()
for kind,ids,model,offset in [('judge',range(520),'google/gemini-2.5-flash',0),('audit',cfg['audit_indices'],'anthropic/claude-sonnet-4.6',10000)]:
 for i in ids:
  replies={a:g['text'] for a,g in allgens[i].items()};request,mapping=p.judge_payload(M[i],replies,model,r.SEED+i+offset);request['max_tokens']=1800
  g=p.load(H/'traces'/f'{kind}-{i}.json');rat=p.load(H/'ratings'/f'{kind}-{i}.json');assert g['status']=='complete';assert g['payload']==request;assert g['payload_sha256']==p.sha(p.enc(request));assert rat['mapping']==mapping;parse_text=g['text'];repair=p.load(H/'parse-repair.json') if kind=='audit' and i==467 else None
  if repair:
   assert repair['raw_trace_sha256']==p.sha(p.enc(g));assert parse_text.count(repair['old_fragment'])==1;parse_text=parse_text.replace(repair['old_fragment'],repair['new_fragment'])
  assert rat['ratings']==p.parse_ratings(parse_text,mapping);assert rat['trace_sha256']==p.sha(p.enc(g))
results=p.load(H/'results.json');assert results['status']=='complete';assert not results['missing'];assert results['new_experiment_cost_usd']<=8
for name,n in [('replies-and-ratings.csv',1560),('case-results.csv',3640),('audit-replies-and-ratings.csv',96),('audit-case-results.csv',224)]:
 rr=list(csv.DictReader(open(H/name)));assert len(rr)==n,(name,len(rr),n)
 if name.endswith('replies-and-ratings.csv'):
  for x in rr:
   gold=x['reference'];a=x['observed_'+gold]=='True';loose=x['valid_generation']=='True' and a and x['overhelp']=='False';strict=loose and x['math_error']=='False' and x['context_fit']=='2';assert strict==(x['strict_pass']=='True');assert loose==(x['direction_no_overhelp']=='True')
 else:
  for scope,key in [('all_520',None),('strict_math_346',set(p.load(H/'strict-math-sensitivity.json')['indices']))]:
   stats=results['audit' if name.startswith('audit-') else 'scopes'][scope]['conditions']
   for condition,x in stats.items():
    sub=[v for v in rr if v['condition']==condition and (key is None or int(v['index']) in key)];assert len(sub)==x['n'];assert sum(v['strict_pass']=='True' for v in sub)==x['pass']
summary={'status':'passed','generation_requests_verified':1560,'primary_judge_requests_verified':520,'audit_requests_verified':32,'strict_math_source_ids_verified':346,'all_inputs_rebuilt_identically':True,'all_scores_recomputed':True,'valid_generations':valid,'truncated_generations':truncated,'new_experiment_cost_usd':results['new_experiment_cost_usd'],'source_labels_changed':False,'human_validation_claimed':False,'unseen_test_set_claimed':False,'publisher_score_claimed':False}
p.save(H/'verification.json',summary);print(json.dumps(summary,indent=2))
