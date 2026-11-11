"""Frozen full-520 first-reply expansion. prepare is offline except public prices; run spends money."""
import pathlib,sys,json,csv,hashlib,random,collections,importlib.util,concurrent.futures,urllib.request,argparse,statistics,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('pilot',ROOT/'experiments/routing-pilot/run.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
ARMS=['self_detailed','force_scaffolding','force_rigor'];MODEL='qwen/qwen3-32b';SEED=20261111
# Upper currently advertised GoogleAIStudio price tier protects reservations; actual returned costs are recorded.
p.PRICES['google/gemini-2.5-flash']=(.54e-6,4.5e-6)

def prepare():
 M=p.source();old=list(csv.DictReader(open(ROOT/'experiments/openai-decision-comparison/All 520 decisions.csv')));domains=list(csv.DictReader(open(ROOT/'experiments/final-prompt-revision/All 520 decisions.csv')))
 assert len(M)==len(old)==520
 screen=p.load(ROOT/'experiments/routing-pilot/domain-screen.json');excluded={int(i) for i in screen['non_math']}
 for i,r in enumerate(domains):
  if 'literacy/nonmath'==r['review_domain'] or 'reading comprehension, not mathematics'==r['review_domain'] or r['review_domain'].startswith('non-math tutoring orientation'):excluded.add(i)
 # Explicit mixed-domain review identifies these two reading-comprehension moments (source indices).
 for i,r in enumerate(domains):
  if r['review_domain'].startswith('mixed:305-306') and i in [305,306]:excluded.add(i)
 cases=[]
 for i,m in enumerate(M):
  assert old[i]['source_id']==m['id'] and old[i]['reference']==m['dimension']
  cases.append({'index':i,'source_id':m['id'],'student_id':m['provenance']['conv_id'].split('_')[1],'reference':m['dimension'],'jev':old[i]['jev_decision'],'decisions':old[i]['openai_decisions_decision'],'archived_decisions_seconds':float(old[i]['decisions_seconds']),'archived_decisions_cost_usd':float(old[i]['decisions_cost_usd']),'domain':domains[i]['review_domain'],'known_nonmath':i in excluded})
 assert sum(c['jev']==c['reference'] for c in cases)==376 and sum(c['decisions']==c['reference'] for c in cases)==386
 rng=random.Random(SEED);order=list(range(520));rng.shuffle(order);audit=[];used=set();counts=collections.Counter()
 for i in order:
  c=cases[i]
  if c['student_id'] in used or counts[c['reference']]>=16:continue
  audit.append(i);used.add(c['student_id']);counts[c['reference']]+=1
  if len(audit)==32:break
 assert len(audit)==32
 cfg={'created_utc':None,'seed':SEED,'model':MODEL,'arms':ARMS,'cases':cases,'audit_indices':audit,'policies':p.POLICIES,'self_choice':p.SELF,'common':p.COMMON,'judge':p.JUDGE,'output_cap':384,'temperature':0,'max_spend_usd':8,'full_history':True,'source_sha256':p.sha((ROOT/'data/jev/moments.jsonl').read_bytes()),'archived_router_csv_sha256':p.sha((ROOT/'experiments/openai-decision-comparison/All 520 decisions.csv').read_bytes()),'plan_sha256':p.sha((HERE/'PLAN.md').read_bytes()),'pilot_runner_sha256':p.sha((ROOT/'experiments/routing-pilot/run.py').read_bytes()),'runner_sha256':p.sha(pathlib.Path(__file__).read_bytes()),'n_students':len({c['student_id'] for c in cases})}
 f=HERE/'frozen.json'
 if f.exists():assert p.load(f)==cfg,'Do not change frozen plan'
 else:p.save(f,cfg)
 for model in [MODEL,'google/gemini-2.5-flash','anthropic/claude-sonnet-4.6']:
  d=json.load(urllib.request.urlopen('https://openrouter.ai/api/v1/models/'+model+'/endpoints',timeout=30));p.save(HERE/('endpoints-'+model.split('/')[-1]+'.json'),d)
 inputs=[len(p.enc(p.tutor_messages(m,'self_detailed','rigor'))) for m in M]
 print(json.dumps({'n':520,'students':cfg['n_students'],'known_nonmath':len(excluded),'audit':len(audit),'max_input_bytes':max(inputs),'avg_input_bytes':statistics.mean(inputs),'empirical_estimate_usd':1560*.0005613815+520*.0032566553125+32*.0326581875,'hard_cap':8}))

def payload(m,arm):
 x=p.chat_payload(MODEL,p.tutor_messages(m,arm,'scaffolding'));x['seed']=SEED;return x

def verified():
 cfg=p.load(HERE/'frozen.json');M=p.source();assert cfg['plan_sha256']==p.sha((HERE/'PLAN.md').read_bytes());assert cfg['runner_sha256']==p.sha(pathlib.Path(__file__).read_bytes());assert cfg['pilot_runner_sha256']==p.sha((ROOT/'experiments/routing-pilot/run.py').read_bytes());assert cfg['source_sha256']==p.sha((ROOT/'data/jev/moments.jsonl').read_bytes());assert cfg['policies']==p.POLICIES and cfg['self_choice']==p.SELF and cfg['judge']==p.JUDGE
 return cfg,M

def run(args):
 cfg,M=verified();client=p.Client(HERE/'traces',p.key('OPENROUTER_API_KEY',args.openrouter_env),cap=8)
 jobs=[];kind=args.stage
 if kind=='generate':
  jobs=[(i,a) for i in range(520) for a in ARMS];random.Random(SEED+1).shuffle(jobs)
  if args.limit:jobs=jobs[:args.limit]
  def work(job):
   i,a=job;return client.request('openrouter',payload(M[i],a),f'gen-{i}-{a}')
 else:
  model='google/gemini-2.5-flash' if kind=='judge' else 'anthropic/claude-sonnet-4.6';indices=list(range(520)) if kind=='judge' else cfg['audit_indices'];jobs=indices[:];random.Random(SEED+(2 if kind=='judge' else 3)).shuffle(jobs)
  if args.limit:jobs=jobs[:args.limit]
  def work(i):
   replies={a:p.load(HERE/'traces'/f'gen-{i}-{a}.json')['text'] for a in ARMS}
   request,mapping=p.judge_payload(M[i],replies,model,SEED+i+(10000 if kind=='audit' else 0));request['max_tokens']=1800
   tag=f'{kind}-{i}';r=client.request('openrouter',request,tag);ratings=p.parse_ratings(r['text'],mapping)
   p.save(HERE/'ratings'/(tag+'.json'),{'case_index':i,'model':model,'mapping':mapping,'ratings':ratings,'trace_sha256':p.sha(p.enc(r))});return r
 failures=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  futures={pool.submit(work,j):j for j in jobs}
  for f in concurrent.futures.as_completed(futures):
   try:f.result()
   except Exception as e:
    failures.append({'job':futures[f],'error':str(e)[:500]});print(json.dumps({'failure':failures[-1]}),flush=True)
    if 'Budget guard' in str(e):
     for other in futures:other.cancel()
     break
 p.save(HERE/(kind+'-status.json'),{'jobs':len(jobs),'failed':failures,'spent_usd':client.spent,'completed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
 print(json.dumps({'stage':kind,'jobs':len(jobs),'failures':len(failures),'spent_usd':client.spent}),flush=True)
 if failures:sys.exit(2)

def main():
 a=argparse.ArgumentParser();a.add_argument('command',choices=['prepare','verify','run']);a.add_argument('--stage',choices=['generate','judge','audit'],default='generate');a.add_argument('--workers',type=int,default=6);a.add_argument('--limit',type=int);a.add_argument('--openrouter-env',default='/Users/ee2282/Documents/LemmaEducation_dev/.env.local');args=a.parse_args()
 if args.command=='prepare':prepare()
 elif args.command=='verify':verified();print('Frozen files verified; no API call')
 else:run(args)
if __name__=='__main__':main()
