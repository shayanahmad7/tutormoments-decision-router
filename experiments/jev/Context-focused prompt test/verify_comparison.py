"""Independent all-record verification and student-cluster uncertainty summary."""
from pathlib import Path
import collections
import csv
import datetime
import hashlib
import importlib.util
import json
import random
import statistics

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('optimization',P/'optimize_jev.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows,split=m.rows_and_split()
selection=json.loads((P/'Frozen selected prompt.json').read_text())
name=selection['selected_candidate']
old=m.baseline_entries();new=m.entries_in(P/'Full rerun/Responses')
assert set(old)==set(new)==set(range(520))
assert len(list((P/'Full rerun/Responses').glob('*.json')))==520
frozen_time=datetime.datetime.fromisoformat(selection['frozen_at_utc']).timestamp()
reference_files=json.loads((P/'Original output hashes.json').read_text())
assert all(hashlib.sha256((P.parent/f).read_bytes()).hexdigest()==sha for f,sha in reference_files.items())

for name2 in m.PROMPTS:
    for i in split['development_indices']:
        e=json.loads((P/'Development'/name2/'Responses'/f'{i:03d}.json').read_text())
        payload=m.payload_for(rows[i],name2)
        assert e['request_payload']==payload and e['request_sha256']==m.sha(m.canonical(payload))
        m.original.parse_answer(e['response'])

for i,row in enumerate(rows):
    payload=m.payload_for(row,name)
    assert new[i]['request_payload']==payload
    assert new[i]['request_sha256']==m.sha(m.canonical(payload))
    assert payload['state']==m.original.payload_for(row)['state']
    assert set(payload)=={'model','state','questions'}
    assert set(payload['questions'])=={'next_move'}
    assert payload['model']==new[i]['response']['model']=='jev-1.14.0'
    m.original.parse_answer(new[i]['response'])
    if i in set(split['evaluation_indices']):
        assert not new[i].get('reused_from_development')
        assert (P/'Full rerun/Responses'/f'{i:03d}.json').stat().st_mtime>=frozen_time

transcripts=m.original.TRANSCRIPTS
students={r['transcript_id']:r['session']['student_id'] for r in map(json.loads,transcripts.open())}
student_for=lambda i:students[rows[i]['provenance']['conv_id'].split('_')[-1]]
assert not {student_for(i) for i in split['development_indices']} & {student_for(i) for i in split['evaluation_indices']}
assert len({student_for(i) for i in split['evaluation_indices']})==71

correct=lambda e,i:int(e[i]['response']['answers']['next_move']['choice']==rows[i]['dimension'])
result=json.loads((P/'Final comparison.json').read_text())
for section,indices in [('all_520',list(range(520))),('evaluation_382',split['evaluation_indices'])]:
    assert sum(correct(old,i) for i in indices)==result[section]['baseline']['correct']
    assert sum(correct(new,i) for i in indices)==result[section]['optimized']['correct']
    assert sum(correct(new,i)-correct(old,i) for i in indices)==result[section]['paired']['net_correct_change']
csvrows=list(csv.DictReader((P/'All 520 - Original versus optimized.csv').open()))
assert len(csvrows)==520
for i,r in enumerate(csvrows):
    assert int(r['moment_index'])==i and r['reference_label']==rows[i]['dimension']
    assert (r['optimized_correct']=='True')==bool(correct(new,i))

# Resample complete student clusters. Report the moment-weighted accuracy difference.
groups=collections.defaultdict(list)
for i in split['evaluation_indices']:groups[student_for(i)].append(i)
cluster_counts=[(len(ids),sum(correct(new,i)-correct(old,i) for i in ids)) for ids in groups.values()]
rng=random.Random(2026102903);draws=[]
for _ in range(10000):
    sample=rng.choices(cluster_counts,k=len(cluster_counts))
    draws.append(sum(delta for n,delta in sample)/sum(n for n,delta in sample))
draws.sort()
def quantile(values,p):
    k=(len(values)-1)*p;lo=int(k);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(k-lo)
bootstrap={'seed':2026102903,'replicates':10000,'student_clusters':len(groups),
           'evaluation_moments':382,'estimand':'Moment-weighted paired accuracy change, optimized minus original',
           'point_estimate':result['evaluation_382']['paired']['accuracy_change'],
           'percentile_95_interval':[quantile(draws,.025),quantile(draws,.975)],
           'limitation':'Exploratory conditional interval; does not account for prior benchmark exposure, prompt-selection uncertainty or repeated API-sampling variability.'}
m.write(P/'Student-cluster uncertainty.json',bootstrap)

prob_groups=[]
for threshold in [.75,.9,.95]:
    ids=[i for i in range(520) if max(new[i]['response']['answers']['next_move']['probabilities'].values())>=threshold]
    prob_groups.append({'minimum_top_probability':threshold,'n':len(ids),'correct':sum(correct(new,i) for i in ids),
                        'accuracy':sum(correct(new,i) for i in ids)/len(ids) if ids else None})
m.write(P/'Optimized confidence summary.json',prob_groups)

examples={}
for kind,condition in [('improved',lambda i:not correct(old,i) and correct(new,i)),
                       ('harmed',lambda i:correct(old,i) and not correct(new,i))]:
    candidates=[i for i in split['evaluation_indices'] if condition(i)]
    candidates.sort(key=lambda i:-max(new[i]['response']['answers']['next_move']['probabilities'].values()))
    examples[kind]=candidates[:2]
m.write(P/'Evaluation example selection.json',{'rule':'Two highest new top-probability cases per paired outcome; evaluation only','indices':examples})

new_cost=m.cost_so_far()-json.loads((P.parent/'Results.json').read_text())['actual_usage_cost_estimate_usd']
verification={'status':'PASS','full_case_decisions_verified':520,'development_case_decisions_verified':len(m.PROMPTS)*138,
              'new_evaluation_calls':382,'development_predictions_reused_for_selected_prompt':138,
              'full_context_unchanged_checks':520,'returned_model_id':'jev-1.14.0',
              'original_output_hashes_unchanged':len(reference_files),'csv_rows_verified':520,
              'student_overlap_between_subsets':0,'selection_frozen_before_all_new_evaluation_calls':True,
              'source_sha256':m.sha(m.original.SOURCE.read_bytes()),
              'new_round_cost_estimate_usd':new_cost,'combined_cost_estimate_usd':m.cost_so_far(),
              'new_unique_api_calls':len(m.PROMPTS)*138+382,'submitted_materials_edited':False}
assert verification['combined_cost_estimate_usd']<1
m.write(P/'Final verification.json',verification)
print(json.dumps({'verification':verification,'all_520':result['all_520'],'evaluation_382':result['evaluation_382'],
                  'uncertainty':bootstrap,'confidence':prob_groups,'examples':examples},indent=2))
