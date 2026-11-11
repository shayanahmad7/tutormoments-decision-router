"""Post-run provenance check only. Never changes ratings or scores."""
import csv,json,pathlib,re,unicodedata,collections
H=pathlib.Path(__file__).resolve().parent

def norm(t):
 t=unicodedata.normalize('NFKC',t).translate(str.maketrans({'’':"'",'‘':"'",'“':'"','”':'"','–':'-','—':'-'}))
 t=re.sub(r'[*_`]', '',t)
 return re.sub(r'\s+',' ',t).strip().casefold()

def ordered_segments(e,r):
 parts=[p.strip() for p in re.split(r'\.{3}|…',e) if p.strip()]
 if len(parts)<2:return False
 start=0
 for part in parts:
  n=r.find(part,start)
  if n<0:return False
  start=n+len(part)
 return True

rows=[];counts={}
for phase,file in [('primary','replies-and-ratings.csv'),('audit','audit-replies-and-ratings.csv')]:
 counts[phase]=collections.Counter()
 for row in csv.DictReader((H/file).open()):
  if row['evidence_exact']=='True':continue
  e,r=norm(row['evidence']),norm(row['reply'])
  kind='formatting_or_case_only' if e in r else ('explicit_ellipsis_with_verbatim_segments' if ordered_segments(e,r) else 'wording_changed_or_omitted')
  rows.append({'phase':phase,'index':row['index'],'moment_number':row['moment_number'],'arm':row['arm'],'classification':kind,'evidence':row['evidence'],'actual_reply':row['reply'],'strict_pass_unchanged':row['strict_pass']})
  counts[phase][kind]+=1
with (H/'Evidence Quote Audit.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
primary=list(csv.DictReader((H/'case-results.csv').open()));audit=list(csv.DictReader((H/'audit-case-results.csv').open()));ids={x['index'] for x in audit}
conditions=list(dict.fromkeys(x['condition'] for x in audit));comparison={}
for c in conditions:
 a=[x for x in primary if x['index'] in ids and x['condition']==c];b=[x for x in audit if x['condition']==c]
 comparison[c]={'n':len(a),'primary_pass':sum(x['strict_pass']=='True' for x in a),'audit_pass':sum(x['strict_pass']=='True' for x in b)}
raw=list(csv.DictReader((H/'replies-and-ratings.csv').open()));araw=list(csv.DictReader((H/'audit-replies-and-ratings.csv').open()));lookup={(x['index'],x['arm']):x for x in raw};agree=sum(lookup[x['index'],x['arm']]['strict_pass']==x['strict_pass'] for x in araw);p1=sum(lookup[x['index'],x['arm']]['strict_pass']=='True' for x in araw)/len(araw);p2=sum(x['strict_pass']=='True' for x in araw)/len(araw);pe=p1*p2+(1-p1)*(1-p2)
out={'note':'No scores changed. Normalization removes whitespace, Markdown emphasis and quote glyph/case differences. Explicit ellipses checked as ordered verbatim segments. Wording differences remain flagged.','quote_mismatches':{k:dict(v) for k,v in counts.items()},'same_32_case_condition_counts':comparison,'pass_agreement_96_replies':{'n':96,'same':agree,'rate':agree/96,'cohen_kappa':(agree/96-pe)/(1-pe)}}
(H/'evidence-and-audit-summary.json').write_text(json.dumps(out,indent=2)+'\n')
text=['# Evaluator evidence audit','',out['note'],'','The original exact-match flags, saved responses and ratings remain unchanged. The CSV lists every flagged quotation with the actual generated reply. This review checks quotation provenance, not correctness of the evaluator judgment.','']
for k,v in counts.items():text.append(f'{k}: '+', '.join(f'{n} {label.replace("_"," ")}' for label,n in v.items())+'.')
text+=['','## Same fixed 32 cases','| Condition | Gemini passes | Claude passes |','|---|---:|---:|']
for c,v in comparison.items():text.append(f'| {c} | {v["primary_pass"]}/32 | {v["audit_pass"]}/32 |')
text+=['',f'Across the 96 independently rated replies, pass/fail agreement was {agree}/96 ({agree/96:.1%}), Cohen kappa {(agree/96-pe)/(1-pe):.3f}. The 32 cases were fixed before outcomes, balanced by source category, one per student. This is a second automated evaluator, not human validation.','']
(H/'Evidence and Evaluator Audit.md').write_text('\n'.join(text));print(json.dumps(out,indent=2))
