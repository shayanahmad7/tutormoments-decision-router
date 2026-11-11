"""Build a self-contained, credential-free review bundle from the completed run."""
import pathlib,json,csv,shutil,zipfile,hashlib,importlib.util,re
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[1]
s=importlib.util.spec_from_file_location('run',H/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
cfg,M=r.verified();results=r.p.load(H/'results.json');assert results['status']=='complete'
D=ROOT.parent/'20 - Conference Paper Submission'/'Supporting Materials'/'Technical Experiment';D.mkdir(parents=True,exist_ok=True)
for name in ['PLAN.md','RESULTS.md','frozen.json','results.json','case-results.csv','replies-and-ratings.csv','audit-case-results.csv','audit-replies-and-ratings.csv','strict-math-sensitivity.json','offline-verification.json','run.py']:
 shutil.copy(H/name,D/name)
shutil.copy(ROOT/'data/jev/moments.jsonl',D/'moments.jsonl')
shutil.copy(ROOT/'experiments/jev-all-520-search/best-prompt.json',D/'Archived Jev Prompt.json')
shutil.copy(ROOT/'experiments/openai-decision-comparison/Decision prompt.json',D/'Archived OpenAI Decisions Prompt.json')
shutil.copy(ROOT/'experiments/openai-decision-comparison/All 520 decisions.csv',D/'Archived Router Decisions.csv')
(D/'Prior Prompt Exploration').mkdir(exist_ok=True)
for src,name in [('experiments/jev-all-520-search/All 520 - Six prompt decisions.csv','Jev - All Six Prompts.csv'),('experiments/jev-all-520-search/results.json','Jev - Prompt Search Results.json'),('experiments/final-prompt-revision/All 520 decisions.csv','Later Revision - All Decisions.csv'),('experiments/final-prompt-revision/README.md','Later Revision - Findings.md')]:
 shutil.copy(ROOT/src,D/'Prior Prompt Exploration'/name)
for name in ['EXECUTION-NOTES.md','ANALYSIS-ADDENDUM.md','interruption-ledger.json','Source Dataset Card.md','Dataset Attribution.md','archived-router-input-audit.json','verification.json','parse-repair.json','audit_evidence.py','Evidence Quote Audit.csv','Evidence and Evaluator Audit.md','evidence-and-audit-summary.json','First Reply Results.pdf','First Reply Results.png','paper-results-table.tex','PAPER-RESULTS.md','Illustrative Cases.md','illustrative-cases.json','offline-package-verification.json']:
 shutil.copy(H/name,D/name)
for dirname in ['traces','ratings','failed-attempts']:
 (D/dirname).mkdir(exist_ok=True)
 for f in (H/dirname).glob('*.json'):shutil.copy(f,D/dirname/f.name)
s=importlib.util.spec_from_file_location('search',ROOT/'experiments/jev-all-520-search/run.py');js=importlib.util.module_from_spec(s);s.loader.exec_module(js)
cached={str(i):js.entry('C',i) for i in range(520)}
# Only original route outcomes, timing and costs are needed for offline summary regeneration.
cached={i:{k:v for k,v in x.items() if k in ['response','elapsed_ms','cost_usd','payload_sha256','status']} for i,x in cached.items()};(D/'archived-jev-C-outcomes.json').write_text(json.dumps(cached,ensure_ascii=False)+'\n')
s=(H/'analyze.py').read_text();start=s.index("s=importlib.util.spec_from_file_location('finalrun'");end=s.index('CONDITIONS=',start)
s=s[:start]+'''from types import SimpleNamespace
r=SimpleNamespace(MODEL='qwen/qwen3-32b',SEED=20261111,ARMS=['self_detailed','force_scaffolding','force_rigor'])
def read_json(path): return json.loads(path.read_text())
def save_json(path,value): path.write_text(json.dumps(value,indent=2)+'\\n')
p=SimpleNamespace(load=read_json,save=save_json)
'''+s[end:]
s=s.replace("cfg,M=r.verified();pred=[];raw=[];missing=[];auditraw=[];auditpred=[]", "cfg=read_json(HERE/'frozen.json');M=[json.loads(x) for x in (HERE/'moments.jsonl').read_text().splitlines()];pred=[];raw=[];missing=[];auditraw=[];auditpred=[]")
start=s.index(" spec=importlib.util.spec_from_file_location('jevsearch'");end=s.index(" for c in cfg['cases']:",start)
s=s[:start]+" cached={int(k):v for k,v in read_json(HERE/'archived-jev-C-outcomes.json').items()}\n"+s[end:]
s=s.replace("js.m.answer(cached[i])['choice']", "cached[i]['response']['answers']['next_move']['choice']")
(D/'reproduce_summary.py').write_text(s)
raw=list(csv.DictReader(open(H/'replies-and-ratings.csv')));by={}
for x in raw:by.setdefault(int(x['index']),{})[x['arm']]=x
condition=list(csv.DictReader(open(H/'case-results.csv')));cby={}
for x in condition:cby.setdefault(int(x['index']),{})[x['condition']]=x
wide=[]
for c in cfg['cases']:
 i=c['index'];row={'Moment':i+1,'Assigned condition':c['reference'],'Jev decision':c['jev'],'OpenAI Decisions decision':c['decisions'],'Student ID':c['student_id']}
 for a,name in [('self_detailed','Self-choice'),('force_scaffolding','Scaffold policy'),('force_rigor','Rigor policy')]:
  x=by[i][a];row.update({name+' reply':x['reply'],name+' pass':x['strict_pass'],name+' over-helping':x['overhelp'],name+' reasoning':x['reason']})
 for k,x in cby[i].items():row[k+' pass']=x['strict_pass']
 wide.append(row)
with (D/'All 520 Cases - Replies and Results.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(wide[0]));w.writeheader();w.writerows(wide)
(D/'README.md').write_text('''# TutorMoments technical experiment

Start with RESULTS.md and All 520 Cases - Replies and Results.csv. PLAN.md describes the frozen study. The CSV contains actual generated replies and all selected-policy outcomes; conditions sharing a reply are paired selections, not additional independent samples.

Primary evaluator: Gemini 2.5 Flash; fixed 32-case second-evaluator audit: Claude Sonnet 4.6. These are automated first-reply ratings, not observed learning and not the publisher's multi-turn leaderboard score. On the same 32 cases, Jev minus self-choice changed from -1 passing case with Gemini to +6 with Claude. The audit therefore shows evaluator sensitivity, not confirmation of a routing effect. The source preview was used in prior prompt development. The original labels remain unchanged. The 346-case sensitivity analysis is a strict matched mathematics frame, with additional eligibility requirements for usable first replies across 15 response conditions, conversational cuts and duplicates; the 174 other cases are not all non-mathematical.

Run `python3 reproduce_summary.py` to reconstruct results.json, CSV tables and RESULTS.md offline. It uses Python's standard library, the included full conversation records, saved API outputs, frozen archived route decisions, and recorded ratings. No key or network call is needed. Preserve a copy if you want the supplied summaries unchanged.

`moments.jsonl` is the public released TutorMoments input corpus. It also contains teacher hints and future reference material for review; the saved tutor/judge requests in traces/ show exactly what was actually supplied. Hidden reference material was excluded from deployable tutor inputs. See offline-verification.json.

The original live runner run.py is included for transparency and depends on the project repository's publisher protocol and earlier pilot helper. The self-contained reproduce_summary.py is the offline entry point. Full project code: https://github.com/shayanahmad7/tutormoments-decision-router . Source dataset: https://huggingface.co/datasets/allenai/tutormoments-preview . Publisher code: https://github.com/allenai/tutormoments .
''')
manifest={str(f.relative_to(D)):hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*') if f.is_file() and f.name!='manifest.json'}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for f in D.rglob('*'):
 if f.is_file():assert not re.search(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{40,}|\bAIza[A-Za-z0-9_-]{30,}',f.read_bytes()),f
z=D.parent/'Technical Experiment - Complete Review Package.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
 for f in D.rglob('*'):
  if f.is_file():archive.write(f,str(pathlib.Path(D.name)/f.relative_to(D)))
print(json.dumps({'folder':str(D),'zip':str(z),'zip_bytes':z.stat().st_size,'files':len(manifest)+1}))
