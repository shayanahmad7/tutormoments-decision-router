import copy, importlib.util, json, pathlib, tempfile, unittest

P=pathlib.Path(__file__).resolve().parents[1]/'experiments/routing-pilot/run.py'
spec=importlib.util.spec_from_file_location('routing_ablation',P);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
spec2=importlib.util.spec_from_file_location('routing_analysis',P.parent/'analyze.py');a=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(a)
spec3=importlib.util.spec_from_file_location('pipeline',P.parent/'pipeline.py');pipe=importlib.util.module_from_spec(spec3);spec3.loader.exec_module(pipe)

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
 def test_derived_policies_use_actual_selected_reply(self):
  self.assertEqual(a.selected_arm('jev_detailed','rigor','scaffolding',.9),'force_rigor')
  self.assertEqual(a.selected_arm('teacher_detailed','rigor','scaffolding',.9),'force_scaffolding')
  self.assertEqual(a.selected_arm('opposite_teacher','rigor','scaffolding',.9),'force_rigor')
  self.assertEqual(a.selected_arm('confidence_fallback','rigor','scaffolding',.79),'self_detailed')
  self.assertEqual(a.selected_arm('confidence_fallback','rigor','scaffolding',.8),'force_rigor')
 def test_paired_test_counts_discordance(self):
  v=a.paired([1,1,1,0],[0,0,0,0],['rigor','rigor','scaffolding','scaffolding'])
  self.assertEqual(v['wins'],3);self.assertEqual(v['losses'],0)
  self.assertEqual(v['mcnemar_exact_p'],.25);self.assertEqual(v['difference_pp'],75)
 def test_streaming_non_thinking_control_is_uniform(self):
  for arm in r.ARMS:
   q=r.chat_payload(r.MODELS[0],r.tutor_messages(self.m,arm,'scaffolding'))
   self.assertTrue(q['messages'][-1]['content'].endswith('/no_think'))
   self.assertEqual(q['max_tokens'],384);self.assertFalse(q['provider']['allow_fallbacks'])
 def test_live_pipeline_uses_jev_choice_not_teacher_label(self):
  class FakeClient:
   def __init__(self):self.calls=[]
   def request(self,service,payload,tag):
    self.calls.append((service,payload))
    if service=='typesafe':return {'response':{'model':'jev-1.14.0','answers':{'next_move':{'type':'choice','choice':'scaffolding','probabilities':{'scaffolding':.9,'rigor':.1},'confidence':.8}}},'cost_usd':.001,'elapsed_ms':100}
    return {'text':'Try one part.','payload_sha256':r.sha(r.enc(payload)),'cost_usd':.002,'first_answer_ms':200}
  client=FakeClient();result=pipe.route_then_reply(self.m,client,r.MODELS[0],'test')
  self.assertEqual(len(client.calls),2);self.assertEqual(result['decision'],'scaffolding')
  self.assertIn(r.POLICIES['scaffolding'],client.calls[1][1]['messages'][0]['content'])
  self.assertNotIn(r.POLICIES['rigor'],client.calls[1][1]['messages'][0]['content'])
  self.assertEqual(result['recorded_serial_first_answer_ms'],300)

if __name__=='__main__':unittest.main()
