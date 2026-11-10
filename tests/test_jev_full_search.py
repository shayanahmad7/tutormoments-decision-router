import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('full_search',ROOT/'experiments/jev-all-520-search/run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class FullSearch(unittest.TestCase):
 def test_all_six_are_binary_decisions_with_no_hidden_metadata(self):
  row=m.m.source()[0];other=copy.deepcopy(row)
  for field in ['id','dimension','rubric','student','provenance']:other[field]='HIDDEN_REFERENCE_CANARY'
  for c in m.specs():
   p=m.payload(row,c)
   self.assertEqual(p,m.payload(other,c))
   self.assertEqual(set(p['questions']),{'next_move'})
   self.assertEqual(set(p['questions']['next_move']['criteria']),{'rigor','scaffolding'})
   self.assertNotIn('HIDDEN_REFERENCE_CANARY',json.dumps(p))
 def test_existing_payloads_are_not_modified(self):
  for row in m.m.source():
   for c in 'ABCDE':self.assertEqual(m.payload(row,c),m.m.payload(row,c))
 def test_new_candidate_preserves_full_history(self):
  for row in m.m.source():self.assertIn(m.m.lines(row['context']),m.payload(row,'F')['state'])
if __name__=='__main__':unittest.main()
