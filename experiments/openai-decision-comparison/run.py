"""Matched decision-only benchmark. prepare/verify are offline; run makes paid calls."""
from pathlib import Path
import argparse,collections,concurrent.futures,hashlib,json,os,random,threading,time,urllib.request,urllib.error
H=Path(__file__).resolve().parent
ROOT=H.parents[1]
MODEL='gpt-6-luna'
ARMS=('decisions','llm')
SEED=20261110
CAP=2.0

def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text())
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def rows():return [json.loads(l) for l in (ROOT/'data/jev/moments.jsonl').read_text().splitlines()]
def prior(i):return load(ROOT/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json')
def payload(i,arm):
 p=prior(i)['payload'];q=p['questions']['next_move']
 question={'type':'choice','name':'next_teaching_mode','instructions':json.dumps(q['instructions'],ensure_ascii=False),'choices':[{'value':k,'description':json.dumps(v,ensure_ascii=False)} for k,v in q['criteria'].items()]}
 common={'model':MODEL,'prompt_cache_options':{'mode':'explicit'}}
 if arm=='decisions':return {**common,'input':p['state'],'questions':[question]}
 return {**common,'input':p['state']+'\n\nDECISION TASK:\n'+json.dumps(question,ensure_ascii=False)+'\n\nReturn exactly one word: scaffolding or rigor. Do not explain and do not write a tutoring reply.', 'reasoning':{'effort':'none'},'temperature':0,'max_output_tokens':32,'store':False}
def prepare():
 rr=rows();assert len(rr)==520
 assert sha((ROOT/'data/jev/moments.jsonl').read_bytes())=='c447459f80cf6b138512171a015879aaeab09cef7857e9c03655ad64a75c230f'
 for i,r in enumerate(rr):
  state='Here is the conversation so far:\n\n'+'\n'.join(f"Turn {t['turn_number']}. {t['role'].upper()}: {t['text']}" for t in r['context'])
  assert state==prior(i)['payload']['state'],i
  assert r['id'] not in state
 cfg={'model':MODEL,'seed':SEED,'cap_usd':CAP,'records':520,'label_counts':dict(collections.Counter(r['dimension'] for r in rr)),'source_sha256':sha((ROOT/'data/jev/moments.jsonl').read_bytes()),'runner_sha256':sha(Path(__file__).read_bytes()),'plan_sha256':sha((H/'PLAN.md').read_bytes()),'jev_trace_sha256':[sha((ROOT/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json').read_bytes()) for i in range(520)],'payload_hashes':{a:[sha(enc(payload(i,a))) for i in range(520)] for a in ARMS}}
 f=H/'frozen.json'
 if f.exists():assert load(f)==cfg,'Frozen plan or code changed'
 else:save(f,cfg)
 print(json.dumps({'prepared':520,'arms':ARMS,'full_context_verified':True,'budget_usd':CAP}),flush=True)
def secret(path):
 if os.environ.get('OPENAI_API_KEY'):return os.environ['OPENAI_API_KEY']
 for l in Path(path).read_text().splitlines():
  if l.startswith('OPENAI_API_KEY='):return l.split('=',1)[1].strip().strip('"\'')
 raise RuntimeError('No OpenAI key found')
def cost(u,arm):
 n=u['input_tokens'];d=u.get('input_tokens_details',{});c=d.get('cached_tokens',0);w=d.get('cache_write_tokens',0)
 assert n>=c+w
 return ((n-c-w)*.10+c*.01+w*.125+(u.get('output_tokens',0)*.50 if arm=='llm' else 0))/1e6

def parse(response,arm):
 if arm=='decisions':
  ans=next((a for a in response.get('answers',[]) if a.get('name')=='next_teaching_mode'),{})
  return ans.get('choice') if ans.get('type')=='choice' else None
 text=''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text').strip()
 return text.lower() if text.lower() in ['scaffolding','rigor'] and response.get('status')=='completed' else None

def run(args):
 prepare();cfg=load(H/'frozen.json');key=secret(args.env_file)
 lock=threading.Lock();stop=threading.Event();directory=H/'traces';directory.mkdir(exist_ok=True)
 spent=sum(load(p).get('cost_usd',0) for p in directory.glob('*.json'));pending=0
 def one(job):
  nonlocal spent,pending
  arm,i=job;p=directory/f'{arm}-{i:03d}.json';reqbody=payload(i,arm);digest=sha(enc(reqbody));assert digest==cfg['payload_hashes'][arm][i]
  if p.exists():
   r=load(p);assert r['payload_sha256']==digest
   if r.get('status')=='complete':return
   raise RuntimeError('Review saved failure before retry: '+p.name)
  if stop.is_set():return
  # Byte-count bound exceeds likely token count; cache disabled in both arms.
  reserve=(len(enc(reqbody))+2048)*.125/1e6+32*.5/1e6
  with lock:
   if spent+pending+reserve>CAP:stop.set();raise RuntimeError('Budget cap')
   pending+=reserve
  r={'arm':arm,'index':i,'endpoint':'decisions' if arm=='decisions' else 'responses','payload':reqbody,'payload_sha256':digest,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'attempts':[],'status':'pending'}
  start=time.perf_counter();response=None
  try:
   for attempt in range(4):
    if stop.is_set():raise RuntimeError('Stopped after another request failed')
    req=urllib.request.Request('https://api.openai.com/v1/'+r['endpoint'],data=enc(reqbody),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    st=time.perf_counter()
    try:
     with urllib.request.urlopen(req,timeout=90) as conn:
      response=json.load(conn);r['api_request_id']=conn.headers.get('x-request-id');r['attempts'].append({'status':conn.status,'elapsed_ms':(time.perf_counter()-st)*1000})
     break
    except urllib.error.HTTPError as e:
     detail=e.read().decode(errors='replace').replace(key,'[REDACTED]')[:1200]
     r['attempts'].append({'status':e.code,'detail':detail,'elapsed_ms':(time.perf_counter()-st)*1000})
     if e.code not in [429,500,502,503,504] or 'insufficient_quota' in detail or 'credit_balance_exhausted' in detail or attempt==3:raise RuntimeError(f'HTTP {e.code}: {detail}') from None
     time.sleep(min(20,3*(attempt+1)))
   if response is None:raise RuntimeError('No response')
   r.update(response=response,usage=response['usage'],prediction=parse(response,arm),status='complete',cost_usd=cost(response['usage'],arm))
  except Exception as e:
   stop.set();r.update(status='failed',error=str(e).replace(key,'[REDACTED]'),cost_usd=reserve,cost_is_bound=True)
   raise
  finally:
   r['elapsed_ms']=(time.perf_counter()-start)*1000;save(p,r)
   with lock:pending-=reserve;spent+=r.get('cost_usd',reserve)
  return r
 jobs=[(a,i) for i in range(520) for a in ARMS];random.Random(SEED).shuffle(jobs)
 if args.preflight:jobs=[('decisions',0),('llm',0),('decisions',1),('llm',1)]
 start=time.time();done=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=1 if args.preflight else args.workers) as pool:
  fs=[pool.submit(one,j) for j in jobs]
  try:
   for f in concurrent.futures.as_completed(fs):
    f.result();done+=1
    if done%40==0 or args.preflight:print(json.dumps({'completed':done,'planned':len(jobs),'cost_usd':round(spent,6),'seconds':round(time.time()-start,1)}),flush=True)
  except BaseException:
   stop.set()
   for f in fs:f.cancel()
   raise
 print(json.dumps({'finished':True,'completed':done,'cost_usd':spent}),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','run']);ap.add_argument('--preflight',action='store_true');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--env-file',default='/Users/ee2282/Documents/ChatGPT/papi/papi-demo/.env.local');args=ap.parse_args()
 if args.command=='prepare':prepare()
 else:run(args)
