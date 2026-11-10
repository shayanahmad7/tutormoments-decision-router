import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('decision_study',ROOT/'experiments/jev-decision-study/run.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class JevDecisionStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=m.source()
 def test_reference_labels_and_student_separation(self):
  sp=m.split();stu=m.students(self.rows)
  self.assertEqual(len(self.rows),520)
  self.assertEqual(sum(r['dimension']=='rigor' for r in self.rows),260)
  self.assertFalse({stu[i] for i in sp['development_indices']}&{stu[i] for i in sp['evaluation_indices']})
 def test_hidden_metadata_cannot_change_request(self):
  original=self.rows[0];altered=copy.deepcopy(original)
  for key in ['dimension','id','rubric','provenance','student']:altered[key]='SECRET_GOLD_FUTURE_CANARY'
  for candidate in m.specifications():
   self.assertEqual(m.payload(original,candidate),m.payload(altered,candidate))
   self.assertNotIn('SECRET_GOLD_FUTURE_CANARY',json.dumps(m.payload(altered,candidate)))
 def test_baseline_exactly_reproduces_prior_selected_prompt(self):
  for r in self.rows:self.assertEqual(m.payload(r,'A'),m.old.payload_for(r,'A - Current learner evidence'))
 def test_context_window_is_past_only_and_keeps_endpoint(self):
  for r in self.rows:
   w=m.window(r['context'])
   self.assertEqual(w[-1],r['context'][-1]);self.assertLessEqual(len(w),80)
   self.assertGreaterEqual(len(w),min(12,len(r['context'])))
   self.assertEqual(w,r['context'][-len(w):])
 def test_full_history_preserved_for_four_candidates(self):
  for r in self.rows:
   for c in ['A','B','C','E']:self.assertIn(m.lines(r['context']),m.payload(r,c)['state'])
 def test_duplicate_label_conflict_ceiling(self):
  groups=m.groups(self.rows)
  conflicts=[ids for ids in groups.values() if len({self.rows[i]['dimension'] for i in ids})>1]
  self.assertEqual(conflicts,[[69,70],[366,367],[410,411]])
  self.assertEqual(sum(max(m.collections.Counter(self.rows[i]['dimension'] for i in ids).values()) for ids in groups.values()),517)
  for ids in conflicts:
   for c in m.specifications():self.assertEqual(m.payload(self.rows[ids[0]],c),m.payload(self.rows[ids[1]],c))

if __name__=='__main__':unittest.main()
