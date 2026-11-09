"""Recompute every result from saved responses. No API requests."""
import collections, csv, importlib.util, json, math, random, statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pilot',HERE/'run.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
CONDITIONS=['original','self_detailed','jev_label','jev_detailed','teacher_detailed','opposite_teacher','always_scaffolding','always_rigor','confidence_fallback']

def selected_arm(condition,route,gold,prob):
 if condition in p.ARMS:return condition
 if condition=='jev_detailed':return 'force_'+route
 if condition=='teacher_detailed':return 'force_'+gold
 if condition=='opposite_teacher':return 'force_'+('rigor' if gold=='scaffolding' else 'scaffolding')
 if condition.startswith('always_'):return 'force_'+condition[7:]
 if condition=='confidence_fallback':return 'force_'+route if prob>=.8 else 'self_detailed'
 raise ValueError(condition)

def q(values,f):
 if not values:return None
 a=sorted(values);pos=(len(a)-1)*f;lo=math.floor(pos);hi=math.ceil(pos)
 return a[lo]*(hi-pos)+a[hi]*(pos-lo) if hi!=lo else a[lo]
def dist(v):return {'n':len(v),'mean':statistics.mean(v) if v else None,'p50':q(v,.5),'p95':q(v,.95)}
def paired(a,b,labels,seed=20261109):
 assert len(a)==len(b)==len(labels)
 d=[x-y for x,y in zip(a,b)];win=sum(x>0 for x in d);loss=sum(x<0 for x in d);discord=win+loss
 pv=min(1.,2*sum(math.comb(discord,i) for i in range(min(win,loss)+1))/(2**discord)) if discord else 1.
 strata=[[i for i,l in enumerate(labels) if l==g] for g in sorted(set(labels))]
 rng=random.Random(seed);boots=[]
 for _ in range(10000):
  ids=[rng.choice(group) for group in strata for _ in group];boots.append(statistics.mean(d[i] for i in ids))
 return {'n':len(d),'difference_pp':100*statistics.mean(d),'ci95_pp':[100*q(boots,.025),100*q(boots,.975)],'wins':win,'losses':loss,'ties':len(d)-discord,'mcnemar_exact_p':pv}

def main():
 cfg=p.load(HERE/'frozen.json');source=p.source();out=[];raw=[];judge_comparison=[];bad_evidence=[]
 for c in cfg['cases']:
  idx=c['index'];rt=p.load(HERE/'traces'/f'route-{idx}.json');ans=rt['response']['answers']['next_move'];route=ans['choice'];prob=max(ans['probabilities'].values())
  for model in cfg['models']:
   short=model.split('/')[-1];jp=HERE/'ratings'/f'judge1-{idx}-{short}.json'
   if not jp.exists():continue
   j=p.load(jp);rr={j['mapping'][r['id']]:r for r in j['ratings']}
   gen={a:p.load(HERE/'traces'/f'gen-{idx}-{short}-{a}.json') for a in p.ARMS}
   scores={}
   for arm,g in gen.items():
    rating=rr[arm];valid=bool(g['text'].strip()) and g['finish_reason'] in ['stop','end_turn'] and not g.get('reasoning_text','').strip()
    aligned=rating[c['reference']]
    loose=bool(valid and aligned and not rating['overhelp'])
    strict=bool(loose and not rating['math_error'] and rating['context_fit']==2)
    evidence_ok=rating['evidence'].strip() in g['text'] if rating['evidence'].strip() else False
    if not evidence_ok:bad_evidence.append({'index':idx,'model':model,'arm':arm})
    scores[arm]=(strict,loose)
    raw.append({'index':idx,'student_id':c['student_id'],'reference':c['reference'],'model':model,'arm':arm,
                'response':g['text'],**{k:v for k,v in rating.items() if k!='id'},'evidence_exact':evidence_ok,'valid_generation':valid,
                'strict_pass':strict,'direction_no_overhelp':loose,'provider':g['provider'],'finish_reason':g['finish_reason']})
   for cond in CONDITIONS:
    arm=selected_arm(cond,route,c['reference'],prob);g=gen[arm];r=rr[arm]
    uses_router=cond in ['jev_label','jev_detailed','confidence_fallback']
    route_cost=rt['cost_usd'] if uses_router else 0;route_time=rt['elapsed_ms'] if uses_router else 0
    out.append({'index':idx,'student_id':c['student_id'],'reference':c['reference'],'model':model,'condition':cond,'selected_arm':arm,
                'route':route,'route_matches_teacher':route==c['reference'],'route_probability':prob,
                'strict_pass':scores[arm][0],'direction_no_overhelp':scores[arm][1],
                'overhelp':r['overhelp'],'math_error':r['math_error'],'uncertain':r['uncertain'],'context_fit':r['context_fit'],
                'first_answer_ms_serial_estimate':(g['first_answer_ms']+route_time) if g['first_answer_ms'] is not None else None,
                'full_reply_ms_serial_estimate':g['elapsed_ms']+route_time,'deployment_cost_usd':g['cost_usd']+route_cost})
   second=HERE/'ratings'/f'judge2-{idx}-{short}.json'
   if second.exists():
    j2=p.load(second)
    for rating in j2['ratings']:
     arm=j2['mapping'][rating['id']];valid=bool(gen[arm]['text'].strip()) and gen[arm]['finish_reason'] in ['stop','end_turn'] and not gen[arm].get('reasoning_text','').strip()
     strict2=bool(valid and rating[c['reference']] and not rating['overhelp'] and not rating['math_error'] and rating['context_fit']==2)
     judge_comparison.append({'index':idx,'model':model,'arm':arm,'primary':scores[arm][0],'secondary':strict2,'secondary_rating':rating})
 results={'planned_n_per_model':32,'conditions':{},'primary_comparisons':{},'cross_judge':{},'routing':{},'evidence_quote_issues':bad_evidence}
 for model in cfg['models']:
  rows=[r for r in out if r['model']==model];results['conditions'][model]={}
  for cond in CONDITIONS:
   rr=[r for r in rows if r['condition']==cond]
   if not rr:continue
   results['conditions'][model][cond]={'n':len(rr),'strict_pass':sum(r['strict_pass'] for r in rr),
      'direction_no_overhelp':sum(r['direction_no_overhelp'] for r in rr),'overhelp':sum(r['overhelp'] for r in rr),
      'math_error':sum(r['math_error'] for r in rr),'uncertain':sum(r['uncertain'] for r in rr),
      'by_reference':{g:{'n':sum(r['reference']==g for r in rr),'strict_pass':sum(r['reference']==g and r['strict_pass'] for r in rr)} for g in ['scaffolding','rigor']},
      'first_answer_ms_serial_estimate':dist([r['first_answer_ms_serial_estimate'] for r in rr if r['first_answer_ms_serial_estimate'] is not None]),
      'cost_per_1000_replies_usd':statistics.mean(r['deployment_cost_usd'] for r in rr)*1000}
  a=[r for r in rows if r['condition']=='jev_detailed'];b=[r for r in rows if r['condition']=='self_detailed']
  if a:results['primary_comparisons'][model]=paired([int(r['strict_pass']) for r in a],[int(r['strict_pass']) for r in b],[r['reference'] for r in a])
  counter={}
  for route_ok in [True,False]:
   ids={r['index'] for r in a if r['route_matches_teacher']==route_ok}
   counter[str(route_ok)]={cond:{'n':sum(r['index'] in ids and r['condition']==cond for r in rows),'pass':sum(r['index'] in ids and r['condition']==cond and r['strict_pass'] for r in rows)} for cond in ['self_detailed','jev_detailed','teacher_detailed','opposite_teacher']}
  results.setdefault('route_error_decomposition',{})[model]=counter
 prim=results['primary_comparisons'];running=0
 for rank,(model,r) in enumerate(sorted(prim.items(),key=lambda kv:kv[1]['mcnemar_exact_p'])):
  running=max(running,min(1.,r['mcnemar_exact_p']*(len(prim)-rank)));r['holm_p']=running
 if len(prim)==2:
  a=[];b=[];labels=[]
  for c in cfg['cases']:
   diffs=[]
   for model in cfg['models']:
    rr={r['condition']:r for r in out if r['index']==c['index'] and r['model']==model}
    if not rr:break
    diffs.append(int(rr['jev_detailed']['strict_pass'])-int(rr['self_detailed']['strict_pass']))
   if len(diffs)==2:a.append(diffs[0]);b.append(diffs[1]);labels.append(c['reference'])
  if a:
   v=paired(a,b,labels);v.pop('mcnemar_exact_p');results['size_interaction_14b_minus_32b']=v
 routes=[p.load(HERE/'traces'/f'route-{c["index"]}.json') for c in cfg['cases']]
 results['routing']={'n':len(routes),'correct':sum(r['response']['answers']['next_move']['choice']==c['reference'] for r,c in zip(routes,cfg['cases'])),
                     'latency_ms':dist([r['elapsed_ms'] for r in routes]),'by_reference':{g:{'n':16,'correct':sum(c['reference']==g and r['response']['answers']['next_move']['choice']==g for r,c in zip(routes,cfg['cases']))} for g in ['scaffolding','rigor']}}
 for model in cfg['models']:
  cc=[r for r in judge_comparison if r['model']==model]
  results['cross_judge'][model]={'n_replies':len(cc),'n_cases':len({r['index'] for r in cc}),'agree':sum(r['primary']==r['secondary'] for r in cc),'primary_pass':sum(r['primary'] for r in cc),'secondary_pass':sum(r['secondary'] for r in cc)}
 traces=[p.load(f) for f in (HERE/'traces').glob('*.json')]
 results['spending_usd']=sum(r['cost_usd'] for r in traces);results['api_calls']=len(traces)
 results['truncated_generations']=sum(r.get('finish_reason')=='length' for r in traces if r['tag'].startswith('gen-'))
 results['unexpected_reasoning_generations']=sum(bool(r.get('reasoning_text','').strip()) for r in traces if r['tag'].startswith('gen-'))
 results['providers']=dict(collections.Counter(r.get('provider') for r in traces if r['tag'].startswith('gen-')))
 p.save(HERE/'results.json',results);p.save(HERE/'judge-comparison.json',judge_comparison)
 for name,data in [('case-results.csv',out),('replies-and-ratings.csv',raw)]:
  if data:
   with (HERE/name).open('w') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 print(json.dumps(results,indent=2))
if __name__=='__main__':main()
