"""Recompute frozen first-reply results without API calls; partial coverage is explicit."""
import pathlib,json,csv,collections,statistics,math,random,importlib.util
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('finalrun',HERE/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);p=r.p
CONDITIONS=['self_detailed','jev_directed','decisions_directed','always_scaffolding','always_rigor','teacher_directed','opposite_teacher']
LABELS={'self_detailed':'Detailed self-choice','jev_directed':'Jev-directed policy','decisions_directed':'Decisions-directed policy','always_scaffolding':'Always scaffold','always_rigor':'Always rigor','teacher_directed':'Teacher-directed diagnostic','opposite_teacher':'Opposite-teacher diagnostic'}
def q(v,x):
 if not v:return None
 a=sorted(v);pos=(len(a)-1)*x;lo=math.floor(pos);hi=math.ceil(pos);return a[lo]+(a[hi]-a[lo])*(pos-lo)
def summary(v):return {'n':len(v),'mean':statistics.mean(v) if v else None,'median':q(v,.5),'p95':q(v,.95)}
def arm(c,condition):
 if condition=='self_detailed':return condition
 if condition=='jev_directed':d=c['jev']
 elif condition=='decisions_directed':d=c['decisions']
 elif condition=='teacher_directed':d=c['reference']
 elif condition=='opposite_teacher':d='rigor' if c['reference']=='scaffolding' else 'scaffolding'
 else:d=condition.removeprefix('always_')
 return 'force_'+d

def paired(rows,a,b):
 bycase=collections.defaultdict(dict)
 for x in rows:bycase[x['index']][x['condition']]=x
 vals=[(int(v[a]['strict_pass'])-int(v[b]['strict_pass']),v[a]['student_id']) for v in bycase.values() if a in v and b in v]
 if not vals:return None
 groups=collections.defaultdict(list)
 for d,student in vals:groups[student].append(d)
 totals=[(sum(v),len(v)) for v in groups.values()];rng=random.Random(r.SEED);boots=[]
 for _ in range(10000):
  sample=[rng.choice(totals) for _ in totals];boots.append(sum(s for s,n in sample)/sum(n for s,n in sample))
 return {'n_moments':len(vals),'n_student_clusters':len(groups),'difference_pp':100*sum(d for d,_ in vals)/len(vals),'student_cluster_bootstrap_ci95_pp':[100*q(boots,.025),100*q(boots,.975)],'wins':sum(d>0 for d,_ in vals),'losses':sum(d<0 for d,_ in vals),'ties':sum(d==0 for d,_ in vals),'bootstrap_resamples':10000}

def main():
 cfg,M=r.verified();pred=[];raw=[];missing=[];auditraw=[];auditpred=[]
 spec=importlib.util.spec_from_file_location('jevsearch',r.ROOT/'experiments/jev-all-520-search/run.py');js=importlib.util.module_from_spec(spec);spec.loader.exec_module(js)
 cached={i:js.entry('C',i) for i in range(520)}
 for c in cfg['cases']:
  i=c['index'];gens={}
  for a in r.ARMS:
   f=HERE/'traces'/f'gen-{i}-{a}.json'
   if not f.exists() or p.load(f).get('status')!='complete':missing.append({'index':i,'kind':'generation','arm':a});continue
   gens[a]=p.load(f)
  for kind,rawout,predout in [('judge',raw,pred),('audit',auditraw,auditpred)]:
   f=HERE/'ratings'/f'{kind}-{i}.json'
   if not f.exists():
    if kind=='judge' or i in cfg['audit_indices']:missing.append({'index':i,'kind':kind})
    continue
   j=p.load(f);ratings={j['mapping'][x['id']]:x for x in j['ratings']};scores={}
   for a in r.ARMS:
    if a not in gens or a not in ratings:continue
    g=gens[a];z=ratings[a];valid=bool(g['text'].strip()) and g.get('finish_reason') in ['stop','end_turn'] and not g.get('reasoning_text','').strip()
    loose=bool(valid and z[c['reference']] and not z['overhelp']);strict=bool(loose and not z['math_error'] and z['context_fit']==2)
    scores[a]={'strict_pass':strict,'direction_no_overhelp':loose,'valid_generation':valid,'observed_scaffolding':z['scaffolding'],'observed_rigor':z['rigor'],'overhelp':z['overhelp'],'math_error':z['math_error'],'context_fit':z['context_fit'],'uncertain':z['uncertain']}
    rawout.append({'index':i,'moment_number':i+1,'student_id':c['student_id'],'reference':c['reference'],'arm':a,'judge':j['model'],'reply':g['text'],**scores[a],'evidence':z['evidence'],'evidence_exact':bool(z['evidence'].strip()) and z['evidence'].strip() in g['text'],'reason':z['reason'],'finish_reason':g.get('finish_reason'),'provider':g.get('provider')})
   for condition in CONDITIONS:
    a=arm(c,condition)
    if a not in scores:continue
    g=gens[a];route_ms=0;route_cost=0
    if condition=='jev_directed':route_ms=cached[i]['elapsed_ms'];route_cost=cached[i]['cost_usd'];assert js.m.answer(cached[i])['choice']==c['jev']
    elif condition=='decisions_directed':route_ms=c['archived_decisions_seconds']*1000;route_cost=c['archived_decisions_cost_usd']
    predout.append({'index':i,'moment_number':i+1,'student_id':c['student_id'],'reference':c['reference'],'domain':c['domain'],'known_nonmath':c['known_nonmath'],'condition':condition,'selected_arm':a,**scores[a],'generator_first_answer_ms':g.get('first_answer_ms'),'historical_router_ms':route_ms,'estimated_serial_first_answer_ms':g.get('first_answer_ms',0)+route_ms if g.get('first_answer_ms') is not None else None,'generator_cost_usd':g['cost_usd'],'historical_router_cost_usd':route_cost,'estimated_deployed_reply_cost_usd':g['cost_usd']+route_cost,'reply_words':len(g['text'].split())})
 contexts=collections.defaultdict(list)
 for i,m in enumerate(M):contexts[json.dumps(m['context'],sort_keys=True,ensure_ascii=False)].append(i)
 conflict={i for g in contexts.values() if len({M[j]['dimension'] for j in g})>1 for i in g}
 scopes={'strict_math_346':set(p.load(HERE/'strict-math-sensitivity.json')['indices']),'all_520':set(range(520)),'known_nonmath_excluded':{c['index'] for c in cfg['cases'] if not c['known_nonmath']},'prior_math_positive':{c['index'] for c in cfg['cases'] if c['domain'].startswith('mathematics')},'nonconflicting_contexts':set(range(520))-conflict}
 result={'status':'complete' if not missing else 'incomplete','model':r.MODEL,'planned_cases':520,'n_student_clusters':cfg['n_students'],'unique_generated_replies':len(list((HERE/'traces').glob('gen-*.json'))),'primary_judge':'google/gemini-2.5-flash','audit_judge':'anthropic/claude-sonnet-4.6','scopes':{},'audit':{},'missing':missing,'measure':'First-reply automated rubric; not publisher multi-turn score','routing':'Archived JevC and OpenAI Decisions predictions choose between generated policy replies; not fresh end-to-end pipeline calls'}
 for kind,rows,dest in [('primary',pred,result['scopes']),('audit',auditpred,result['audit'])]:
  for name,ids in scopes.items():
   rr=[x for x in rows if x['index'] in ids];stats={}
   for cond in CONDITIONS:
    z=[x for x in rr if x['condition']==cond];n=len(z)
    if not n:continue
    stats[cond]={'n':n,'pass':sum(x['strict_pass'] for x in z),'rate':sum(x['strict_pass'] for x in z)/n,'direction_no_overhelp':sum(x['direction_no_overhelp'] for x in z),'overhelp':sum(x['overhelp'] for x in z),'math_error':sum(x['math_error'] for x in z),'uncertain':sum(x['uncertain'] for x in z),'both_observed':sum(x['observed_scaffolding'] and x['observed_rigor'] for x in z),'by_reference':{g:{'n':sum(x['reference']==g for x in z),'pass':sum(x['reference']==g and x['strict_pass'] for x in z)} for g in ['scaffolding','rigor']},'generator_first_answer_ms':summary([x['generator_first_answer_ms'] for x in z if x['generator_first_answer_ms'] is not None]),'estimated_serial_first_answer_ms':summary([x['estimated_serial_first_answer_ms'] for x in z if x['estimated_serial_first_answer_ms'] is not None]),'cost_per_1000_deployed_replies':1000*statistics.mean(x['estimated_deployed_reply_cost_usd'] for x in z)}
   dest[name]={'planned_n':len(ids),'conditions':stats,'paired':{a+'_minus_'+b:paired(rr,a,b) for a,b in [('jev_directed','self_detailed'),('decisions_directed','self_detailed'),('jev_directed','always_rigor'),('jev_directed','always_scaffolding')]}}
 # Exploratory mechanism summaries specified before any new judge calls.
 result['branch_headroom']={};result['route_error_propagation']={}
 for name,ids in scopes.items():
  rr=[x for x in pred if x['index'] in ids];case=collections.defaultdict(dict)
  for x in rr:case[x['index']][x['condition']]=x
  counts=collections.Counter();prop={route:{str(match):{'n':0,'selected_pass':0,'self_choice_pass':0,'teacher_policy_pass':0} for match in [True,False]} for route in ['jev','decisions']}
  for i,cc in case.items():
   if not all(c in cc for c in CONDITIONS):continue
   sc=cc['always_scaffolding']['strict_pass'];ri=cc['always_rigor']['strict_pass']
   counts['both_pass' if sc and ri else 'scaffold_only_pass' if sc else 'rigor_only_pass' if ri else 'neither_pass']+=1
   c=cfg['cases'][i]
   for route in ['jev','decisions']:
    z=prop[route][str(c[route]==c['reference'])];z['n']+=1;z['selected_pass']+=int(cc[route+'_directed']['strict_pass']);z['self_choice_pass']+=int(cc['self_detailed']['strict_pass']);z['teacher_policy_pass']+=int(cc['teacher_directed']['strict_pass'])
  result['branch_headroom'][name]={'n':sum(counts.values()),**dict(counts),'note':'Paired potential replies; best-of-two is an after-outcome diagnostic, not a deployable policy.'};result['route_error_propagation'][name]=prop
 primarymap={(x['index'],x['arm']):x for x in raw};pairedjudges=[(primarymap[(x['index'],x['arm'])],x) for x in auditraw if (x['index'],x['arm']) in primarymap]
 result['judge_agreement']={'n_replies':len(pairedjudges),'same_pass':sum(a['strict_pass']==b['strict_pass'] for a,b in pairedjudges),'primary_pass':sum(a['strict_pass'] for a,b in pairedjudges),'audit_pass':sum(b['strict_pass'] for a,b in pairedjudges)}
 result['evidence_quote_mismatches']={'primary':sum(not x['evidence_exact'] for x in raw),'audit':sum(not x['evidence_exact'] for x in auditraw)}
 traces=[p.load(f) for f in (HERE/'traces').glob('*.json')];failures=[p.load(f) for f in (HERE/'failed-attempts').glob('*.json')];result['failed_attempt_reservations_usd']=sum(x.get('cost_usd',x.get('reserve_usd',0)) for x in failures);result['failed_or_interrupted_attempts']=len(failures);result['new_experiment_cost_usd']=sum(x.get('cost_usd',x.get('reserve_usd',0)) for x in traces)+result['failed_attempt_reservations_usd'];result['calls_by_status']=dict(collections.Counter(x['status'] for x in traces));result['truncated_generations']=sum(x.get('finish_reason')=='length' for x in traces if x['tag'].startswith('gen-'));result['cost_by_phase_usd']={stage:sum(x.get('cost_usd',x.get('reserve_usd',0)) for x in traces if x['tag'].startswith(stage+'-')) for stage in ['gen','judge','audit']};result['cost_by_phase_usd']['failed_or_interrupted_reservations']=result['failed_attempt_reservations_usd'];result['max_observed_generator_prompt_tokens']=max((x.get('usage',{}).get('prompt_tokens',0) for x in traces if x['tag'].startswith('gen-')),default=0);result['unexpected_reasoning_generations']=sum(bool(x.get('reasoning_text','').strip()) for x in traces if x['tag'].startswith('gen-'));result['routing_label_matches']={'jev':376,'decisions':386,'n':520};result['historical_jev_latency_ms']=summary([x['elapsed_ms'] for x in cached.values()])
 for name,rr in [('case-results.csv',pred),('replies-and-ratings.csv',raw),('audit-case-results.csv',auditpred),('audit-replies-and-ratings.csv',auditraw)]:
  if rr:
   with (HERE/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 p.save(HERE/'results.json',result)
 report=['# Full-preview first-reply routing results',f"Status: {result['status']}. New experiment cost: ${result['new_experiment_cost_usd']:.4f}.",'All outcomes below are automated first-reply ratings. They are not the published TutorMoments multi-turn score and do not measure student learning.']
 for scope in ['all_520','strict_math_346','known_nonmath_excluded','prior_math_positive']:
  report+=['',f'## {scope}','| Condition | Passing replies | Rate | Scaffolding | Rigor |','|---|---:|---:|---:|---:|']
  for cond,z in result['scopes'][scope]['conditions'].items():report.append(f"| {LABELS[cond]} | {z['pass']}/{z['n']} | {100*z['rate']:.1f}% | {z['by_reference']['scaffolding']['pass']}/{z['by_reference']['scaffolding']['n']} | {z['by_reference']['rigor']['pass']}/{z['by_reference']['rigor']['n']} |")
  for name,z in result['scopes'][scope]['paired'].items():
   if z:report.append(f"{name}: {z['difference_pp']:+.1f} pp; student-cluster95% interval {z['student_cluster_bootstrap_ci95_pp'][0]:+.1f} to {z['student_cluster_bootstrap_ci95_pp'][1]:+.1f}; wins {z['wins']}, losses {z['losses']}.")
 report+=['','## Evaluation audit',json.dumps(result['judge_agreement']),json.dumps(result['evidence_quote_mismatches']),'','## Limits','Routes were archived, and policy selection was applied to paired generated alternatives. Tutor prompts and routing prompts were developed on this same source preview. These findings are exploratory internal evaluation. The known-nonmath-excluded subset is not a fully adjudicated math-only corpus. Generation calls ran concurrently; serial latency sums add historical route timing and cannot establish deployment speed. All outcomes and fixed-policy controls are retained.']
 (HERE/'RESULTS.md').write_text('\n'.join(report)+'\n');print(json.dumps({'status':result['status'],'cost':result['new_experiment_cost_usd'],'primary':result['scopes']['all_520'],'audit_agreement':result['judge_agreement']},indent=2))
if __name__=='__main__':main()
