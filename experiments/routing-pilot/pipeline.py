"""Deployable route-then-generate path using the pilot's frozen policies.

The paired experiment generates both policies for analysis. This function instead
generates only the policy selected by Jev. It never reads the teacher label.
"""
import importlib.util,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('routing_pilot',Path(__file__).with_name('run.py'))
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)

def route_then_reply(moment,client,model,request_id):
 """Use a unique request_id for a new interaction; exact trace replay is resumable."""
 started=time.perf_counter();jev=pilot.jev_module()
 route=client.request('typesafe',jev.payload_for(moment,'A - Current learner evidence'),request_id+'-route')
 answer=jev.original.parse_answer(route['response'])
 branch='force_'+answer['choice']
 payload=pilot.chat_payload(model,pilot.tutor_messages(moment,branch,answer['choice']))
 reply=client.request('openrouter',payload,request_id+'-reply')
 return {'decision':answer['choice'],'probabilities':answer['probabilities'],'reply':reply['text'],
         'generator_payload_sha256':reply['payload_sha256'],
         'cost_usd':route['cost_usd']+reply['cost_usd'],
         'recorded_serial_first_answer_ms':route['elapsed_ms']+reply['first_answer_ms'],
         'invocation_ms':(time.perf_counter()-started)*1000,
         'timing_note':'invocation_ms includes cache reuse when present; recorded_serial_first_answer_ms sums original API timings. Do not use replay lookup time as live service latency.'}
