"""Offline verification and paired analysis of the one-shot prompt revision."""
import collections,csv,importlib.util,json,random,statistics
from pathlib import Path
H=Path(__file__).resolve().parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=module('final_runner',H/'run.py')
old=module('prior_analysis',m.ROOT/'experiments/openai-decision-comparison/analyze.py')
NAMES={'jev':'Jev 1.14.0','decisions':'OpenAI Decisions (GPT-6 Luna)','llm':'GPT-6 Luna, one-word answer'}

def main():
 m.prepare();cfg=m.load(H/'frozen.json');rows=m.rows();refs=[r['dimension'] for r in rows]
 predictions={};records={};previous={}
 for arm in m.ARMS:
  rr=[m.load(H/'traces'/f'{arm}-{i:03d}.json') for i in range(520)]
  for i,r in enumerate(rr):
   assert r['arm']==arm and r['index']==i and r['status']=='complete'
   assert len(r['attempts'])==1 and r['attempts'][0]['status']==200
   assert m.sha(m.enc(r['payload']))==r['payload_sha256']==cfg['payload_hashes'][arm][i]
   assert r['payload']==m.payload(rows[i],arm)
   assert r['response']['model']==m.MODELS[arm]
   assert r['prediction']==m.parse(r['response'],arm)
   assert r['usage']==r['response']['usage']
   assert abs(r['cost_usd']-m.cost(r['usage'],arm))<1e-12
   if arm!='jev':
    assert r['usage']['input_tokens_details'].get('cached_tokens',0)==0
    assert r['usage']['input_tokens_details'].get('cache_write_tokens',0)==0
   if arm=='llm':assert r['usage']['output_tokens_details'].get('reasoning_tokens',0)==0
  records[arm]=rr;predictions[arm]=[r['prediction'] for r in rr]
  if arm=='jev':prior=[m.load(m.ROOT/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json') for i in range(520)]
  else:prior=[m.load(m.ROOT/'experiments/openai-decision-comparison/traces'/f'{arm}-{i:03d}.json') for i in range(520)]
  previous[arm]=[m.parse(r['response'],arm) for r in prior]
 results={k:old.stats(predictions[k],refs,records[k]) for k in m.ARMS}
 failures=[m.load(p) for p in sorted((H/'traces').glob('failed-*.json'))]
 for f in failures:
  assert f['status']=='failed' and 'response' not in f
  assert f['payload_sha256']==m.sha(m.enc(f['payload']))==cfg['payload_hashes'][f['arm']][f['index']]
 for k in m.ARMS:
  ff=[f for f in failures if f['arm']==k];failed_indices={f['index'] for f in ff}
  results[k]['retried_requests']=len(failed_indices)
  results[k]['failed_transport_attempts']=sum(len(f['attempts']) for f in ff)
  results[k]['failed_attempt_seconds']=sum(f['elapsed_ms']/1000 for f in ff)
  results[k]['failed_attempt_cost_reservation_usd']=sum(f['cost_usd'] for f in ff)
  clean=[r['elapsed_ms']/1000 for r in records[k] if r['index'] not in failed_indices]
  results[k]['clean_median_seconds']=statistics.median(clean)
  inclusive=[(r['elapsed_ms']+sum(f['elapsed_ms'] for f in ff if f['index']==r['index']))/1000 for r in records[k]]
  results[k]['retry_inclusive_median_seconds']=statistics.median(inclusive)
  results[k]['retry_inclusive_p95_seconds']=old.percentile(inclusive,.95)

 transcript_rows=[json.loads(l) for l in (m.ROOT/'data/jev/transcripts.jsonl').read_text().splitlines()]
 sm={r['transcript_id']:r['session']['student_id'] for r in transcript_rows};students=[sm[r['provenance']['conv_id'].split('_')[-1]] for r in rows]
 groups=collections.defaultdict(list)
 for i,s in enumerate(students):groups[s].append(i)
 def paired(a,b):
  delta=[int(a[i]==refs[i])-int(b[i]==refs[i]) for i in range(520)]
  clusters=[(sum(delta[i] for i in ids),len(ids)) for ids in groups.values()];rng=random.Random(m.SEED);boot=[]
  for _ in range(10000):
   sample=rng.choices(clusters,k=len(clusters));boot.append(sum(x for x,n in sample)/sum(n for x,n in sample))
  return {'additional_correct':sum(delta),'difference_percentage_points':sum(delta)/520*100,'a_only_correct':delta.count(1),'b_only_correct':delta.count(-1),'both_correct':sum(a[i]==refs[i] and b[i]==refs[i] for i in range(520)),'neither_correct':sum(a[i]!=refs[i] and b[i]!=refs[i] for i in range(520)),'student_cluster_bootstrap_95ci_percentage_points':[old.percentile(boot,.025)*100,old.percentile(boot,.975)*100]}
 changes={k:paired(predictions[k],previous[k]) for k in m.ARMS}
 pairs={a+'_minus_'+b:paired(predictions[a],predictions[b]) for a,b in [('decisions','llm'),('decisions','jev'),('llm','jev')]}
 context_groups=collections.defaultdict(list)
 for i,r in enumerate(rows):context_groups[m.sha(m.enc(r['context']))].append(i)
 conflicts=[ids for ids in context_groups.values() if len({refs[i] for i in ids})>1]
 notes=[json.loads(l) for p in m.review_files() for l in p.read_text().splitlines() if l.strip()]
 reviews={i:n for n in notes for i in n['indices']}
 result={'methods':results,'previous_correct':{k:sum(p==g for p,g in zip(previous[k],refs)) for k in m.ARMS},'new_minus_previous':changes,'new_method_comparisons':pairs,'cost_usd':sum(r['cost_usd'] for r in results.values()),'student_clusters':len(groups),'bootstrap_resamples':10000,'bootstrap_seed':m.SEED,'review_conversations':len(notes),'review_moments':len(reviews),'unique_contexts':len(context_groups),'conflicting_context_groups_zero_based':conflicts,'deterministic_context_only_maximum_correct':sum(max(collections.Counter(refs[i] for i in ids).values()) for ids in context_groups.values()),'interpretation':'Exploratory agreement with unchanged published labels after full-corpus prompt development. Not held-out validation or a measure of tutoring quality.'}
 result['previous_class_correct']={k:{g:sum(previous[k][i]==g for i in range(520) if refs[i]==g) for g in m.LABELS} for k in m.ARMS}
 result['failed_transport_attempts']=sum(len(f['attempts']) for f in failures)
 result['failed_attempt_cost_reservation_usd']=sum(f['cost_usd'] for f in failures)
 result['budget_accounted_cost_usd']=result['cost_usd']+result['failed_attempt_cost_reservation_usd']
 result['api_attempts']=1560+result['failed_transport_attempts']
 m.save(H/'results.json',result)
 fields=['moment_number','source_id','conversation_group','reference','review_domain']
 for k in m.ARMS:fields += [k+'_previous',k+'_revised',k+'_correct',k+'_change',k+'_seconds',k+'_cost_usd']
 with (H/'All 520 decisions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for i,r in enumerate(rows):
   row={'moment_number':i+1,'source_id':r['id'],'conversation_group':reviews[i]['group'],'reference':refs[i],'review_domain':reviews[i].get('domain','Not separately classified')}
   for k in m.ARMS:
    before=previous[k][i]==refs[i];after=predictions[k][i]==refs[i]
    row.update({k+'_previous':previous[k][i],k+'_revised':predictions[k][i],k+'_correct':after,k+'_change':'fixed' if after and not before else 'regressed' if before and not after else 'unchanged',k+'_seconds':records[k][i]['elapsed_ms']/1000,k+'_cost_usd':records[k][i]['cost_usd']})
   w.writerow(row)
 verification={'completed_decisions':1560,'api_attempts':result['api_attempts'],'failed_transport_attempts':result['failed_transport_attempts'],'completed_per_method':{k:len(records[k]) for k in m.ARMS},'attempts_per_successful_trace':1,'full_context_verified':True,'no_labels_hints_future_or_ids_in_request_construction':True,'frozen_request_hashes_verified':1560,'review_coverage':m.review_audit(),'invalid_outputs':{k:results[k]['invalid'] for k in m.ARMS},'cost_recomputed':True,'no_openai_cache_or_llm_reasoning_tokens':True,'results_sha256':m.sha((H/'results.json').read_bytes()),'csv_sha256':m.sha((H/'All 520 decisions.csv').read_bytes())}
 m.save(H/'verification.json',verification)
 lines=['# One final prompt revision: scaffold or rigor','','All 520 published moments were classified once by each method using one frozen revised prompt and the complete conversation up to the cutoff. No tutoring responses were generated.','','| Method | Previous correct | Revised correct | Revised accuracy | Change | Scaffold /260 | Rigor /260 | New token cost | Median request latency |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 best_previous=max(m.ARMS,key=lambda k:result['previous_correct'][k])
 best_new=max(m.ARMS,key=lambda k:results[k]['correct'])
 lines[4:4]=[f"The best revised score is {results[best_new]['correct']}/520 from {NAMES[best_new]}. The previous best was {result['previous_correct'][best_previous]}/520 from {NAMES[best_previous]}. The revision did not improve that previous best. Retain the earlier Decisions prompt as the strongest observed configuration; the small LLM gain is not a demonstrated generalization improvement.",'']
 for k in m.ARMS:
  r=results[k];d=changes[k];lines.append(f"| {NAMES[k]} | {result['previous_correct'][k]}/520 | {r['correct']}/520 | {r['accuracy']:.1%} | {d['difference_percentage_points']:+.2f} pp | {r['scaffolding_correct']} | {r['rigor_correct']} | ${r['cost_usd']:.4f} | {r['median_seconds']:.3f}s |")
 lines += ['',f"Total new token cost: **${result['cost_usd']:.4f}**. Costs use recorded token usage and published rates, not an invoice. All 1,560 completed decisions, including preflight responses, are included. No probability thresholds were fitted and no completed predictions were rerun.",'','## What changed','','The new prompt judges the current instructional need across the learning episode. It distinguishes an unresolved obstacle from a reachable opportunity to explain, attempt or self-correct. It tracks which work the student actually produced, fades help when the obstacle is resolved, and does not equate every error with a need for help or every correct substep with understanding. Specific examples from the previous prompt were removed. See [the exact prompt](prompt.json).','','## Review and evidence limits','','The primary agent and three review subagents reviewed all pre-cut turns in the 112 distinct conversation prefixes that contain these 520 moments, with markers at every earlier cutoff. Repeated shared prefixes were read once. Notes are AI-assisted review, not human adjudication; the source labels were never changed. See [review synthesis](Review%20findings.md) and the per-conversation JSONL notes.','','The full source file includes some literacy and vocabulary moments as well as mathematics. The requested all 520 comparison retains them and should be described as a TutorMoments benchmark result, not an exclusively math result. Domain notes are descriptive and were not used to select or exclude cases.','','All 520 cases and previous errors informed prompt development. This is an exploratory full-benchmark revision, **not an unseen-data test**. The prompt contains no case IDs, answer lookup rules, teacher hints, expected labels or case-specific examples, but those safeguards do not remove development-set bias. A new held-out corpus is needed to test generalization.','','The reference category is aggregated teacher annotation. A representative hint can disagree with that aggregate, and some hints describe later exchanges unavailable to a classifier at the cutoff. Three identical-context pairs have opposite categories, limiting a consistent deterministic context-only classifier to 517/520. Neither that ceiling nor a higher agreement score establishes the best teaching action or student learning.','','## Paired changes from the previous prompt','','| Method | Previously wrong, now correct | Previously correct, now wrong | Net change | 95% student-cluster interval for change (pp) |','|---|---:|---:|---:|---:|']
 for k,d in changes.items():
  lo,hi=d['student_cluster_bootstrap_95ci_percentage_points'];lines.append(f"| {NAMES[k]} | {d['a_only_correct']} | {d['b_only_correct']} | {d['additional_correct']:+d} | [{lo:+.2f}, {hi:+.2f}] |")
 lines += ['','Intervals use 10,000 paired bootstrap resamples of 89 student clusters. They describe uncertainty in the observed paired differences, not prompt-selection bias or generalization.','','## Comparison among the revised methods','','| Comparison | Net correct advantage | Difference (pp) | 95% student-cluster interval (pp) |','|---|---:|---:|---:|']
 for key,d in pairs.items():
  lo,hi=d['student_cluster_bootstrap_95ci_percentage_points'];lines.append(f"| {key.replace('_minus_',' versus ')} | {d['additional_correct']:+d} | {d['difference_percentage_points']:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
 lines += ['', '## Which decisions changed', '']
 for k in m.ARMS:
  prev=result['previous_class_correct'][k];r=results[k]
  lines.append(f"- {NAMES[k]}: scaffolding matches {prev['scaffolding']} to {r['scaffolding_correct']} ({r['scaffolding_correct']-prev['scaffolding']:+d}); rigor matches {prev['rigor']} to {r['rigor_correct']} ({r['rigor_correct']-prev['rigor']:+d}).")
 lines += ['','The same instruction and criterion strings were used through provider-specific request schemas. The two OpenAI arms use the same named model through different interfaces; this is a practical configuration comparison, not an isolated causal test of internal architecture. LLM reasoning was disabled and output capped at 32 tokens. Four HTTP workers interleaved all three methods; latency includes network and service conditions.','','## Files','','- [All 520 decisions](All%20520%20decisions.csv): previous and revised predictions, reference, errors, timing and cost.','- [Exact prompt](prompt.json), [frozen plan](PLAN.md), [request hashes](frozen.json).','- [Results](results.json), [verification](verification.json), `traces/` for exact requests and responses.','- [Review findings](Review%20findings.md), `review-notes.jsonl` and `review-agent-*.jsonl` for full review notes.','','Offline verification: `python3 experiments/final-prompt-revision/analyze.py`. The runner resumes completed identical requests without new charges. Do not alter the frozen plan or prompt.','','## Sources','','- [TutorMoments project](https://tutormoments.allen.ai/), [paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [dataset](https://huggingface.co/datasets/allenai/tutormoments-preview). Source revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`.','- [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing).','- [Jev models and pricing](https://docs.typesafe.ai/models).','','## Material Passport','','Public, deidentified source conversations; automated classification and AI-assisted review. No new human participants, human validation, tutoring response generation or learning-outcome measurement.']
 lines += ['', '## Transport recovery', '', f"Failed transport attempts with no model response: {result['failed_transport_attempts']}. These are preserved separately in traces. Their actual billed cost is unknown; a conservative ${result['failed_attempt_cost_reservation_usd']:.6f} reservation brings total budget-accounted cost to ${result['budget_accounted_cost_usd']:.4f}. Only unfinished requests were resumed with identical payloads. Successful-request timing is reported above; retry-inclusive timing and failure overhead are in results.json. See EXECUTION-NOTES.md."]
 (H/'README.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
