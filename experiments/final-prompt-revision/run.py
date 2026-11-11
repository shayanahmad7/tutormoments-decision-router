"""One frozen, decision-only pass per provider. prepare is offline; run is paid."""
from pathlib import Path
import argparse, collections, concurrent.futures, hashlib, json, os, random, threading, time, urllib.request, urllib.error

H=Path(__file__).resolve().parent
ROOT=H.parents[1]
ARMS=('jev','decisions','llm')
MODELS={'jev':'jev-1.14.0','decisions':'gpt-6-luna','llm':'gpt-6-luna'}
ENDPOINTS={'jev':'https://api.typesafe.ai/v1/systemone','decisions':'https://api.openai.com/v1/decisions','llm':'https://api.openai.com/v1/responses'}
SEED=20261111
CAP=2.0
LABELS=('scaffolding','rigor')
SOURCE_SHA='c447459f80cf6b138512171a015879aaeab09cef7857e9c03655ad64a75c230f'

def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def load(p):return json.loads(p.read_text())
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def rows():return [json.loads(l) for l in (ROOT/'data/jev/moments.jsonl').read_text().splitlines()]
def state(row):return 'Here is the conversation so far:\n\n'+'\n'.join(f"Turn {t['turn_number']}. {t['role'].upper()}: {t['text']}" for t in row['context'])
def payload(row,arm):
 q=load(H/'prompt.json');s=state(row)
 if arm=='jev':return {'model':MODELS[arm],'state':s,'questions':{'next_move':{'type':'choice',**q}}}
 question={'type':'choice','name':'next_teaching_mode','instructions':q['instructions'],'choices':[{'value':k,'description':v} for k,v in q['criteria'].items()]}
 common={'model':MODELS[arm],'prompt_cache_options':{'mode':'explicit'}}
 if arm=='decisions':return {**common,'input':s,'questions':[question]}
 return {**common,'input':s+'\n\nDECISION TASK:\n'+json.dumps(question,ensure_ascii=False)+'\n\nReturn exactly one word: scaffolding or rigor. Do not explain and do not write a tutoring reply.', 'reasoning':{'effort':'none'},'temperature':0,'max_output_tokens':32,'store':False}

def review_files():return sorted([H/'review-notes.jsonl',*H.glob('review-agent-*.jsonl')])
def review_audit():
 inventory=load(H/'conversation-inventory.json');notes=[json.loads(l) for p in review_files() for l in p.read_text().splitlines() if l.strip()]
 assert len(notes)==112 and sorted(n['group'] for n in notes)==list(range(112)),'Full review not yet completed'
 for n in notes:assert n['indices']==inventory[n['group']]['indices'],n['group']
 assert sorted(i for n in notes for i in n['indices'])==list(range(520))
 return {'conversations':112,'moments':520,'files':{p.name:sha(p.read_bytes()) for p in review_files()},'review_type':'AI-assisted full pre-cut transcript review; not human adjudication'}
def prepare():
 rr=rows();assert len(rr)==520
 assert sha((ROOT/'data/jev/moments.jsonl').read_bytes())==SOURCE_SHA
 review=review_audit()
 for i,r in enumerate(rr):
  assert all(set(t)=={'turn_number','role','text'} for t in r['context'])
  prior=load(ROOT/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json')
  assert state(r)==prior['payload']['state'],i
 cfg={'models':MODELS,'seed':SEED,'cap_usd':CAP,'records':520,'label_counts':dict(collections.Counter(r['dimension'] for r in rr)), 'source_sha256':SOURCE_SHA,'runner_sha256':sha(Path(__file__).read_bytes()),'plan_sha256':sha((H/'PLAN.md').read_bytes()),'prompt_sha256':sha((H/'prompt.json').read_bytes()),'review':review,'payload_hashes':{a:[sha(enc(payload(r,a))) for r in rr] for a in ARMS}}
 f=H/'frozen.json'
 if f.exists():assert load(f)==cfg,'Frozen review, plan, code or prompt changed'
 else:save(f,cfg)
 print(json.dumps({'prepared':520,'arms':ARMS,'review':review,'budget_usd':CAP}),flush=True)

def secret(name,path):
 if os.environ.get(name):return os.environ[name]
 for line in Path(path).read_text().splitlines():
  if line.startswith(name+'='):return line.split('=',1)[1].strip().strip('"\'')
 raise RuntimeError('No '+name+' found')
def cost(u,arm):
 n=u['input_tokens']
 if arm=='jev':return n*.042/1e6
 d=u.get('input_tokens_details',{});c=d.get('cached_tokens',0);w=d.get('cache_write_tokens',0);assert n>=c+w
 return ((n-c-w)*.10+c*.01+w*.125+(u.get('output_tokens',0)*.50 if arm=='llm' else 0))/1e6
def parse(response,arm):
 if arm=='jev':return response.get('answers',{}).get('next_move',{}).get('choice')
 if arm=='decisions':
  ans=next((a for a in response.get('answers',[]) if a.get('name')=='next_teaching_mode'),{})
  return ans.get('choice') if ans.get('type')=='choice' else None
 text=''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text').strip().lower()
 return text if text in LABELS and response.get('status')=='completed' else None

def run(args):
 prepare();cfg=load(H/'frozen.json');rr=rows()
 keys={'jev':secret('TYPESAFE_API_KEY',ROOT.parent/'19 - Jev Decision Classification/.env'),'openai':secret('OPENAI_API_KEY',args.env_file)}
 lock=threading.Lock();stop=threading.Event();directory=H/'traces';directory.mkdir(exist_ok=True)
 spent=sum(load(p).get('cost_usd',0) for p in directory.glob('*.json'));pending=0
 def one(job):
  nonlocal spent,pending
  arm,i=job;p=directory/f'{arm}-{i:03d}.json';reqbody=payload(rr[i],arm);digest=sha(enc(reqbody));assert digest==cfg['payload_hashes'][arm][i]
  if p.exists():
   old=load(p);assert old['payload_sha256']==digest
   if old.get('status')=='complete':return
   raise RuntimeError('Review saved failure before retry: '+p.name)
  if stop.is_set():return
  reserve=(len(enc(reqbody))+2048)*(.042 if arm=='jev' else .125)/1e6+32*.5/1e6
  with lock:
   if spent+pending+reserve>CAP:stop.set();raise RuntimeError('Budget cap')
   pending+=reserve
  key=keys['jev' if arm=='jev' else 'openai']
  r={'arm':arm,'index':i,'endpoint':ENDPOINTS[arm],'payload':reqbody,'payload_sha256':digest,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'attempts':[],'status':'pending'}
  start=time.perf_counter();response=None
  try:
   # Completed model outputs are never rerun. Transport errors stop the run;
   # no hidden retries or replacement predictions in this final experiment.
   req=urllib.request.Request(ENDPOINTS[arm],data=enc(reqbody),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
   try:
    with urllib.request.urlopen(req,timeout=90) as conn:
     response=json.load(conn);r['api_request_id']=conn.headers.get('x-request-id');r['attempts'].append({'status':conn.status,'elapsed_ms':(time.perf_counter()-start)*1000})
   except urllib.error.HTTPError as e:
    detail=e.read().decode(errors='replace').replace(key,'[REDACTED]')[:1200]
    r['attempts'].append({'status':e.code,'detail':detail,'elapsed_ms':(time.perf_counter()-start)*1000})
    raise RuntimeError(f'HTTP {e.code}: {detail}') from None
   r.update(response=response,usage=response['usage'],prediction=parse(response,arm),status='complete',cost_usd=cost(response['usage'],arm))
  except Exception as e:
   stop.set();r.update(status='failed',error=str(e).replace(key,'[REDACTED]'),cost_usd=reserve,cost_is_bound=True)
   raise
  finally:
   r['elapsed_ms']=(time.perf_counter()-start)*1000;save(p,r)
   with lock:pending-=reserve;spent+=r.get('cost_usd',reserve)
  return r
 jobs=[(a,i) for i in range(520) for a in ARMS];random.Random(SEED).shuffle(jobs)
 if args.preflight:jobs=[(a,i) for i in range(2) for a in ARMS]
 start=time.time();done=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=1 if args.preflight else args.workers) as pool:
  fs=[pool.submit(one,j) for j in jobs]
  try:
   for f in concurrent.futures.as_completed(fs):
    f.result();done+=1
    if done%60==0 or args.preflight:print(json.dumps({'completed_or_reused':done,'planned':len(jobs),'cost_usd':round(spent,6),'seconds':round(time.time()-start,1)}),flush=True)
  except BaseException:
   stop.set()
   for f in fs:f.cancel()
   raise
 print(json.dumps({'finished':True,'completed_or_reused':done,'cost_usd':spent}),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','run']);ap.add_argument('--preflight',action='store_true');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--env-file',default='/Users/ee2282/Documents/ChatGPT/papi/papi-demo/.env.local');args=ap.parse_args()
 if args.command=='prepare':prepare()
 else:run(args)
