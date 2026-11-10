"""Development-only probability threshold selection; no live calls or eval access."""
from pathlib import Path
import datetime,importlib.util,json,statistics
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('decision_calibration_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
GRID=[round(i/20,2) for i in range(2,19)]
def decision(e,t):
 a=m.answer(e)
 if t==.5:return a['choice']
 return 'rigor' if a['probabilities']['rigor']>=t else 'scaffolding'
def metric(rows,entries,ids,t):
 return statistics.mean(sum(decision(entries[i],t)==g for i in ids if rows[i]['dimension']==g)/sum(rows[i]['dimension']==g for i in ids) for g in ['scaffolding','rigor'])
def choose(rows,entries,ids):return min(GRID,key=lambda t:(-metric(rows,entries,ids,t),abs(t-.5),t))
def main():
 cfg=m.checked();sel=m.load(H/'selection.json');rows=m.source();stu=m.students(rows);ids=cfg['development_indices']
 # Deliberately loads only development responses.
 entries={i:m.entry(sel['selected'],i) for i in ids}
 t=choose(rows,entries,ids);folds=[]
 for student in sorted({stu[i] for i in ids}):
  train=[i for i in ids if stu[i]!=student];test=[i for i in ids if stu[i]==student]
  ft=choose(rows,entries,train)
  folds.append({'heldout_student':student,'threshold':ft,'indices':test,'decisions':[decision(entries[i],ft) for i in test]})
 out={'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_candidate':sel['selected'],
 'status':'Secondary amendment after evaluation calls began but before any evaluation scores were calculated or inspected. Raw API choices remain the primary result.',
 'threshold':t,'grid':GRID,'rule':'Maximize development balanced accuracy, then closest to .5, then lower threshold. At .5 use the raw API choice for tie consistency.',
 'development_scores':[{'threshold':v,'balanced_accuracy':metric(rows,entries,ids,v)} for v in GRID],
 'development_oof':folds,'evaluation_outputs_read':0,'additional_api_calls':0,
 'limitation':'Threshold is postprocessing of Jev probabilities, not Jev raw choice. Leave-one-student-out threshold results do not remove earlier prompt-selection exposure.'}
 assert not (H/'threshold-selection.json').exists(),'Do not replace threshold'
 m.save(H/'threshold-selection.json',out)
 print(json.dumps({'threshold':t,'development_balanced_accuracy':metric(rows,entries,ids,t),'raw_balanced_accuracy':metric(rows,entries,ids,.5)}))
if __name__=='__main__':main()
