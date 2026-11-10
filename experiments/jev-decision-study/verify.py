"""Independent offline coverage, provenance, leakage and arithmetic checks."""
from pathlib import Path
import collections,csv,datetime,hashlib,importlib.util,json,math
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('verify_decisions',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 cfg=m.checked();rows=m.source();students=m.students(rows);sel=m.load(H/'selection.json');selected=sel['selected']
 expected={f'{c}-{i:03d}' for c in cfg['candidates'] for i in cfg['development_indices']}
 expected|={f'{c}-{i:03d}' for c in {'A',selected} for i in cfg['evaluation_indices']}
 expected|={f'R{rep}-{i:03d}' for rep in [2,3] for i in range(520)}
 paths=list((H/'traces').glob('*.json'));assert {p.stem for p in paths}==expected and len(paths)==2494
 assert not {students[i] for i in cfg['development_indices']}&{students[i] for i in cfg['evaluation_indices']}
 frozen_time=datetime.datetime.fromisoformat(sel['frozen_at_utc']).timestamp()
 repeat_plan=m.load(H/'repeat-plan.json')
 assert repeat_plan['primary_results_sha256']==m.sha((H/'primary-results-before-repeats.json').read_bytes())
 assert repeat_plan['runner_sha256']==m.sha((H/'repeat.py').read_bytes())
 expense=0
 for p in paths:
  e=m.load(p);prefix,number=p.stem.split('-');i=int(number);c=selected if prefix.startswith('R') else prefix
  assert e['status']=='complete' and e['tag']==p.stem
  assert e['payload']==m.payload(rows[i],c)
  assert e['payload_sha256']==m.sha(m.enc(e['payload']))==cfg['payload_hashes'][c][i]
  assert set(e['payload'])=={'state','model','questions'}
  assert e['response']['model']=='jev-1.14.0';m.answer(e)
  assert math.isclose(e['cost_usd'],e['usage']['input_tokens']*.042/1e6,abs_tol=1e-10)
  expense+=e['cost_usd']
  if not prefix.startswith('R') and i in cfg['evaluation_indices']:
   ts=datetime.datetime.fromisoformat(e['started_utc'].replace('Z','+00:00')).timestamp()
   assert ts>=int(frozen_time)
 allcsv=list(csv.DictReader((H/'All 520 decisions.csv').open()));assert len(allcsv)==520
 results=m.load(H/'results.json');assert math.isclose(expense,results['cost_usd'],abs_tol=1e-10) and expense<2
 for i,row in enumerate(allcsv):
  assert int(row['moment_index'])==i and row['reference_label']==rows[i]['dimension']
  a=m.answer(m.entry(selected,i));assert row['new_decision']==a['choice']
  assert (row['correct']=='True')==(a['choice']==rows[i]['dimension'])
  assert float(row['p_rigor'])==a['probabilities']['rigor']
  votes=[row['new_decision'],row['repeat_2'],row['repeat_3']]
  assert row['majority_decision']==collections.Counter(votes).most_common(1)[0][0]
  for rep in [2,3]:assert row[f'repeat_{rep}']==m.answer(m.load(H/'traces'/f'R{rep}-{i:03d}.json'))['choice']
 for scope,ids in [('all_520',list(range(520))),('evaluation_382',cfg['evaluation_indices']),('development_138',cfg['development_indices'])]:
  chosen=[allcsv[i] for i in ids]
  assert sum(r['correct']=='True' for r in chosen)==results['scopes'][scope]['selected_new_round']['correct']
  assert sum(r['thresholded_correct']=='True' for r in chosen)==results['secondary_threshold_analysis']['scopes'][scope]['correct']
  if scope!='development_138':
   assert sum(r['majority_decision']==r['reference_label'] for r in chosen)==results['repeatability']['majority'][scope]['correct']
 errors=list(csv.DictReader((H/'Errors for review.csv').open()))
 assert {int(r['moment_index']) for r in errors}=={i for i,r in enumerate(allcsv) if r['correct']=='False'}
 g=m.groups(rows);ceiling=sum(max(collections.Counter(rows[i]['dimension'] for i in ids).values()) for ids in g.values())
 assert ceiling==517 and len(g)==491
 conflicts=[ids for ids in g.values() if len({rows[i]['dimension'] for i in ids})>1]
 assert conflicts==[[69,70],[366,367],[410,411]]
 for ids in conflicts:
  for c in cfg['candidates']:assert len({cfg['payload_hashes'][c][i] for i in ids})==1
 manifest=H/'archive-manifest.json'
 if manifest.exists():
  for name,digest in m.load(manifest)['files'].items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==digest,name
 status={'status':'PASS','unique_successful_calls':len(paths),'full_record_decisions_each_run':520,'raw_new_prompt_errors':len(errors),'student_overlap':0,'cost_usd':round(expense,6),'identical_input_conflict_pairs':3,'gold_labels_changed':0,'network_calls':0}
 m.save(H/'verification.json',status);print(json.dumps(status,indent=2))
if __name__=='__main__':main()
