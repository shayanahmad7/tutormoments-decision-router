"""Independently verify every candidate on all 520 records. Offline only."""
from pathlib import Path
import collections,csv,hashlib,importlib.util,json,math
from fractions import Fraction
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('full_verify_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 cfg=m.checked();rows=m.m.source();result=m.m.load(H/'results.json');csvrows=list(csv.DictReader((H/'All 520 - Six prompt decisions.csv').open()))
 assert len(csvrows)==520 and [int(r['moment_index']) for r in csvrows]==list(range(520))
 assert collections.Counter(r['dimension'] for r in rows)=={'scaffolding':260,'rigor':260}
 found={};cost=0;choices={};probs={}
 expected_new={f'{c}-{i:03d}' for c in m.specs() for i in range(520) if f'{c}-{i:03d}' not in cfg['reused']}
 assert {p.stem for p in (H/'traces').glob('*.json')}==expected_new and len(expected_new)==1666
 for c in m.specs():
  choices[c]={};probs[c]={};count=0
  for i,row in enumerate(rows):
   e=m.entry(c,i);assert e['status']=='complete'
   assert e['payload']==m.payload(row,c)
   assert e['payload_sha256']==m.m.sha(m.m.enc(e['payload']))==cfg['payload_hashes'][c][i]
   a=m.m.answer(e);assert e['response']['model']=='jev-1.14.0'
   assert e['payload']['questions']['next_move']['type']=='choice'
   assert csvrows[i][c+'_decision']==a['choice'] and float(csvrows[i][c+'_p_rigor'])==a['probabilities']['rigor']
   assert csvrows[i]['reference_label']==row['dimension']
   choices[c][i]=a['choice'];probs[c][i]=a['probabilities']['rigor'];count+=1
   if f'{c}-{i:03d}' in expected_new:
    expected=e['usage']['input_tokens']*.042/1e6;assert math.isclose(e['cost_usd'],expected,abs_tol=1e-10);cost+=expected
  assert count==520 and result['raw'][c]['n']==520
  assert sum(choices[c][i]==rows[i]['dimension'] for i in range(520))==result['raw'][c]['correct'];found[c]=count
 probs['mean']={i:float(sum((Fraction(str(probs[c][i])) for c in m.specs()),Fraction(0))/6) for i in range(520)}
 choices['mean']={i:'rigor' if p>.5 else 'scaffolding' if p<.5 else choices['A'][i] for i,p in probs['mean'].items()}
 for c,curve in result['threshold_curves'].items():
  assert [v['threshold'] for v in curve]==cfg['threshold_grid']
  for point in curve:
   t=point['threshold'];got={i:choices[c][i] if t==.5 else 'rigor' if p>=t else 'scaffolding' for i,p in probs[c].items()}
   assert sum(got[i]==rows[i]['dimension'] for i in range(520))==point['correct']
  best=min(curve,key=lambda v:(-v['correct'],abs(v['threshold']-.5),v['threshold']))
  assert result['threshold_fitted'][c]['correct']==best['correct'] and result['threshold_fitted'][c]['threshold']==best['threshold']
 raw=result['selection']['best_raw']['candidate'];tuned=result['selection']['best_tuned']['candidate'];threshold=result['best_threshold']
 assert sum(r['best_raw_correct']=='True' for r in csvrows)==result['raw'][raw]['correct']
 assert sum(r['best_fitted_correct']=='True' for r in csvrows)==result['threshold_fitted'][tuned]['correct']
 for i,row in enumerate(csvrows):
  assert row['best_raw_decision']==choices[raw][i]
  fitted=choices[tuned][i] if threshold==.5 else 'rigor' if probs[tuned][i]>=threshold else 'scaffolding'
  assert row['best_fitted_decision']==fitted
 assert math.isclose(cost,result['new_cost_usd'],abs_tol=1e-9) and cost<1.5
 assert result['candidate_record_decisions']==3120 and result['reused_calls']==1454 and result['new_calls']==1666
 manifest=H/'archive-manifest.json'
 if manifest.exists():
  for file,digest in m.m.load(manifest)['files'].items():assert hashlib.sha256((H/file).read_bytes()).hexdigest()==digest,file
 out={'status':'PASS','records_verified_per_prompt':found,'candidate_record_decisions':3120,'new_calls':1666,'reused_calls':1454,'new_cost_usd':round(cost,6),'tutor_or_judge_calls':0,'network_calls':0}
 m.m.save(H/'verification.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
