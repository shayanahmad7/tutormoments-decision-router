"""Offline status, cost and original-rule reporting; no API calls."""
from pathlib import Path
import csv,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
spec=importlib.util.spec_from_file_location('replay',H/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
cfg=r.prepare();rows=r.base.rows();traces=[json.loads(f.read_text()) for f in (H/'traces').glob('*.json')];states=[json.loads(f.read_text()) for f in (H/'cases').glob('*.json')];scored=[x for x in states if x['status']=='scored'];complete=[x for x in traces if x['status']=='complete'];failed=[x for x in traces if x['status']!='complete']
for x in traces:assert r.sha(r.enc(x['payload']))==x['payload_sha256']
for x in complete:
 if x['kind']=='tutor':
  assert x['payload']['model']=='gpt-6-astra' and x['payload']['reasoning_effort']=='high' and x['payload']['max_completion_tokens']==128000
 else:assert x['payload']['model']=='anthropic/claude-opus-4.6'
site=json.loads((H/'website-leaderboard.json').read_text());a=next(x for x in site['models'] if x['id']=='gpt-6-astra')['eval_aware']
result={'status':'complete' if len(scored)==20 else 'incomplete','planned_cases':20,'scored_cases':len(scored),'completed_api_calls':len(complete),'failed_api_calls':len(failed),'completed_call_token_cost_usd':sum(x['cost_usd'] for x in complete),'failed_call_reservations_not_observed_charges_usd':sum(x['cost_usd'] for x in failed),'publisher_full520':{**a,'overall_mean_from_rounded_rates':(a['scaffolding']+a['rigor'])/2},'metrics':r.p.publisher_metrics([(rows[x['index']],x['annotation']) for x in scored]) if scored else None,'errors':[x.get('error') for x in failed],'limitations':['Same 20 moments as earlier classification pilot, not a new held-out test.','Claude via OpenRouter pinned Anthropic rather than direct Anthropic.','Synchronous non-streaming calls; judge not batch. No comparable timing claim.','Undated model aliases can change since original leaderboard run.']}
(H/'results.json').write_text(json.dumps(result,indent=2))
if scored:
 fields=['index','moment_id','dimension','action_label','overscaffold','pass_publisher_rule','previous_binary_prediction','previous_binary_correct']
 with (H/'Replay results.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for s in scored:
   old=json.loads((ROOT/'experiments/astra-decision-pilot/traces'/f"astra-{s['index']:03d}.json").read_text())
   w.writerow({**{k:s[k] for k in ['index','moment_id','dimension','pass_publisher_rule']},'action_label':s['annotation']['action_label'],'overscaffold':bool(s['annotation']['overscaffold_decomposed']),'previous_binary_prediction':old['prediction'],'previous_binary_correct':old['prediction']==s['dimension']})
print(json.dumps(result,indent=2))
