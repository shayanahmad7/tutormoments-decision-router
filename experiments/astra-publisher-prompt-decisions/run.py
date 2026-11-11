"""Astra decision-only test with minimally adapted publisher prompt."""
from pathlib import Path
import argparse,collections,sys,concurrent.futures,importlib.util,json,random,threading,time,urllib.request,urllib.error
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
spec=importlib.util.spec_from_file_location('base',ROOT/'experiments/final-prompt-revision/run.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
load=base.load;save=base.save;enc=base.enc;sha=base.sha
sys.path.insert(0,str(ROOT/'src'))
from tm_router import publisher_protocol as protocol
SEED=20261110;CAP=2.5;MODEL='gpt-6-astra';MAX_OUTPUT=4096
def select():
 rows=base.rows();tt=[json.loads(l) for l in (ROOT/'data/jev/transcripts.jsonl').read_text().splitlines()];sm={r['transcript_id']:r['session']['student_id'] for r in tt}
 ids=list(range(520));random.Random(SEED).shuffle(ids);selected=[];used=set();counts=collections.Counter()
 for i in ids:
  student=sm[rows[i]['provenance']['conv_id'].split('_')[-1]];label=rows[i]['dimension']
  if student not in used and counts[label]<10:selected.append(i);used.add(student);counts[label]+=1
  if len(selected)==20:break
 assert len(selected)==len(used)==20 and counts=={'scaffolding':10,'rigor':10}
 return selected
def decision_input(row):
 source=(ROOT/'src/tm_router/publisher_prompts/tutor/scaffolding_rigor.txt').read_text()
 core=source.split('### Sending multiple messages')[0].rstrip()
 assert core.count('{student_context}')==1
 rendered=core.replace('{student_context}',row['student']['context'])
 return rendered+'\n\nHere is the conversation so far:\n\n'+protocol._format_transcript_prefix(row['context'])+'\n\n'+(H/'decision-instruction.txt').read_text().strip()
def payload(i):
 old=load(ROOT/'experiments/astra-decision-pilot/traces'/f'astra-{i:03d}.json')['payload']
 return {**old,'input':decision_input(base.rows()[i])}
def prepare():
 ids=select();assert sha((ROOT/'data/jev/moments.jsonl').read_bytes())==base.SOURCE_SHA
 old=load(ROOT/'experiments/astra-decision-pilot/frozen.json');assert ids==old['indices']
 cfg={'indices':ids,'n':20,'model':MODEL,'reasoning':'high','max_output_tokens':MAX_OUTPUT,'cap_usd':CAP,'source_sha256':base.SOURCE_SHA,'runner_sha256':sha(Path(__file__).read_bytes()),'base_runner_sha256':sha((ROOT/'experiments/final-prompt-revision/run.py').read_bytes()),'publisher_prompt_sha256':sha((ROOT/'src/tm_router/publisher_prompts/tutor/scaffolding_rigor.txt').read_bytes()),'decision_instruction_sha256':sha((H/'decision-instruction.txt').read_bytes()),'plan_sha256':sha((H/'PLAN.md').read_bytes()),'request_hashes':{str(i):sha(enc(payload(i))) for i in ids},'baseline_hashes':{str(i):sha((ROOT/'experiments/astra-decision-pilot/traces'/f'astra-{i:03d}.json').read_bytes()) for i in ids}}
 p=H/'frozen.json'
 if p.exists():assert load(p)==cfg,'Frozen configuration changed'
 else:save(p,cfg)
 print(json.dumps({'prepared':20,'indices':ids,'model':MODEL,'reasoning':'high','cap_usd':CAP}),flush=True)
 return cfg
def cost(u):
 d=u.get('input_tokens_details',{});c=d.get('cached_tokens',0);w=d.get('cache_write_tokens',0);n=u['input_tokens'];assert n>=c+w
 return ((n-c-w)*10+c*1+w*12.5+u['output_tokens']*50)/1e6
def run(args):
 cfg=prepare();key=base.secret('OPENAI_API_KEY','/Users/ee2282/Documents/ChatGPT/papi/papi-demo/.env.local');directory=H/'traces';directory.mkdir(exist_ok=True)
 spent=sum(load(p)['cost_usd'] for p in directory.glob('*.json'));pending=0;lock=threading.Lock();stop=threading.Event()
 def one(i):
  nonlocal spent,pending
  body=payload(i);digest=sha(enc(body));assert digest==cfg['request_hashes'][str(i)];p=directory/f'astra-{i:03d}.json'
  if p.exists():
   r=load(p);assert r['payload_sha256']==digest and r['status']=='complete';return
  if stop.is_set():return
  reserve=(len(enc(body))+2048)*12.5/1e6+MAX_OUTPUT*50/1e6
  with lock:
   if spent+pending+reserve>CAP:stop.set();raise RuntimeError('Budget reservation cap reached')
   pending+=reserve
  r={'index':i,'payload':body,'payload_sha256':digest,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'pending'};start=time.perf_counter()
  try:
   req=urllib.request.Request('https://api.openai.com/v1/responses',data=enc(body),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
   try:
    with urllib.request.urlopen(req,timeout=180) as conn:response=json.load(conn);r['http_status']=conn.status;r['api_request_id']=conn.headers.get('x-request-id')
   except urllib.error.HTTPError as e:raise RuntimeError('HTTP '+str(e.code)+': '+e.read().decode(errors='replace').replace(key,'[REDACTED]')[:1000]) from None
   r.update(response=response,usage=response['usage'],prediction=base.parse(response,'llm'),status='complete',cost_usd=cost(response['usage']))
  except Exception as e:
   r.update(status='failed',error=str(e).replace(key,'[REDACTED]'),cost_usd=reserve,cost_is_bound=True);stop.set();raise
  finally:
   r['elapsed_ms']=(time.perf_counter()-start)*1000;save(p,r)
   with lock:pending-=reserve;spent+=r['cost_usd']
  print(json.dumps({'index':i,'status':r['status'],'valid_output':r.get('prediction') in base.LABELS,'reasoning_tokens':r.get('usage',{}).get('output_tokens_details',{}).get('reasoning_tokens'),'total_cost_usd':round(spent,5)}),flush=True)
 ids=cfg['indices'][:1] if args.preflight else cfg['indices']
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  fs=[pool.submit(one,i) for i in ids]
  try:
   for f in concurrent.futures.as_completed(fs):f.result()
  except BaseException:
   stop.set()
   for f in fs:f.cancel()
   raise
 print(json.dumps({'complete':len(ids),'cost_usd':spent}),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','run']);ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
 if args.command=='prepare':prepare()
 else:run(args)
