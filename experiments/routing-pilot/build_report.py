"""Create the readable report and local conversation viewer from saved results."""
import csv,html,json
from pathlib import Path
H=Path(__file__).resolve().parent
def main():
 r=json.loads((H/'results.json').read_text());cfg=json.loads((H/'frozen.json').read_text())
 models=cfg['models'];names={'original':'Original aware','self_detailed':'Detailed self-choice','jev_label':'Jev label only','jev_detailed':'Jev + detailed policy','teacher_detailed':'Teacher label + policy','opposite_teacher':'Opposite teacher label','always_scaffolding':'Always scaffold','always_rigor':'Always rigor','confidence_fallback':'Jev with .80 fallback','llm_detailed':'Qwen 14B router + policy'}
 lines=['# Jev-directed math tutoring: pilot results','',
 'This experiment tests whether a separate scaffold/rigor decision changes the quality of a small tutor’s next reply. Every comparison uses the same conversation inputs. The original 32-case sample contains four non-math current tasks; the math-only results below contain 28 cases from 28 students. All ratings are model-generated and remain open to human review.','',
 '## Math cases','',
 '| Condition | Qwen3 14B | Qwen3 32B |','|---|---:|---:|']
 for cond,name in names.items():
  vals=[r['math_only'][m]['conditions'][cond] for m in models]
  lines.append('| '+name+' | '+' | '.join(f"{v['strict_pass']}/{v['n']} ({100*v['strict_pass']/v['n']:.1f}%)" for v in vals)+' |')
 lines+=['','The table above uses Gemini 2.5 Flash. The following table uses independent Claude Sonnet 4.6 ratings of the same replies.','', '| Condition | Qwen3 14B, Claude judge | Qwen3 32B, Claude judge |','|---|---:|---:|']
 for cond,name in names.items():
  vals=[r['secondary_judge_analysis'][m]['math_only']['conditions'][cond] for m in models]
  lines.append('| '+name+' | '+' | '.join(f"{v['strict_pass']}/{v['n']} ({100*v['strict_pass']/v['n']:.1f}%)" for v in vals)+' |')
 lines+=['','A pass means the reply shows the teacher-required direction, avoids over-helping and detected mathematical errors, and fits the context. This is our first-reply measure, not the published five-speaking-turn TutorMoments score. Neither this measure nor label agreement establishes student learning.','',
 '## Math-only paired comparison','', '| Tutor / judge | Jev minus detailed self-choice | Paired 95% interval | Wins / losses | Exact p |','|---|---:|---:|---:|---:|']
 for m in models:
  for judge,v in [('Gemini',r['math_only'][m]['primary_comparison']),('Claude',r['secondary_judge_analysis'][m]['math_only']['paired'])]:
   lines.append(f"| {m.split('/')[-1]} / {judge} | {v['difference_pp']:+.1f} pp | {v['ci95_pp'][0]:+.1f} to {v['ci95_pp'][1]:+.1f} | {v['wins']} / {v['losses']} | {v['mcnemar_exact_p']:.3f} |")
 lines+=['','These exploratory sensitivity tests are unadjusted. Percentile bootstrap intervals and discrete exact tests need not give identical threshold decisions on a sample this small. The exact tests govern any significance statement.','',
 '## Primary comparison on the frozen 32-case sample','',
 '| Tutor | Jev detailed minus detailed self-choice | Paired 95% interval | Wins / losses | Holm-adjusted exact p |','|---|---:|---:|---:|---:|']
 for m in models:
  v=r['primary_comparisons'][m]
  lines.append(f"| {m.split('/')[-1]} | {v['difference_pp']:+.1f} percentage points | {v['ci95_pp'][0]:+.1f} to {v['ci95_pp'][1]:+.1f} | {v['wins']} / {v['losses']} | {v['holm_p']:.3f} |")
 lines+=['','The primary test was frozen on all 32 cases. The domain screen was recorded before any judging, and the 28-case math-only table is a sensitivity analysis. Small samples leave wide uncertainty. All derived policies reuse the same two forced-policy replies, so they are paired comparisons, not additional independent samples.','',
 '## What each control tells us','',
 '- Original aware versus detailed self-choice: whether the detailed instructions help by themselves.',
 '- Jev detailed versus detailed self-choice: whether choosing the policy outside the tutor adds value.',
 '- Jev detailed versus Jev label only: whether detailed branch instructions add value beyond the short decision.',
 '- Teacher policy versus Jev policy: how much the routing errors change the outcome under these particular generated replies.',
 '- Fixed and opposite policies: whether the generator follows the policy and whether matching the situation matters.',
 '- Confidence fallback: a fixed .80 probability rule, specified before results; lower-confidence cases use the self-choice reply. This is not a fitted or calibrated deployment rule.','',
 '## Route accuracy','',f"The Qwen3 14B decision-only control matched {r['llm_routing']['correct']}/{r['llm_routing']['n']} teacher labels.",f"Fresh Jev decisions matched {r['routing']['correct']} of 32 teacher labels. Median routing call time was {r['routing']['latency_ms']['p50']:.0f} ms. This is separate from reply quality.",'',
 '## Delay and estimated deployment cost','',
 '| Tutor and condition | Median first answer | p95 first answer | Cost per 1,000 replies |','|---|---:|---:|---:|']
 for m in models:
  for cond in ['original','self_detailed','jev_detailed','confidence_fallback','llm_detailed']:
   v=r['conditions'][m][cond];t=v['first_answer_ms_serial_estimate']
   lines.append(f"| {m.split('/')[-1]}: {names[cond]} | {t['p50']/1000:.2f}s | {t['p95']/1000:.2f}s | ${v['cost_per_1000_replies_usd']:.3f} |")
 lines+=['','Routed timing adds the fresh Jev call to the saved generator call. It is a reconstructed serial estimate. Shared-provider rate limits and concurrent execution make this a diagnostic, not a speed benchmark. Costs include only the route and delivered reply; generating both potential replies and judging them are experiment costs.','',
 '## Evaluation checks','']
 for m in models:
  v=r['cross_judge'][m]
  lines.append(f"- {m.split('/')[-1]}: the two judges agreed on {v['agree']}/{v['n_replies']} reply pass/fail ratings across {v['n_cases']} cases. Primary judge passes: {v['primary_pass']}; secondary judge passes: {v['secondary_pass']}.")
 lines+=['- Eight second-judge cases were prespecified. After detecting a primary-judge context error, the check was extended to all 32 cases, without changing prompts or selecting favorable ratings. Both evaluations are reported. See `judge-audit-extension.json`.']
 lines +=[f"- Truncated main-run replies: {r['truncated_generations']}. They count as failed replies.",f"- Unexpected non-whitespace reasoning outputs: {r['unexpected_reasoning_generations']}.",f"- Evidence-quote issues flagged for review: {len(r['evidence_quote_issues'])}.",
 f"- Successful experiment calls: {r['api_calls']}. Main trace cost: ${r['spending_usd']:.3f}. Including setup and conservative failed-request reservations: ${r['spending_including_setup_and_failed_reservations_usd']:.3f}.",'',
 '## Files and reproduction','',
 '- [Study design](PLAN.md), [execution changes](EXECUTION-NOTES.md), [frozen settings](frozen.json).',
 '- [Replies and ratings](replies-and-ratings.csv): the actual generated text with individual rubric judgments and evidence.',
 '- [Condition results by case](case-results.csv): which saved response each policy selected and how it scored.',
 '- [Machine-readable totals](results.json), [second-judge ratings](judge-comparison.json).',
 '- `review.html`: download and open locally to read each conversation and all five generated replies side by side.',
 '- Exact API requests and returned data are in `traces/`; setup calls and failed attempts are kept separately. No credentials are included.','',
 'Offline reproduction:','', '```sh','python3 experiments/routing-pilot/analyze.py','python3 experiments/routing-pilot/verify.py','python3 experiments/routing-pilot/build_report.py','```','',
 'A live rerun costs money. Preserve this run; use a new output directory or checkout for a new study. Supply `OPENROUTER_API_KEY` and `TYPESAFE_API_KEY` privately, then use `run.py prepare` and `run.py run`. Already successful requests are reused only when their exact payload hash matches. The $5 client guard includes setup and failed-attempt reservations.','',
 '## Next study','',
 'The conference claim should concern the effect and limits of separating instructional choice from generation, not the invention of pedagogical routing. Before treating this as paper evidence, expand beyond this small, previously explored preview; keep student-separated evaluation, add repeated generation seeds and another tutor family, repeat the cheap LLM-router control at scale, perform blinded human review, and evaluate multi-turn behavior with the publisher pipeline. Freeze the choices before the larger run. See the linked plan for related work and the analysis strategy.','']
 (H/'RESULTS.md').write_text('\n'.join(lines))
 source=[json.loads(l) for l in (H.parents[1]/'data/jev/moments.jsonl').read_text().splitlines()]
 ratings=list(csv.DictReader((H/'replies-and-ratings.csv').open()))
 cases=[{**c,'context':source[c['index']]['context'],'replies':[r for r in ratings if int(r['index'])==c['index']]} for c in cfg['cases']]
 data=json.dumps(cases,ensure_ascii=False).replace('<','\\u003c')
 page='''<!doctype html><meta charset="utf-8"><title>Jev tutoring pilot: case reader</title><style>body{max-width:1250px;margin:36px auto;padding:0 24px;font:16px/1.5 system-ui;color:#172024;background:#fafafa}h1{font-size:30px}select{padding:9px;font-size:16px;margin:4px 12px 16px 0}section{background:white;border:1px solid #ddd;padding:18px;margin:16px 0;border-radius:8px}pre{white-space:pre-wrap;font:15px/1.6 system-ui}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}.cards section{margin:0}small{color:#526064}h3{margin-top:0}.pass{border-top:4px solid #3b7462}.fail{border-top:4px solid #a45b48}</style><h1>Jev tutoring pilot</h1><p>Read the source conversation and the actual replies. Ratings below are model-assisted, not human validation.</p><label>Case <select id="case"></select></label><label>Tutor <select id="model"><option>qwen/qwen3-14b</option><option>qwen/qwen3-32b</option></select></label><div id="content"></div><script>const data=DATA;const sel=document.querySelector('#case');data.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent='Moment '+c.index+' · teacher: '+c.reference;sel.append(o)});function el(tag,text,parent){const n=document.createElement(tag);n.textContent=text;parent.append(n);return n}function render(){const c=data[+sel.value],out=document.querySelector('#content');out.replaceChildren();const sec=el('section','',out);el('h2','Conversation at the stopping point',sec);el('pre',c.context.slice(-14).map(t=>t.role.toUpperCase()+': '+t.text).join('\\n\\n'),sec);const d=el('details','',sec);el('summary','Full preceding conversation ('+c.context.length+' turns)',d);el('pre',c.context.map(t=>t.role.toUpperCase()+': '+t.text).join('\\n\\n'),d);const cards=el('div','',out);cards.className='cards';c.replies.filter(r=>r.model===document.querySelector('#model').value).forEach(r=>{const a=el('section','',cards);a.className=r.strict_pass==='True'?'pass':'fail';el('h3',r.arm.replaceAll('_',' '),a);el('pre',r.response,a);el('p','Rubric pass: '+r.strict_pass+' · Over-help: '+r.overhelp+' · Math error: '+r.math_error+' · Context fit: '+r.context_fit+'/2',a);el('small','Gemini: '+r.reason,a);el('p','Independent Claude pass: '+r.secondary_pass,a);el('small','Claude: '+r.secondary_reason,a)})}sel.onchange=render;document.querySelector('#model').onchange=render;render();</script>'''.replace('DATA',data)
 (H/'review.html').write_text(page)
 print('Wrote RESULTS.md and review.html')
if __name__=='__main__':main()
