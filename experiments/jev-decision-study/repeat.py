"""Post-primary robustness check: two unchanged repeats, never best-of-run."""
from pathlib import Path
import concurrent.futures,datetime,importlib.util,json,random
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('repeat_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 cfg=m.checked();selected=m.load(H/'selection.json')['selected'];rows=m.source()
 f=H/'repeat-plan.json'
 spec={'candidate':selected,'repeats':[2,3],'indices':list(range(520)),'changes_to_prompt_or_model':False,
 'primary_results_sha256':m.sha((H/'results.json').read_bytes()),
 'reason':'After primary results, check repeatability because the fresh old prompt differed from its archived run on 25 decisions. No prompt retuning.',
 'analysis':'Report all three runs, per-case agreement, majority of three raw decisions and arithmetic mean probability with fixed .5 cutoff. Exact .5 ties use first-run choice. Never select the best replicate.',
 'status':'Exploratory post-primary robustness check, not an independent confirmation of a newly selected prompt.',
 'runner_sha256':m.sha(Path(__file__).read_bytes())}
 if f.exists():
  prior=m.load(f)
  for k,v in spec.items():
   if k!='primary_results_sha256':assert prior[k]==v
 else:spec['frozen_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();m.save(f,spec)
 key=m.old.original.load_key(m.ROOT.parent/'19 - Jev Decision Classification/.env')
 client=m.infra.Client(H/'traces',typesafe_key=key,cap=2)
 jobs=[(rep,i) for rep in [2,3] for i in range(520)];random.Random(20261111).shuffle(jobs)
 def one(job):
  rep,i=job;p=m.payload(rows[i],selected)
  assert m.sha(m.enc(p))==cfg['payload_hashes'][selected][i]
  e=client.request('typesafe',p,f'R{rep}-{i:03d}');m.answer(e)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(one,j) for j in jobs]
  try:
   for f in concurrent.futures.as_completed(futures):f.result()
  except BaseException:
   for f in futures:f.cancel()
   raise
 print('Both fixed repeats complete.')
if __name__=='__main__':main()
