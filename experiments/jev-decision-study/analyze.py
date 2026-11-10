"""Offline, student-clustered analysis of decision agreement. No API calls."""
from pathlib import Path
import collections,csv,importlib.util,json,random,statistics
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('decision_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cal=m.module('decision_calibration',H/'calibration.py')

def quantile(a,p):
 a=sorted(a);x=(len(a)-1)*p;i=int(x);j=min(i+1,len(a)-1);return a[i]+(a[j]-a[i])*(x-i)
def prediction(e):return m.answer(e)['choice']
def stats(rows,entries,ids):
 d=m.old.metrics(rows,entries,ids)
 d['brier_rigor']=statistics.mean((m.answer(entries[i])['probabilities']['rigor']-(rows[i]['dimension']=='rigor'))**2 for i in ids)
 d['confidence_coverage']={}
 for t in [.75,.9,.95,.99]:
  accepted=[i for i in ids if max(m.answer(entries[i])['probabilities'].values())>=t]
  n=len(accepted);correct=sum(prediction(entries[i])==rows[i]['dimension'] for i in accepted)
  d['confidence_coverage'][str(t)]={'n':n,'correct':correct,'coverage':n/len(ids),'accuracy':correct/n if n else None}
 return d

def paired(rows,old,new,ids,students,new_predict=prediction):
 groups=collections.defaultdict(list)
 for i in ids:groups[students[i]].append(i)
 delta={i:int(new_predict(new[i])==rows[i]['dimension'])-int(prediction(old[i])==rows[i]['dimension']) for i in ids}
 clusters=[(len(g),sum(delta[i] for i in g)) for g in groups.values()]
 rng=random.Random(20261110);samples=[]
 for _ in range(10000):
  draw=rng.choices(clusters,k=len(clusters));samples.append(sum(d for n,d in draw)/sum(n for n,d in draw))
 return {'n':len(ids),'student_clusters':len(groups),'wins':sum(v==1 for v in delta.values()),'losses':sum(v==-1 for v in delta.values()),
 'ties':sum(v==0 for v in delta.values()),'difference_pp':100*sum(delta.values())/len(ids),
 'student_cluster_95_interval_pp':[100*quantile(samples,.025),100*quantile(samples,.975)],
 'uncertainty_note':'Exploratory percentile interval for this selected prompt on this previously explored corpus; does not include prompt-selection or repeated-service uncertainty.'}

def main():
 cfg=m.checked();rows=m.source();students=m.students(rows);sel=m.load(H/'selection.json');c=sel['selected']
 dev=cfg['development_indices'];ev=cfg['evaluation_indices'];all_ids=list(range(520))
 fresh={i:m.entry('A',i) for i in all_ids};new={i:m.entry(c,i) for i in all_ids}
 original=m.old.baseline_entries();prior=m.old.entries_in(m.old.HERE/'Full rerun/Responses')
 versions={'original_archived':original,'previous_selected_archived':prior,'previous_selected_fresh':fresh,'selected_new_round':new}
 for records in versions.values():
  assert len(records)==520
  for e in records.values():m.answer(e)
 groups=m.groups(rows);conflicts={i for ids in groups.values() if len({rows[i]['dimension'] for i in ids})>1 for i in ids}
 unique=[ids[0] for ids in groups.values() if len({rows[i]['dimension'] for i in ids})==1]
 nonconflicting=[i for i in all_ids if i not in conflicts]
 known_nonmath={137,226,266,327} # Prior response pilot screen, not an exhaustive corpus domain review.
 result={'selected_candidate':c,'candidate_name':cfg['candidates'][c]['name'],'model':cfg['model'],'audit':cfg['audit'],
 'development_scores':sel['development_scores'],'scopes':{},'paired':{},'confidence_is_model_probability_not_guarantee':True}
 for scope,ids in [('all_520',all_ids),('development_138',dev),('evaluation_382',ev),('nonconflicting_514',nonconflicting),('consistent_unique_488',unique),('excluding_four_known_nonmath_not_exhaustive',[i for i in all_ids if i not in known_nonmath])]:
  result['scopes'][scope]={name:stats(rows,entries,ids) for name,entries in versions.items()}
 for name,baseline in [('fresh_control',fresh),('archived_previous_selected',prior),('archived_original',original)]:
  result['paired'][name]=paired(rows,baseline,new,ev,students)
 result['same_prompt_repeatability']={'n':520,'same_decision':sum(prediction(fresh[i])==prediction(prior[i]) for i in all_ids),
 'prior_correct':sum(prediction(prior[i])==rows[i]['dimension'] for i in all_ids),'fresh_correct':sum(prediction(fresh[i])==rows[i]['dimension'] for i in all_ids)}
 contradictory=[]
 for h,ids in groups.items():
  if len(ids)>1:
   contradictory.append({'indices':ids,'context_sha256':h,'reference_labels':[rows[i]['dimension'] for i in ids],
    'selected_choices':[prediction(new[i]) for i in ids],'consistent_choices':len({prediction(new[i]) for i in ids})==1})
 result['duplicate_request_consistency']=contradictory
 traces=[m.load(p) for p in sorted((H/'traces').glob('*.json'))]
 assert all(t['status']=='complete' for t in traces)
 result['unique_successful_calls']=len(traces);result['input_tokens']=sum(t['usage']['input_tokens'] for t in traces)
 result['cost_usd']=sum(t['cost_usd'] for t in traces)
 result['retries']=sum(len(t.get('connection_attempts',[])) for t in traces)
 result['latency_ms']={name:{'median':statistics.median(e['elapsed_ms'] for e in entries.values()),'p95':quantile([e['elapsed_ms'] for e in entries.values()],.95)} for name,entries in [('fresh_control',fresh),('selected',new)]}
 threshold=m.load(H/'threshold-selection.json');t=threshold['threshold']
 result['secondary_threshold_analysis']={'threshold':t,'scopes':{}}
 for scope,ids in [('all_520',all_ids),('development_138',dev),('evaluation_382',ev)]:
  correct=sum(cal.decision(new[i],t)==rows[i]['dimension'] for i in ids)
  per={g:{'n':sum(rows[i]['dimension']==g for i in ids),'correct':sum(rows[i]['dimension']==g and cal.decision(new[i],t)==g for i in ids)} for g in ['scaffolding','rigor']}
  result['secondary_threshold_analysis']['scopes'][scope]={'n':len(ids),'correct':correct,'accuracy':correct/len(ids),'per_label':per,'balanced_accuracy':statistics.mean(v['correct']/v['n'] for v in per.values())}
 oof={i:d for f in threshold['development_oof'] for i,d in zip(f['indices'],f['decisions'])}
 result['secondary_threshold_analysis']['development_oof']={'n':len(oof),'correct':sum(oof[i]==rows[i]['dimension'] for i in oof),
 'balanced_accuracy':statistics.mean(sum(oof[i]==g and rows[i]['dimension']==g for i in oof)/sum(rows[i]['dimension']==g for i in oof) for g in ['scaffolding','rigor'])}
 result['secondary_threshold_analysis']['paired_evaluation_vs_fresh_control']=paired(rows,fresh,new,ev,students,new_predict=lambda e:cal.decision(e,t))
 repeats={1:new,**{rep:{i:m.load(H/'traces'/f'R{rep}-{i:03d}.json') for i in all_ids} for rep in [2,3]}}
 majority={i:collections.Counter(prediction(repeats[rep][i]) for rep in repeats).most_common(1)[0][0] for i in all_ids}
 meanprob={i:statistics.mean(m.answer(repeats[rep][i])['probabilities']['rigor'] for rep in repeats) for i in all_ids}
 meanchoice={i:('rigor' if meanprob[i]>.5 else 'scaffolding' if meanprob[i]<.5 else prediction(new[i])) for i in all_ids}
 def derived_stats(choices,ids):
  correct=sum(choices[i]==rows[i]['dimension'] for i in ids)
  per={g:{'n':sum(rows[i]['dimension']==g for i in ids),'correct':sum(rows[i]['dimension']==g and choices[i]==g for i in ids)} for g in ['scaffolding','rigor']}
  return {'n':len(ids),'correct':correct,'accuracy':correct/len(ids),'per_label':per,'balanced_accuracy':statistics.mean(v['correct']/v['n'] for v in per.values())}
 result['repeatability']={'same_choice_all_three':sum(len({prediction(repeats[rep][i]) for rep in repeats})==1 for i in all_ids),
 'n':520,'changed_indices':[i for i in all_ids if len({prediction(repeats[rep][i]) for rep in repeats})>1],
 'runs':{str(rep):{scope:stats(rows,entries,ids) for scope,ids in [('all_520',all_ids),('evaluation_382',ev)]} for rep,entries in repeats.items()},
 'majority':{scope:derived_stats(majority,ids) for scope,ids in [('all_520',all_ids),('evaluation_382',ev)]},
 'mean_probability':{scope:derived_stats(meanchoice,ids) for scope,ids in [('all_520',all_ids),('evaluation_382',ev)]},
 'majority_paired_vs_fresh_control':paired(rows,fresh,{i:{'decision':majority[i]} for i in all_ids},ev,students,new_predict=lambda e:e['decision'])}
 result['examples']={}
 for kind,predicate in [('improved',lambda i:prediction(fresh[i])!=rows[i]['dimension'] and prediction(new[i])==rows[i]['dimension']),('regressed',lambda i:prediction(fresh[i])==rows[i]['dimension'] and prediction(new[i])!=rows[i]['dimension']),('persistent_error',lambda i:prediction(fresh[i])!=rows[i]['dimension'] and prediction(new[i])!=rows[i]['dimension'])]:
  candidates=[i for i in ev if predicate(i)];candidates.sort(key=lambda i:(-max(m.answer(new[i])['probabilities'].values()),i))
  result['examples'][kind]=candidates[:3]
 csvrows=[]
 for i,r in enumerate(rows):
  a=m.answer(new[i]);d={'moment_index':i,'student_id':students[i],'split':'development' if i in dev else 'evaluation','reference_label':r['dimension'],
   'original_archived':prediction(original[i]),'previous_selected_archived':prediction(prior[i]),'previous_selected_fresh':prediction(fresh[i]),
   'new_selected_prompt':c,'new_decision':a['choice'],'correct':a['choice']==r['dimension'],'thresholded_decision':cal.decision(new[i],t),'thresholded_correct':cal.decision(new[i],t)==r['dimension'],'p_scaffolding':a['probabilities']['scaffolding'],'p_rigor':a['probabilities']['rigor'],
   'repeat_2':prediction(repeats[2][i]),'repeat_3':prediction(repeats[3][i]),'majority_decision':majority[i],'mean_probability_decision':meanchoice[i],'mean_p_rigor':meanprob[i],
   'top_probability':max(a['probabilities'].values()),'confidence':a['confidence'],'identical_input_label_conflict':i in conflicts,
   'known_nonmath_from_prior_screen':i in known_nonmath,'context_turns':len(r['context']),'selected_input_turns':len(m.window(r['context'])) if cfg['candidates'][c]['view']=='window' else len(r['context']),
   'teacher_note_for_review_only_never_sent':r['rubric'].get('hint',''),'last_student_turn':next((t['text'] for t in reversed(r['context']) if t['role']=='student'),'')}
  csvrows.append(d)
 for name,data in [('All 520 decisions.csv',csvrows),('Errors for review.csv',[r for r in csvrows if not r['correct']])]:
  with (H/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(csvrows[0]));w.writeheader();w.writerows(data)
 m.save(H/'results.json',result)
 m.save(H/'selected-prompt.json',cfg['candidates'][c])
 print(json.dumps({'selected':c,'development':sel['development_scores'],'all':{k:v['correct'] for k,v in result['scopes']['all_520'].items()},'evaluation':{k:v['correct'] for k,v in result['scopes']['evaluation_382'].items()},'paired':result['paired'],'cost_usd':result['cost_usd'],'calls':len(traces)},indent=2))
if __name__=='__main__':main()
