"""Four-case original-prompt replay with explicit 8192-token safety cap."""
from pathlib import Path
import argparse,ast,concurrent.futures,hashlib,importlib.util,json,re,sys,threading,time,urllib.request,urllib.error
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'src'))
from tm_router import publisher_protocol as p
spec=importlib.util.spec_from_file_location('base',ROOT/'experiments/final-prompt-revision/run.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
load=base.load;save=base.save;sha=base.sha;enc=base.enc
SOURCE=ROOT/'experiments/astra-publisher-replay'
CAP=3.;LOCK=threading.Lock();STOP=threading.Event();RESERVED=0.
JSON_SYSTEM='You must respond with valid JSON only. Do not include markdown code fences, explanations, or any text outside the JSON object.'
def source_helpers():
 ns={}
 tree=ast.parse((SOURCE/'source/client.py').read_text())
 names={'_openai_user_content','_cache_breakpoint_offset','_mark_cache_breakpoint','_openai_text_part'}
 nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
 assert len(nodes)==4
 exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+nodes,type_ignores=[])),'publisher_client_functions','exec'),ns)
 return ns
WIRE=source_helpers()
def parts(m,role,g):
 s=m['student']
 return p._build_role_prompt(role,p._format_transcript_prefix(m['context']),p._extra(g),s['context'],tutor_mode='scaffolding_rigor',reference_transcript=s['reference'],persona=s['trait']['persona'])
def tutor_payload(m,g):
 head,tail=parts(m,'TUTOR',g)
 content=WIRE['_openai_user_content'](tail,head,None,explicit_cache=True)
 assert ''.join(b['text'] for b in content)==p.tutor_messages(m,'scaffolding_rigor',g)[0]['content']
 return {'model':'gpt-6-astra','messages':[{'role':'user','content':content}],'max_completion_tokens':128000 if m['id']==base.rows()[309]['id'] and not g else 8192,'reasoning_effort':'high','prompt_cache_options':{'mode':'explicit'}}
def claude_payload(prompt,judge=False,head=None):
 content=prompt if head is None else [{'type':'text','text':head,'cache_control':{'type':'ephemeral'}},{'type':'text','text':prompt}]
 b={'model':'anthropic/claude-opus-4.6','max_tokens':8192,'messages':[{'role':'user','content':content}],'thinking':{'type':'adaptive' if judge else 'disabled'},'provider':{'only':['Anthropic'],'allow_fallbacks':False,'require_parameters':True}}
 if judge:b['system']=JSON_SYSTEM
 return b
def prepare():
 src=ROOT/'data/jev/moments.jsonl';old=load(ROOT/'experiments/astra-decision-pilot/frozen.json');rows=base.rows()
 counts={'scaffolding':0,'rigor':0};ids=[]
 for i in old['indices']:
  if counts[rows[i]['dimension']]<2:ids.append(i);counts[rows[i]['dimension']]+=1
 old={**old,'indices':ids}
 assert ids==[309,250,325,376]
 assert sha(src.read_bytes())==old['source_sha256']
 cfg={'indices':old['indices'],'source_sha256':old['source_sha256'],'cases':[{'moment_index':i,'moment_id':rows[i]['id']} for i in old['indices']],'budget_usd':CAP,'run_sha256':sha(Path(__file__).read_bytes()),'plan_sha256':sha((H/'PLAN.md').read_bytes()),'protocol_sha256':sha(Path(p.__file__).read_bytes()),'source_hashes':{f.name:sha(f.read_bytes()) for f in (SOURCE/'source').glob('*')},'initial_tutor_payload_hashes':{str(i):sha(enc(tutor_payload(rows[i],[]))) for i in old['indices']}}
 if (H/'frozen.json').exists():assert load(H/'frozen.json')==cfg
 else:save(H/'frozen.json',cfg)
 return cfg
def spent():return sum(load(f)['cost_usd'] for f in (H/'traces').glob('*.json'))
def call(payload,tag,kind):
 global RESERVED
 path=H/'traces'/(tag+'.json');digest=sha(enc(payload))
 if path.exists():
  t=load(path);assert t['payload_sha256']==digest and t['status']=='complete';return t['text']
 is_tutor=kind=='tutor';key=base.secret('OPENAI_API_KEY','/Users/ee2282/Documents/ChatGPT/papi/papi-demo/.env.local') if is_tutor else base.secret('OPENROUTER_API_KEY','/Users/ee2282/Documents/LemmaEducation_dev/.env.local')
 url='https://api.openai.com/v1/chat/completions' if is_tutor else 'https://openrouter.ai/api/v1/messages'
 reserve=(len(enc(payload))+2048)*(12.5 if is_tutor else 6.25)/1e6+payload.get('max_tokens',payload.get('max_completion_tokens'))*(50 if is_tutor else 25)/1e6
 with LOCK:
  if STOP.is_set():raise RuntimeError('Stopped')
  if spent()+RESERVED+reserve>CAP:STOP.set();raise RuntimeError('Budget reservation ceiling reached')
  RESERVED+=reserve
 trace={'tag':tag,'kind':kind,'payload':payload,'payload_sha256':digest,'endpoint':url,'status':'pending','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};start=time.perf_counter()
 try:
  request=urllib.request.Request(url,data=enc(payload),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','X-OpenRouter-Metadata':'enabled'})
  try:
   with urllib.request.urlopen(request,timeout=240) as c:d=json.load(c)
  except urllib.error.HTTPError as e:raise RuntimeError('HTTP '+str(e.code)+': '+e.read().decode(errors='replace').replace(key,'[REDACTED]')[:700]) from None
  trace['response']=d;u=d['usage'];trace['usage']=u
  if is_tutor:
   ch=d['choices'][0];assert ch['finish_reason']=='stop',ch['finish_reason'];text=ch['message']['content'];details=u.get('prompt_tokens_details',{});cached=details.get('cached_tokens',0);write=details.get('cache_write_tokens',0)
   cost=((u['prompt_tokens']-cached-write)*10+cached+write*12.5+u['completion_tokens']*50)/1e6
  else:
   assert d['stop_reason'] in ['end_turn','stop_sequence'],d.get('stop_reason')
   assert d.get('provider') in [None,'Anthropic'],d.get('provider')
   text=''.join(x['text'] for x in d['content'] if x.get('type')=='text')
   cost=(u['input_tokens']*5+u.get('cache_read_input_tokens',0)*.5+u.get('cache_creation_input_tokens',0)*6.25+u['output_tokens']*25)/1e6
   metadata=d.get('openrouter_metadata',{});trace['reported_metadata']=metadata
  assert isinstance(text,str) and text.strip()
  trace.update(text=text,status='complete',cost_usd=cost)
 except Exception as e:
  trace.update(status='failed',error=str(e).replace(key,'[REDACTED]'),cost_usd=reserve,cost_is_upper_bound=True);STOP.set();raise
 finally:
  trace['elapsed_ms']=(time.perf_counter()-start)*1000;save(path,trace)
  with LOCK:RESERVED-=reserve
 return text

def clean_json(s):
 s=s.strip()
 if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
 json.loads(s)
 return s

def run_case(i):
 m=base.rows()[i];path=H/'cases'/f'{i:03d}.json';st=load(path) if path.exists() else {'index':i,'moment_id':m['id'],'dimension':m['dimension'],'generated_turns':[],'next_step':0,'status':'pending'}
 if st['status']=='scored':return
 g=st['generated_turns']
 for step in range(st['next_step'],5):
  if step%2==0:
   text=call(tutor_payload(m,g),f'{i:03d}-tutor-{step}','tutor');text,end,change=p.parse_tutor_output(text);pieces=p.split_messages(text)
   if not pieces and not(end or change):pieces=['...']
   g=p.append_generated_turns(m,g,'TUTOR',pieces)
  else:
   head,tail=parts(m,'STUDENT',g);text=call(claude_payload(tail,head=head),f'{i:03d}-student-{step}','student');g=p.append_generated_turns(m,g,'STUDENT',p.split_messages(text) or ['...']);end=change=False
  st.update(generated_turns=g,next_step=step+1,status='replayed' if step==4 or end or change else 'running');save(path,st)
  if end or change:st['stop_reason']='END' if end else 'PROBLEM_CHANGE';save(path,st);break
 if not g:raise RuntimeError('No generated turns; manual source-path check required')
 annotation=p.parse_annotation(clean_json(call(claude_payload(p.scorer_annotate_prompt(m,g),True),f'{i:03d}-judge-annotate','judge')))
 facets={}
 for kind in ['action','overscaffold']:
  prompt=p.scorer_decompose_prompt(annotation,kind)
  if prompt:
   raw=clean_json(call(claude_payload(prompt,True),f'{i:03d}-judge-{kind}','judge'));facets[kind]=p.parse_facets(raw)
  else:facets[kind]=[]
 prompt=p.scorer_structure_prompt(facets['action'])
 label=p.parse_action_label(clean_json(call(claude_payload(prompt,True),f'{i:03d}-judge-structure','judge'))) if prompt else 'neither'
 assert label!='unclear'
 st.update(status='scored',annotation={**annotation,'action_label':label,'action_decomposed':facets['action'],'overscaffold_decomposed':facets['overscaffold']},pass_publisher_rule=label in [m['dimension'],'both'] and not facets['overscaffold']);save(path,st)
 print(json.dumps({'case':i,'status':'scored','action':label,'pass':st['pass_publisher_rule'],'cost_so_far':round(spent(),4)}),flush=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','run']);ap.add_argument('--preflight',action='store_true');args=ap.parse_args();cfg=prepare()
 if args.command=='prepare':print(json.dumps({'prepared':len(cfg['indices'])}));return
 (H/'traces').mkdir(exist_ok=True);(H/'cases').mkdir(exist_ok=True)
 # Serial preserves worst-case per-call budget reserve without doubling it.
 ids=cfg['indices'][:1] if args.preflight else cfg['indices']
 for i in ids:run_case(i)
 print(json.dumps({'done':len(ids),'cost_usd':spent()}),flush=True)
if __name__=='__main__':main()
