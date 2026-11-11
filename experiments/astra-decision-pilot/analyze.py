"""Offline paired pilot analysis, cascade estimates and context diagnostics."""
from pathlib import Path
import collections,csv,importlib.util,json,math,statistics
H=Path(__file__).resolve().parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=module('pilot',H/'run.py');R=m.ROOT;b=m.base
NAMES={'astra':'GPT-6 Astra, high reasoning','jev':'Jev 1.14.0','decisions':'OpenAI Decisions, Luna','llm':'GPT-6 Luna, one-word'}
def pct(x,q):
 x=sorted(x);v=(len(x)-1)*q;i=int(v);return x[i]+(x[min(i+1,len(x)-1)]-x[i])*(v-i)
def wilson(c,n):
 z=1.959963984540054;p=c/n;d=1+z*z/n;mid=(p+z*z/(2*n))/d;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [mid-half,mid+half]
def score(pred,ref,records):
 n=len(ref);c=sum(x==y for x,y in zip(pred,ref));t=[r['elapsed_ms']/1000 for r in records]
 return {'n':n,'correct':c,'accuracy':c/n,'wilson_95ci':wilson(c,n),'by_label':{g:{'n':ref.count(g),'correct':sum(x==g for x,y in zip(pred,ref) if y==g)} for g in b.LABELS},'invalid':sum(x not in b.LABELS for x in pred),'cost_usd':sum(r['cost_usd'] for r in records),'median_seconds':statistics.median(t),'p95_seconds':pct(t,.95),'input_tokens':sum(r['usage']['input_tokens'] for r in records),'output_tokens':sum(r['usage'].get('output_tokens',0) for r in records),'reasoning_tokens':sum(r['usage'].get('output_tokens_details',{}).get('reasoning_tokens',0) for r in records)}
def paired(a,c,refs):
 wins=sum(x==g and y!=g for x,y,g in zip(a,c,refs));losses=sum(x!=g and y==g for x,y,g in zip(a,c,refs));n=wins+losses
 p=min(1,2*sum(math.comb(n,k) for k in range(min(wins,losses)+1))/2**n) if n else 1.
 return {'astra_only_correct':wins,'baseline_only_correct':losses,'net_correct':wins-losses,'difference_percentage_points':100*(wins-losses)/len(refs),'exact_two_sided_mcnemar_p':p}
def main():
 cfg=m.prepare();ids=cfg['indices'];rows=b.rows();refs=[rows[i]['dimension'] for i in ids];records={};pred={}
 for a in ['astra',*b.ARMS]:
  records[a]=[m.load((H/'traces'/f'astra-{i:03d}.json') if a=='astra' else (R/'experiments/final-prompt-revision/traces'/f'{a}-{i:03d}.json')) for i in ids]
  pred[a]=[]
  for i,r in zip(ids,records[a]):
   assert r['status']=='complete' and r['index']==i
   if a=='astra':
    assert r['payload']==m.payload(i) and r['payload_sha256']==m.sha(m.enc(r['payload']))==cfg['request_hashes'][str(i)]
    assert r['response']['model']=='gpt-6-astra' and abs(r['cost_usd']-m.cost(r['usage']))<1e-12
    assert r['usage']['input_tokens_details'].get('cached_tokens',0)==0 and r['usage']['input_tokens_details'].get('cache_write_tokens',0)==0
   else:assert m.sha((R/'experiments/final-prompt-revision/traces'/f'{a}-{i:03d}.json').read_bytes())==cfg['baseline_hashes'][f'{a}-{i:03d}']
   p=b.parse(r['response'],'llm' if a=='astra' else a);assert p==r['prediction'];pred[a].append(p)
 results={a:score(pred[a],refs,records[a]) for a in records}
 comparisons={a:paired(pred['astra'],pred[a],refs) for a in b.ARMS};ordered=sorted(comparisons,key=lambda k:comparisons[k]['exact_two_sided_mcnemar_p']);adj=0
 for rank,k in enumerate(ordered):adj=max(adj,min(1,(3-rank)*comparisons[k]['exact_two_sided_mcnemar_p']));comparisons[k]['holm_adjusted_p']=adj
 conf=[max(r['response']['answers']['next_move']['probabilities'].values()) for r in records['jev']]
 cascades={}
 for threshold in [.9,.8,.95]:
  defer=[p<threshold for p in conf];choices=[pred['astra'][j] if d else pred['jev'][j] for j,d in enumerate(defer)];synthetic=[]
  for j,d in enumerate(defer):
   jr=records['jev'][j];ar=records['astra'][j];synthetic.append({'elapsed_ms':jr['elapsed_ms']+(ar['elapsed_ms'] if d else 0),'cost_usd':jr['cost_usd']+(ar['cost_usd'] if d else 0),'usage':{'input_tokens':jr['usage']['input_tokens']+(ar['usage']['input_tokens'] if d else 0),'output_tokens':jr['usage']['output_tokens']+(ar['usage']['output_tokens'] if d else 0),'output_tokens_details':{'reasoning_tokens':ar['usage'].get('output_tokens_details',{}).get('reasoning_tokens',0) if d else 0}}})
  z=score(choices,refs,synthetic);z.update(threshold=threshold,astra_calls=sum(defer),jev_only_cases=20-sum(defer),cost_reduction_vs_astra=1-z['cost_usd']/results['astra']['cost_usd'],confident_jev_errors=sum(not d and pred['jev'][j]!=refs[j] for j,d in enumerate(defer)),astra_errors_avoided=sum(not d and pred['jev'][j]==refs[j] and pred['astra'][j]!=refs[j] for j,d in enumerate(defer)),astra_correct_overridden=sum(not d and pred['jev'][j]!=refs[j] and pred['astra'][j]==refs[j] for j,d in enumerate(defer)),estimated_not_deployed=True)
  cascades[str(threshold)]=z
 old={}
 for a in b.ARMS:
  rr=[m.load(R/('experiments/jev-decision-study/traces' if a=='jev' else 'experiments/openai-decision-comparison/traces')/(f'C-{i:03d}.json' if a=='jev' else f'{a}-{i:03d}.json')) for i in ids]
  pp=[b.parse(r['response'],a) for r in rr];old[a]=score(pp,refs,rr)
 diagnostics={};allrefs=[r['dimension'] for r in rows]
 for a in b.ARMS:
  rr=[m.load(R/'experiments/final-prompt-revision/traces'/f'{a}-{i:03d}.json') for i in range(520)];lengths=[r['usage']['input_tokens'] for r in rr];order=sorted(range(520),key=lambda i:lengths[i]);q=[]
  for j in range(0,520,130):
   ii=order[j:j+130];q.append({'n':130,'min_tokens':min(lengths[i] for i in ii),'max_tokens':max(lengths[i] for i in ii),'correct':sum(rr[i]['prediction']==allrefs[i] for i in ii),'accuracy':sum(rr[i]['prediction']==allrefs[i] for i in ii)/130})
  diagnostics[a]={'min_tokens':min(lengths),'median_tokens':statistics.median(lengths),'max_tokens':max(lengths),'length_quartiles':q}
  if a=='jev':
   confidence=[]
   for t in [.8,.9,.95]:
    ii=[i for i,r in enumerate(rr) if max(r['response']['answers']['next_move']['probabilities'].values())>=t];c=sum(rr[i]['prediction']==allrefs[i] for i in ii)
    confidence.append({'threshold':t,'n':len(ii),'coverage':len(ii)/520,'correct':c,'accuracy':c/len(ii),'by_label':{g:{'n':sum(allrefs[i]==g for i in ii),'correct':sum(rr[i]['prediction']==g for i in ii if allrefs[i]==g)} for g in b.LABELS}})
   diagnostics[a]['confidence_subsets']=confidence
 ensembles={}
 earlier_decisions=[m.load(R/'experiments/openai-decision-comparison/traces'/f'decisions-{i:03d}.json')['prediction'] for i in range(520)]
 for version in ['earlier','revised']:
  allrecords={}
  for a in b.ARMS:
   directory=R/('experiments/final-prompt-revision/traces' if version=='revised' else ('experiments/jev-decision-study/traces' if a=='jev' else 'experiments/openai-decision-comparison/traces'))
   allrecords[a]=[m.load(directory/(f'C-{i:03d}.json' if version=='earlier' and a=='jev' else f'{a}-{i:03d}.json')) for i in range(520)]
  pp={a:[b.parse(x['response'],a) for x in rr] for a,rr in allrecords.items()}
  votes=[collections.Counter(pp[a][i] for a in b.ARMS).most_common(1)[0][0] for i in range(520)]
  ensembles[version]={'n':520,'correct':sum(x==g for x,g in zip(votes,allrefs)),'by_label':{g:sum(votes[i]==g for i in range(520) if allrefs[i]==g) for g in b.LABELS},'component_token_cost_usd':sum(x['cost_usd'] for rr in allrecords.values() for x in rr),'fixes_vs_previous_best_decisions':sum(votes[i]==allrefs[i] and earlier_decisions[i]!=allrefs[i] for i in range(520)),'regressions_vs_previous_best_decisions':sum(votes[i]!=allrefs[i] and earlier_decisions[i]==allrefs[i] for i in range(520)),'post_hoc':True,'description':'Unweighted majority of Jev, Decisions and Luna; no new API calls.'}
 out={'n':20,'source_indices':ids,'methods':results,'astra_vs_baselines':comparisons,'cascades':cascades,'older_prompt_supplementary':old,'full_520_diagnostics':diagnostics,'post_hoc_full_520_majority':ensembles,'new_spend_usd':results['astra']['cost_usd'],'notes':['Exploratory20-case pilot; same prompt and cases, differing model/reasoning configurations.','All20 selected cases mathematical and from distinct students. Selection was independent of model errors.','All520 source records previously informed prompt development; no held-out generalization claim.','Cascade costs and latency are estimated from component traces, not a live sequential deployment.','Historical cheap-model timings and current Astra timings differ in concurrency and service conditions.']}
 m.save(H/'results.json',out)
 with (H/'All 20 decisions.csv').open('w',newline='') as f:
  fields=['moment_number','source_id','reference','astra','jev','decisions','luna','jev_probability','cascade_090','escalated_090','astra_seconds','astra_cost_usd'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for j,i in enumerate(ids):w.writerow(dict(zip(fields,[i+1,rows[i]['id'],refs[j],pred['astra'][j],pred['jev'][j],pred['decisions'][j],pred['llm'][j],conf[j],pred['astra'][j] if conf[j]<.9 else pred['jev'][j],conf[j]<.9,records['astra'][j]['elapsed_ms']/1000,records['astra'][j]['cost_usd']])))
 verification={'new_api_responses':20,'saved_comparator_responses':60,'unique_student_sampling_verified':True,'labels_10_each':True,'payloads_and_baselines_hash_verified':True,'invalid_outputs':{k:v['invalid'] for k,v in results.items()},'astra_incomplete':sum(r['response']['status']!='completed' for r in records['astra']),'no_cache_tokens':True,'source_and_frozen_plan_verified':True,'results_sha256':m.sha((H/'results.json').read_bytes()),'csv_sha256':m.sha((H/'All 20 decisions.csv').read_bytes())};m.save(H/'verification.json',verification)
 lines=['# Astra decision-only pilot','','## Material Passport','','Public TutorMoments data. Twenty new Astra classifications; saved comparison decisions. Automated analysis, no human validation or generated tutor responses.','','## Matched results','','Each method uses the same latest prompt and the same20 moments, with ten moments per category from20 distinct students. Astra uses high reasoning; Luna uses none. Sample and cascade thresholds were frozen before Astra outputs.','','| Method | Correct /20 | Accuracy | Scaffold /10 | Rigor /10 | Token cost for these20 | Median complete request |','|---|---:|---:|---:|---:|---:|---:|']
 for a,r in results.items():lines.append(f"| {NAMES[a]} | {r['correct']} | {r['accuracy']:.1%} | {r['by_label']['scaffolding']['correct']} | {r['by_label']['rigor']['correct']} | ${r['cost_usd']:.4f} | {r['median_seconds']:.2f}s |")
 lines+=['',f"New spending: **${out['new_spend_usd']:.4f}**. All other model results are reused. Astra produced {results['astra']['reasoning_tokens']:,} reasoning tokens; {verification['astra_incomplete']} incomplete responses. Its output ceiling was4096 tokens per request, including reasoning.",'','The small sample limits precision. Different reasoning settings mean this compares practical configurations, not model size alone. All records have previously informed prompt development. Latency includes the complete classification request and is not the website\'s tutoring time-to-first-answer-token metric. Cheap-model timings are historical.','','## Paired accuracy differences','','| Astra versus | Astra only correct | Comparator only correct | Net matches | Exact paired p | Holm-adjusted p |','|---|---:|---:|---:|---:|---:|']
 for a,r in comparisons.items():lines.append(f"| {NAMES[a]} | {r['astra_only_correct']} | {r['baseline_only_correct']} | {r['net_correct']:+d} | {r['exact_two_sided_mcnemar_p']:.4f} | {r['holm_adjusted_p']:.4f} |")
 lines+=['','## Jev first, Astra when uncertain','','Primary threshold0.90;0.80 and0.95 are predeclared sensitivity checks. Probabilities are model scores, not guaranteed correctness. These are offline estimates from actual component outputs, not a deployed pipeline.','','| Accept Jev at | Correct /20 | Calls to Astra /20 | Estimated cost | Saving vs always Astra | Confident Jev errors |','|---|---:|---:|---:|---:|---:|']
 for k,r in cascades.items():lines.append(f"| {k} | {r['correct']} | {r['astra_calls']} | ${r['cost_usd']:.4f} | {r['cost_reduction_vs_astra']:.1%} | {r['confident_jev_errors']} |")
 lines+=['','## Older prompt on the same sample','','These supplementary controls use an older prompt and are not prompt-matched to Astra. They help show whether the latest prompt artificially weakens a comparator.','','| Method | Correct /20 | Accuracy |','|---|---:|---:|']
 for a,r in old.items():lines.append(f"| {NAMES[a]}, earlier prompt C | {r['correct']} | {r['accuracy']:.1%} |")
 lines+=['','## Context length across all520','','| Method | Minimum tokens | Median | Maximum | Accuracy from shortest to longest quartile |','|---|---:|---:|---:|---|']
 for a,d in diagnostics.items():lines.append(f"| {NAMES[a]} | {d['min_tokens']:,} | {d['median_tokens']:,.0f} | {d['max_tokens']:,} | "+' / '.join(f"{q['accuracy']:.1%}" for q in d['length_quartiles'])+' |')
 lines+=['','These inputs fit the documented context limits. Length groups also differ in tasks, students and difficulty, so these descriptive associations do not identify a causal effect of context length. The earlier full-versus-window Jev comparison was376/520 versus375/520, offering no clear windowing gain.','','## Jev selective coverage across all520','','| Probability threshold | Cases accepted | Coverage | Correct among accepted | Observed accuracy |','|---|---:|---:|---:|---:|']
 for r in diagnostics['jev']['confidence_subsets']:lines.append(f"| {r['threshold']} | {r['n']} | {r['coverage']:.1%} | {r['correct']} | {r['accuracy']:.1%} |")
 lines+=['','These are exploratory risk/coverage descriptions from the existing full-corpus run. High accuracy on a small accepted subset is not overall benchmark accuracy or guaranteed calibration. Category breakdowns are in results.json.','','## Files and reproduction','','- [All20 decisions](All%2020%20decisions.csv), [results](results.json), [verification](verification.json).','- [Frozen plan](PLAN.md), [frozen hashes](frozen.json), `traces/` for complete requests/responses.','- [Research assessment](Research%20assessment.md): interpretation, contribution and next study.','','Offline: `python3 experiments/astra-decision-pilot/analyze.py`. Paid: `python3 experiments/astra-decision-pilot/run.py run`; completed requests resume without another charge.','','## Sources','','- [Astra model and pricing](https://developers.openai.com/api/docs/models/gpt-6-astra), [reasoning limits](https://developers.openai.com/api/docs/guides/reasoning).','- [Jev context limits](https://docs.typesafe.ai/models), [Luna context limit](https://developers.openai.com/api/docs/models/gpt-6-luna).','- [TutorMoments](https://tutormoments.allen.ai/).']
 text='\n'.join(lines)+'\n'
 for a,z in {'same20':'same 20','from20':'from 20','these20':'these 20','produced{':'produced {','was4096':'was 4096','threshold0.90;0.80 and0.95':'threshold 0.90; 0.80 and 0.95','all520':'all 520','was376/520 versus375/520':'was 376/520 versus 375/520','All20':'All 20'}.items():text=text.replace(a,z)
 (H/'README.md').write_text(text)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
