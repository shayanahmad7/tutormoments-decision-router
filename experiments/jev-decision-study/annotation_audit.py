"""Post-result text audit. Flags source disagreements; never changes gold labels."""
from pathlib import Path
import csv,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('annotation_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
# Assistant reviewed each keyword-flagged note. This is not independent human validation.
EXPLICIT={48,83,167,176,178,217,245,284,285,291,331,332,342,353,361,363,364,375,376,472,473,495,519}
def main():
 rows=m.source();flags=[]
 for i,r in enumerate(rows):
  note=r['rubric']['hint'];low=note.lower();g=r['dimension']
  if (g=='rigor' and 'scaffold' in low and 'rigor' not in low) or (g=='scaffolding' and 'rigor' in low and 'scaffold' not in low):
   flags.append({'moment_index':i,'reference':g,'representative_note':note,
    'assistant_text_review':'explicit recommendation for opposite direction' if i in EXPLICIT else 'negation, prior support or description; no clear opposite recommendation',
    'changes_to_reference':False})
 assert EXPLICIT.issubset({r['moment_index'] for r in flags})
 result={'screen':'One opposite-direction keyword and no same-direction keyword; not an exhaustive semantic audit.',
 'screened_records':520,'keyword_flags':len(flags),'explicit_opposite_recommendation_flags':len(EXPLICIT),
 'review':'Assistant reading of flagged note text; not independent human adjudication.',
 'interpretation':'The schema says dimension is the aggregate judgment and rubric.hint is one representative annotator’s situation text. Disagreement is a review flag, not proof the aggregate label is wrong. No labels, inputs or scored cases were changed.',
 'source':'https://huggingface.co/datasets/allenai/tutormoments-preview/blob/main/moments.schema.json','records':flags}
 m.save(H/'annotation-note-audit.json',result)
 with (H/'Annotation notes for review.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flags[0]));w.writeheader();w.writerows(flags)
 print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
