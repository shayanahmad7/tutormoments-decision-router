"""Recompute every score from saved API responses. No network calls."""
import collections,csv,importlib.util,json,math,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('matched_run',H/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=m.ROOT
METHODS=['jev','decisions','llm']
NAMES={'jev':'Jev 1.14.0, prompt C (saved first run)','decisions':'OpenAI Decisions, GPT-6 Luna','llm':'GPT-6 Luna, one-word response'}
def percentile(x,p):
 v=sorted(x);a=(len(v)-1)*p;i=int(a);return v[i]+(v[min(i+1,len(v)-1)]-v[i])*(a-i)
def stats(pred,refs,records):
 n=len(refs);cm={g:{h:0 for h in ['scaffolding','rigor','invalid']} for g in ['scaffolding','rigor']}
 for p,g in zip(pred,refs):cm[g][p if p in ['scaffolding','rigor'] else 'invalid']+=1
 correct=sum(p==g for p,g in zip(pred,refs));f1=[]
 for g in ['scaffolding','rigor']:
  tp=cm[g][g];fp=sum(v[g] for k,v in cm.items() if k!=g);fn=sum(v for k,v in cm[g].items() if k!=g)
  f1.append(2*tp/(2*tp+fp+fn) if tp else 0)
 times=[r['elapsed_ms']/1000 for r in records];clean=[r['elapsed_ms']/1000 for r in records if len(r.get('attempts',r.get('connection_attempts',[])))<=1]
 return {'n':n,'correct':correct,'accuracy':correct/n,'scaffolding_correct':cm['scaffolding']['scaffolding'],'rigor_correct':cm['rigor']['rigor'],'invalid':sum(p not in ['scaffolding','rigor'] for p in pred),'macro_f1':statistics.mean(f1),'confusion_matrix':cm,'cost_usd':sum(r['cost_usd'] for r in records),'input_tokens':sum(r['usage']['input_tokens'] for r in records),'output_tokens':sum(r['usage'].get('output_tokens',0) for r in records),'median_seconds':statistics.median(times),'p95_seconds':percentile(times,.95),'clean_median_seconds':statistics.median(clean),'retried_requests':sum(len(r.get('attempts',r.get('connection_attempts',[])))>1 for r in records)}
def main():
 m.prepare();rows=m.rows();refs=[r['dimension'] for r in rows];cfg=m.load(H/'frozen.json')
 pred={};records={};checks=[]
 for arm in ['decisions','llm']:
  rr=[m.load(H/'traces'/f'{arm}-{i:03d}.json') for i in range(520)]
  for i,r in enumerate(rr):
   assert r['status']=='complete'
   assert r['payload_sha256']==m.sha(m.enc(r['payload']))==cfg['payload_hashes'][arm][i]
   assert r['response']['model']=='gpt-6-luna'
   assert r['prediction']==m.parse(r['response'],arm)
   assert abs(r['cost_usd']-m.cost(r['response']['usage'],arm))<1e-12
   assert r['usage']['input_tokens_details'].get('cached_tokens',0)==0
   assert r['usage']['input_tokens_details'].get('cache_write_tokens',0)==0
   if arm=='llm':assert r['usage']['output_tokens_details'].get('reasoning_tokens',0)==0
  records[arm]=rr;pred[arm]=[m.parse(r['response'],arm) for r in rr]
 records['jev']=[m.prior(i) for i in range(520)]
 for i,r in enumerate(records['jev']):assert m.sha((ROOT/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json').read_bytes())==cfg['jev_trace_sha256'][i]
 pred['jev']=[r['response']['answers']['next_move']['choice'] for r in records['jev']]
 results={k:stats(pred[k],refs,records[k]) for k in METHODS}
 split=m.load(ROOT/'experiments/jev/Context-focused prompt test/Development and evaluation split.json')
 for k in METHODS:
  results[k]['prior_split']={s:{'n':len(split[s]),'correct':sum(pred[k][i]==refs[i] for i in split[s])} for s in ['development_indices','evaluation_indices']}
 transcripts=[json.loads(l) for l in (ROOT/'data/jev/transcripts.jsonl').read_text().splitlines()]
 studentmap={r['transcript_id']:r['session']['student_id'] for r in transcripts}
 students=[studentmap[r['provenance']['conv_id'].split('_')[-1]] for r in rows]
 grouped=collections.defaultdict(list)
 for i,s in enumerate(students):grouped[s].append(i)
 pairs={}
 for a,b in [('decisions','llm'),('decisions','jev'),('llm','jev')]:
  delta=[int(pred[a][i]==refs[i])-int(pred[b][i]==refs[i]) for i in range(520)]
  clusters=[(sum(delta[i] for i in ids),len(ids)) for ids in grouped.values()];rng=random.Random(m.SEED);boot=[]
  for _ in range(10000):
   sample=rng.choices(clusters,k=len(clusters));boot.append(sum(x for x,n in sample)/sum(n for x,n in sample))
  pairs[a+'_minus_'+b]={'additional_correct':sum(delta),'difference_percentage_points':sum(delta)/520*100,'a_only_correct':delta.count(1),'b_only_correct':delta.count(-1),'both_correct':sum(pred[a][i]==refs[i] and pred[b][i]==refs[i] for i in range(520)),'neither_correct':sum(pred[a][i]!=refs[i] and pred[b][i]!=refs[i] for i in range(520)),'student_cluster_bootstrap_95ci_percentage_points':[percentile(boot,.025)*100,percentile(boot,.975)*100]}
 out={'methods':results,'paired_comparisons':pairs,'student_clusters':len(grouped),'bootstrap_resamples':10000,'bootstrap_seed':m.SEED,'new_cost_usd':results['decisions']['cost_usd']+results['llm']['cost_usd'],'notes':['Raw returned choices only; no probability threshold fitted in this round.','One pass per API per record. Prompt C was previously explored on these data; exploratory benchmark comparison, not new generalization validation.','Jev timings are from a prior run. OpenAI runs interleaved with four HTTP workers and caching disabled.','Costs computed from recorded API token usage and published prices, not a billing invoice.','Student-cluster intervals address within-student dependence, not prompt-selection bias or reference-label uncertainty.']}
 m.save(H/'results.json',out)
 fields=['moment_number','source_id','reference','jev_decision','openai_decisions_decision','llm_one_word_decision','jev_correct','openai_decisions_correct','llm_correct','jev_rigor_probability','openai_rigor_probability','decisions_seconds','llm_seconds','decisions_cost_usd','llm_cost_usd']
 with (H/'All 520 decisions.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for i,row in enumerate(rows):
   probs=records['decisions'][i]['response']['answers'][0].get('probabilities',[])
   writer.writerow(dict(zip(fields,[i+1,row['id'],refs[i],pred['jev'][i],pred['decisions'][i],pred['llm'][i],pred['jev'][i]==refs[i],pred['decisions'][i]==refs[i],pred['llm'][i]==refs[i],records['jev'][i]['response']['answers']['next_move']['probabilities']['rigor'],next((p['probability'] for p in probs if p['value']=='rigor'),None),records['decisions'][i]['elapsed_ms']/1000,records['llm'][i]['elapsed_ms']/1000,records['decisions'][i]['cost_usd'],records['llm'][i]['cost_usd']])))
 verified={'complete_new_requests':1040,'reused_jev_records':520,'unique_new_tags':len({r['arm']+'-'+str(r['index']) for arm in ['decisions','llm'] for r in records[arm]}),'payload_hashes_verified':1040,'source_and_full_context_verified':True,'cost_recomputed':True,'no_cache_tokens':True,'no_llm_reasoning_tokens':True,'invalid_outputs':{k:results[k]['invalid'] for k in METHODS},'results_sha256':m.sha((H/'results.json').read_bytes()),'comparison_csv_sha256':m.sha((H/'All 520 decisions.csv').read_bytes())}
 m.save(H/'verification.json',verified)
 lines=['# Scaffold or rigor: Decisions API versus a one-word LLM','','All **520 moments** were tested in each OpenAI condition. The saved Jev prompt C results provide the third comparison. Every method received the same full pre-cut conversation and decision criteria. No tutoring response was generated.','','| Method | Correct /520 | Accuracy | Scaffold /260 | Rigor /260 | Median latency | Token cost |','|---|---:|---:|---:|---:|---:|---:|']
 for k in METHODS:
  r=results[k];lines.append(f"| {NAMES[k]} | {r['correct']} | {r['accuracy']:.1%} | {r['scaffolding_correct']} | {r['rigor_correct']} | {r['median_seconds']:.3f}s | ${r['cost_usd']:.4f} |")
 lines+=['','Jev cost and latency describe its earlier saved run. **New spending for both OpenAI runs: $'+f"{out['new_cost_usd']:.4f}"+'**. Cost is calculated from recorded usage at published prices. No caching was used in either OpenAI condition. All completed requests, including preflight calls, are included.','','## Paired differences','','| Comparison | Net additional matches | First only correct | Second only correct | Difference (percentage points), student-cluster 95% interval |','|---|---:|---:|---:|---:|']
 for key,v in pairs.items():
  lo,hi=v['student_cluster_bootstrap_95ci_percentage_points'];lines.append(f"| {key.replace('_minus_',' versus ')} | {v['additional_correct']:+d} | {v['a_only_correct']} | {v['b_only_correct']} | {v['difference_percentage_points']:+.2f} [{lo:+.2f}, {hi:+.2f}] |")
 lines+=['','## What this comparison measures','','This measures agreement with the published scaffolding/rigor category at the stopping point. It does not measure the quality of a generated tutor response or student learning. The published labels are unchanged, including three identical-context pairs with opposite labels.','','Prompt C was selected during earlier exploration of this corpus. These are full-benchmark exploratory results, not a new held-out test. Raw API choices are compared; the previously tuned Jev threshold is not substituted into the main table. The LLM baseline uses reasoning none and a 32-token output ceiling, so the result does not represent all LLM prompting or reasoning settings.','','The two new arms use GPT-6 Luna but different API interfaces. They receive identical evidence and instructional criteria; the LLM additionally receives a one-word formatting instruction. This compares two practical classification configurations, not an isolated causal estimate of one internal model mechanism.','','## Timing and output checks','','| Method | p95 latency | Retried requests | Invalid outputs |','|---|---:|---:|---:|']
 for k in METHODS:
  r=results[k];lines.append(f"| {NAMES[k]} | {r['p95_seconds']:.3f}s | {r['retried_requests']} | {r['invalid']} |")
 lines+=['','Timing measures complete HTTP requests, not time-to-first-token. The OpenAI conditions were interleaved; Jev ran earlier. Service/network load can change timings.','','## Files and reproduction','','- [All 520 decisions](All%20520%20decisions.csv): one row per record, all three predictions, correctness, probabilities, cost and timing.','- [Frozen plan](PLAN.md), [frozen hashes](frozen.json), [machine-readable results](results.json), [verification](verification.json).','- `traces/`: exact OpenAI requests, responses, usage and timings; saved Jev trace hashes point to `../jev-decision-study/traces/C-*.json`.','','Offline: `python3 experiments/openai-decision-comparison/analyze.py`. This recomputes results and verifies full context, source, prompt and response hashes without API calls.','','Paid rerun: `python3 experiments/openai-decision-comparison/run.py run`. Completed identical requests resume without new charges. Budget cap $2. Credentials are read from the environment or a private env file and are not included in this archive.','','## Sources','','- [TutorMoments dataset](https://huggingface.co/datasets/allenai/tutormoments-preview), pinned revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`.','- [OpenAI Decisions documentation](https://developers.openai.com/api/docs/guides/decisions), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing).','- [Jev models and pricing](https://docs.typesafe.ai/models).','','## Material Passport','','Public TutorMoments-Preview source; automated classification only. 1,040 new OpenAI calls and 520 saved Jev calls. Status: completed, results recomputed from archived responses. No human validation claimed.']
 (H/'README.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
