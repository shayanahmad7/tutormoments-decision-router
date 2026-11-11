from pathlib import Path
import json,sys
H=Path(__file__).resolve().parent;R=H.parents[1]
rows=[json.loads(l) for l in (R/'data/jev/moments.jsonl').read_text().splitlines()];groups=json.loads((H/'conversation-inventory.json').read_text())
for gi in map(int,sys.argv[1:]):
 g=groups[gi];rr=rows[g['longest_index']];cuts={}
 for i in g['indices']:
  r=rows[i];assert rr['context'][:len(r['context'])]==r['context']
  cuts.setdefault(len(r['context'])-1,[]).append(i)
 print('\nCONVERSATION',gi,'RECORD INDICES',g['indices'])
 for ti,t in enumerate(rr['context']):
  print(str(t['turn_number'])+(' S ' if t['role']=='student' else ' T ')+t['text'])
  for i in cuts.get(ti,[]):
   r=rows[i];pred=json.loads((R/'experiments/openai-decision-comparison/traces'/f'decisions-{i:03d}.json').read_text())['prediction']
   jev=json.loads((R/'experiments/jev-decision-study/traces'/f'C-{i:03d}.json').read_text())['response']['answers']['next_move']['choice']
   llm=json.loads((R/'experiments/openai-decision-comparison/traces'/f'llm-{i:03d}.json').read_text())['prediction']
   print('<<< MOMENT',i,'REFERENCE',r['dimension'],'PRIOR: decisions='+pred+', jev='+jev+', llm='+str(llm),'NOTE:',r['rubric']['hint'],'>>>')
