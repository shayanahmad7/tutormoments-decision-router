"""Offline audit and report for the four-case capped original-prompt replay."""
from pathlib import Path
import collections,csv,importlib.util,json,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
spec=importlib.util.spec_from_file_location('small_replay',H/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
cfg=r.prepare();rows=r.base.rows();traces=[json.loads(f.read_text()) for f in (H/'traces').glob('*.json')];states=[json.loads(f.read_text()) for f in (H/'cases').glob('*.json')];scored=sorted((s for s in states if s['status']=='scored'),key=lambda s:cfg['indices'].index(s['index']))
completed=[t for t in traces if t['status']=='complete'];failures=[t for t in traces if t['status']!='complete'];reused=json.loads((ROOT/'experiments/astra-publisher-replay/traces/309-tutor-0.json').read_text())
assert (H/'traces/309-tutor-0.json').read_bytes()==(ROOT/'experiments/astra-publisher-replay/traces/309-tutor-0.json').read_bytes()
for t in traces:assert r.sha(r.enc(t['payload']))==t['payload_sha256']
for t in completed:
 b=t['payload'];d=t['response']
 if t['kind']=='tutor':
  assert t['endpoint']=='https://api.openai.com/v1/chat/completions'
  assert b['model']=='gpt-6-astra' and b['reasoning_effort']=='high'
  assert b['max_completion_tokens']==(128000 if t['tag']=='309-tutor-0' else 8192)
  assert d['choices'][0]['finish_reason']=='stop'
 else:
  assert b['model']=='anthropic/claude-opus-4.6' and d['provider']=='Anthropic'
  assert b['max_tokens']==8192 and d['stop_reason'] in ['end_turn','stop_sequence']
  assert b['thinking']['type']==('disabled' if t['kind']=='student' else 'adaptive')
# Reconstruct actual requests from every saved conversation prefix.
for s in scored:
 m=rows[s['index']];g=[]
 for step in range(s['next_step']):
  tag=f"{s['index']:03d}-{'tutor' if step%2==0 else 'student'}-{step}"
  t=next(x for x in completed if x['tag']==tag)
  if step%2==0:
   assert t['payload']==r.tutor_payload(m,g)
   text,end,change=r.p.parse_tutor_output(t['text']);pieces=r.p.split_messages(text)
   if not pieces and not(end or change):pieces=['...']
   g=r.p.append_generated_turns(m,g,'TUTOR',pieces)
  else:
   head,tail=r.parts(m,'STUDENT',g);assert t['payload']==r.claude_payload(tail,head=head)
   g=r.p.append_generated_turns(m,g,'STUDENT',r.p.split_messages(t['text']) or ['...'])
 assert g==s['generated_turns']
 ann=s['annotation'];right=ann['action_label'] in [m['dimension'],'both'] and not ann['overscaffold_decomposed'];assert bool(s['pass_publisher_rule'])==right
 calls={t['tag']:t for t in completed}
 assert calls[f"{s['index']:03d}-judge-annotate"]['payload']==r.claude_payload(r.p.scorer_annotate_prompt(m,g),True)
 for kind in ['action','overscaffold']:
  prompt=r.p.scorer_decompose_prompt(ann,kind)
  if prompt:assert calls[f"{s['index']:03d}-judge-{kind}"]['payload']==r.claude_payload(prompt,True)
 prompt=r.p.scorer_structure_prompt(ann['action_decomposed'])
 if prompt:assert calls[f"{s['index']:03d}-judge-structure"]['payload']==r.claude_payload(prompt,True)
metrics=r.p.publisher_metrics([(rows[s['index']],s['annotation']) for s in scored]) if scored else None
cost=sum(t['cost_usd'] for t in completed);by_kind={k:sum(t['cost_usd'] for t in completed if t['kind']==k) for k in ['tutor','student','judge']}
result={'status':'complete' if len(scored)==4 and not failures else 'incomplete','planned_cases':4,'scored_cases':len(scored),'successes':sum(bool(s['pass_publisher_rule']) for s in scored),'metrics':metrics,'total_token_cost_usd':cost,'new_token_cost_usd':cost-reused['cost_usd'],'reused_token_cost_usd':reused['cost_usd'],'cost_by_role':by_kind,'complete_calls':len(completed),'new_complete_calls':len(completed)-1,'failed_calls':len(failures),'action_counts':dict(collections.Counter(s['annotation']['action_label'] for s in scored)),'incomplete_or_truncated_completed_calls':0,'request_reconstruction_checks_passed':True,'caveats':['Four chosen cases are an implementation check, not a benchmark accuracy estimate.','New calls capped at 8192 output tokens instead of 128000; reused first reply had original 128000 ceiling.','Claude through OpenRouter pinned Anthropic; scoring synchronous/nonbatch; undated aliases may drift.']}
result['maximum_output_tokens_by_role']={k:max([t['usage'].get('completion_tokens',t['usage'].get('output_tokens',0)) for t in completed if t['kind']==k],default=0) for k in ['tutor','student','judge']}
result['openrouter_billed_cost_verified']=all(abs(t['usage']['cost']-t['cost_usd'])<1e-9 for t in completed if t['kind']!='tutor')
(H/'results.json').write_text(json.dumps(result,indent=2))
if scored:
 fields=['moment_number','source_index','dimension','action_label','overscaffolding','publisher_success','earlier_binary_prediction','earlier_binary_correct']
 with (H/'Four replay results.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for s in scored:
   old=json.loads((ROOT/'experiments/astra-decision-pilot/traces'/f"astra-{s['index']:03d}.json").read_text())
   w.writerow({'moment_number':s['index']+1,'source_index':s['index'],'dimension':s['dimension'],'action_label':s['annotation']['action_label'],'overscaffolding':bool(s['annotation']['overscaffold_decomposed']),'publisher_success':bool(s['pass_publisher_rule']),'earlier_binary_prediction':old['prediction'],'earlier_binary_correct':old['prediction']==s['dimension']})
 lines=['# Four original-prompt tutoring replays','','Generated tutor/student dialogue and automated scorer judgments. These are not new human student observations.','']
 for s in scored:
  lines += [f"## Moment {s['index']+1}: {s['dimension']}",'','### Last six original turns','']
  for t in rows[s['index']]['context'][-6:]:lines += [f"**{t['role'].title()}:** {t['text']}",'']
  lines += ['### Generated exchange','']
  for t in s['generated_turns']:lines += [f"**{t['role'].title()}:** {t['text']}",'']
  a=s['annotation'];lines += ['### Automated scoring','',f"Action: **{a['action_label']}**. Over-scaffolding: **{bool(a['overscaffold_decomposed'])}**. Publisher-rule success: **{bool(s['pass_publisher_rule'])}**.",'',a['action'],'',a['result'],'',f"Over-scaffolding spans: {json.dumps(a['overscaffold_decomposed'],ensure_ascii=False)}",'']
 (H/'Readable replays.md').write_text('\n'.join(lines))
print(json.dumps(result,indent=2))
