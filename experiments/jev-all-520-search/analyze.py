"""Offline full-benchmark search. Results are exploratory, not held out."""
from pathlib import Path
import collections,csv,importlib.util,json,statistics
from decimal import Decimal
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('full_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def metrics(gold,choices,probs,ids):
 cm={g:{p:sum(gold[i]==g and choices[i]==p for i in ids) for p in ['scaffolding','rigor']} for g in ['scaffolding','rigor']}
 per={}
 for g in cm:
  n=sum(cm[g].values());tp=cm[g][g];pred=sum(cm[k][g] for k in cm)
  precision=tp/pred if pred else 0;recall=tp/n
  per[g]={'n':n,'correct':tp,'recall':recall,'precision':precision,'f1':2*precision*recall/(precision+recall) if precision+recall else 0}
 correct=sum(gold[i]==choices[i] for i in ids)
 return {'n':len(ids),'correct':correct,'accuracy':correct/len(ids),'per_label':per,'confusion_matrix':cm,
 'macro_f1':statistics.mean(x['f1'] for x in per.values()),'brier_rigor':statistics.mean((probs[i]-(gold[i]=='rigor'))**2 for i in ids)}
def thresholded(probs,raw,t):
 if t==.5:return dict(raw)
 return {i:'rigor' if p>=t else 'scaffolding' for i,p in probs.items()}
def mean_probability(values):
 # Respect decimal probabilities returned by the API at exact grid boundaries.
 return float(sum((Decimal(str(p)) for p in values),Decimal(0))/len(values))

def main():
 cfg=m.checked();rows=m.m.source();ids=list(range(520));gold={i:r['dimension'] for i,r in enumerate(rows)}
 probabilities={};decisions={};full={};traces={}
 for c in m.specs():
  es={i:m.entry(c,i) for i in ids};assert all(e['status']=='complete' for e in es.values())
  traces[c]=es;answers={i:m.m.answer(e) for i,e in es.items()}
  probabilities[c]={i:a['probabilities']['rigor'] for i,a in answers.items()};decisions[c]={i:a['choice'] for i,a in answers.items()}
  full[c]=metrics(gold,decisions[c],probabilities[c],ids)
 probabilities['mean']={i:mean_probability([probabilities[c][i] for c in m.specs()]) for i in ids}
 decisions['mean']={i:'rigor' if p>.5 else 'scaffolding' if p<.5 else decisions['A'][i] for i,p in probabilities['mean'].items()}
 full['mean']=metrics(gold,decisions['mean'],probabilities['mean'],ids)
 curves={};tuned={};tuned_decisions={}
 for c in full:
  curves[c]=[]
  for t in cfg['threshold_grid']:
   choices=thresholded(probabilities[c],decisions[c],t)
   curves[c].append({'threshold':t,'correct':sum(choices[i]==gold[i] for i in ids),'n':520})
  best=min(curves[c],key=lambda x:(-x['correct'],abs(x['threshold']-.5),x['threshold']))
  tuned_decisions[c]=thresholded(probabilities[c],decisions[c],best['threshold'])
  tuned[c]={'threshold':best['threshold'],**metrics(gold,tuned_decisions[c],probabilities[c],ids)}
 best_raw=min(m.specs(),key=lambda c:(-full[c]['correct'],len(m.m.enc(m.specs()[c]['question'])),c))
 best_tuned=min(tuned,key=lambda c:(-tuned[c]['correct'],c=='mean',abs(tuned[c]['threshold']-.5),len(m.m.enc(m.specs()[c]['question'])) if c!='mean' else 0,c))
 current=[m.m.load(p) for p in sorted((H/'traces').glob('*.json'))];assert len(current)==1666
 groups=m.m.groups(rows);conflicts={i for g in groups.values() if len({gold[i] for i in g})>1 for i in g}
 no_conflict=[i for i in ids if i not in conflicts];unique=[g[0] for g in groups.values() if not set(g)&conflicts]
 selected={}
 for name,c,choices in [('best_raw',best_raw,decisions[best_raw]),('best_tuned',best_tuned,tuned_decisions[best_tuned])]:
  selected[name]={'candidate':c,'all_520':metrics(gold,choices,probabilities[c],ids),
    'nonconflicting_514':metrics(gold,choices,probabilities[c],no_conflict),
    'consistent_unique_488':metrics(gold,choices,probabilities[c],unique),
    'wins_vs_A':sum(choices[i]==gold[i] and decisions['A'][i]!=gold[i] for i in ids),
    'losses_vs_A':sum(choices[i]!=gold[i] and decisions['A'][i]==gold[i] for i in ids)}
 result={'status':'complete','model':'jev-1.14.0','records_per_candidate':520,'candidate_record_decisions':3120,
 'scope':'Exploratory optimization and evaluation on the same 520 records; not held-out validation.',
 'candidates':{c:v['name'] for c,v in m.specs().items()},'raw':full,'threshold_fitted':tuned,'threshold_curves':curves,
 'selection':selected,'best_threshold':tuned[best_tuned]['threshold'],
 'best_tuned_tie_rule':'Highest full-set accuracy, prefer one-call over six-call ensemble, closest threshold to .5, shorter question, ID.',
 'reused_calls':len(cfg['reused']),'new_calls':len(current),'new_input_tokens':sum(e['usage']['input_tokens'] for e in current),
 'new_cost_usd':sum(e['cost_usd'] for e in current),'retries':sum(len(e.get('connection_attempts',[])) for e in current),
 'source_labels_changed':False,'tutor_or_judge_calls':0,
 'confidence':{str(t):{'n':sum(max(p,1-p)>=t for p in probabilities[best_raw].values()),'correct':sum(max(probabilities[best_raw][i],1-probabilities[best_raw][i])>=t and decisions[best_raw][i]==gold[i] for i in ids)} for t in [.75,.9,.95,.99]}}
 records=[]
 for i,row in enumerate(rows):
  record={'moment_index':i,'reference_label':gold[i]}
  for c in m.specs():record[c+'_decision']=decisions[c][i];record[c+'_p_rigor']=probabilities[c][i]
  record.update(mean_p_rigor=probabilities['mean'][i],best_raw_candidate=best_raw,best_raw_decision=decisions[best_raw][i],best_raw_correct=decisions[best_raw][i]==gold[i],
   best_fitted_candidate=best_tuned,best_fitted_threshold=tuned[best_tuned]['threshold'],best_fitted_decision=tuned_decisions[best_tuned][i],best_fitted_correct=tuned_decisions[best_tuned][i]==gold[i],
   identical_input_label_conflict=i in conflicts,context_turns=len(row['context']),last_student_turn=next((t['text'] for t in reversed(row['context']) if t['role']=='student'),''))
  records.append(record)
 for name,data in [('All 520 - Six prompt decisions.csv',records),('Best raw prompt - Errors.csv',[r for r in records if not r['best_raw_correct']])]:
  with (H/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(data)
 curve_rows=[{'candidate':c,**r} for c,curve in curves.items() for r in curve]
 with (H/'Threshold search.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(curve_rows[0]));w.writeheader();w.writerows(curve_rows)
 m.m.save(H/'results.json',result)
 print(json.dumps({'raw':{c:v['correct'] for c,v in full.items()},'tuned':{c:[v['correct'],v['threshold']] for c,v in tuned.items()},'best_raw':best_raw,'best_tuned':best_tuned,'new_cost':result['new_cost_usd']},indent=2))
if __name__=='__main__':main()
