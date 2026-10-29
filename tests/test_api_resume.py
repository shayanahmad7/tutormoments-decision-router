import hashlib,io,json,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
from tm_router.api import OpenAIClient,QuotaExhausted
class ResumeTests(unittest.TestCase):
 def test_completed_trace_is_reused_without_network_or_repeat_cost(self):
  payload={'model':'model','input':'public example'}
  with tempfile.TemporaryDirectory() as tmp:
   record={'request_id':'old','tag':'case:step','payload_sha256':hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest(),'payload':payload,'response':{'ok':True},'elapsed_ms':30,'attempts':[{'http_status':200}]}
   Path(tmp,'old.json').write_text(json.dumps(record));c=OpenAIClient(tmp,key='unit-test-not-a-key')
   with patch('urllib.request.urlopen',side_effect=AssertionError('Network must not be used')):
    response,trace=c.post('decisions',payload,'case:step')
   self.assertEqual(response,{'ok':True});self.assertTrue(trace['local_resume_reuse'])
 def test_credit_exhaustion_stops_after_first_failure(self):
  error={'error':{'type':'insufficient_quota','code':'credit_balance_exhausted'}}
  exc=urllib.error.HTTPError('https://api.openai.com/v1/decisions',429,'quota',{},io.BytesIO(json.dumps(error).encode()))
  with tempfile.TemporaryDirectory() as tmp:
   c=OpenAIClient(tmp,key='unit-test-not-a-key')
   with patch('urllib.request.urlopen',side_effect=exc) as request:
    with self.assertRaises(QuotaExhausted):c.post('decisions',{},'first')
    with self.assertRaises(QuotaExhausted):c.post('decisions',{},'second')
   self.assertEqual(request.call_count,1)
