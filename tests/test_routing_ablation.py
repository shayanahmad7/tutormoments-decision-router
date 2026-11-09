import copy, importlib.util, json, pathlib, tempfile, unittest

P=pathlib.Path(__file__).resolve().parents[1]/'experiments/routing-pilot/run.py'
spec=importlib.util.spec_from_file_location('routing_ablation',P);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RoutingAblation(unittest.TestCase):
 def setUp(self):
  self.m={'id':'SECRET_ID','context':[{'turn_number':1,'role':'student','text':'I got 12.'}],
          'dimension':'rigor','student':{'context':'Platform: tutoring_provider_a','reference':'SECRET_FUTURE','trait':{'persona':'SECRET_PERSONA'}},
          'rubric':{'hint':'SECRET_TEACHER','gold':'rigor'},'provenance':{'cut_turn':1}}
 def test_no_labels_or_future_in_generation(self):
  for arm in r.ARMS:
   a=r.tutor_messages(self.m,arm,'rigor');m=copy.deepcopy(self.m);m['dimension']='scaffolding';m['rubric']={};m['student']['reference']='different';m['id']='different'
   self.assertEqual(a,r.tutor_messages(m,arm,'rigor'))
   for s in ['SECRET_ID','SECRET_FUTURE','SECRET_PERSONA','SECRET_TEACHER']:self.assertNotIn(s,json.dumps(a))
 def test_force_policies_do_not_depend_on_router(self):
  for arm in ['force_scaffolding','force_rigor','self_detailed','original']:
   self.assertEqual(r.tutor_messages(self.m,arm,'rigor'),r.tutor_messages(self.m,arm,'scaffolding'))
  self.assertNotEqual(r.tutor_messages(self.m,'jev_label','rigor'),r.tutor_messages(self.m,'jev_label','scaffolding'))
 def test_judge_blinding(self):
  payload,mapping=r.judge_payload(self.m,{a:'reply '+str(i) for i,a in enumerate(r.ARMS)},r.MODELS[0],10)
  s=json.dumps(payload)
  for secret in ['SECRET_ID','SECRET_TEACHER','SECRET_PERSONA','SECRET_FUTURE']+r.ARMS:self.assertNotIn(secret,s)
  self.assertEqual(set(mapping.values()),set(r.ARMS))
 def test_strict_rating_types(self):
  rating={'id':'C1','scaffolding':True,'rigor':False,'overhelp':False,'math_error':False,'uncertain':False,'context_fit':2,'evidence':'text','reason':'reason'}
  self.assertEqual(len(r.parse_ratings(json.dumps({'ratings':[rating]}),['C1'])),1)
  rating['overhelp']='false'
  with self.assertRaises(AssertionError):r.parse_ratings(json.dumps({'ratings':[rating]}),['C1'])
 def test_budget_stops_before_network(self):
  with tempfile.TemporaryDirectory() as d:
   c=r.Client(pathlib.Path(d),cap=0)
   with self.assertRaisesRegex(RuntimeError,'Budget guard'):c.request('openrouter',r.chat_payload(r.MODELS[0],[{'role':'user','content':'hello'}]),'test')
   self.assertEqual(list(pathlib.Path(d).glob('*.json')),[])

if __name__=='__main__':unittest.main()
