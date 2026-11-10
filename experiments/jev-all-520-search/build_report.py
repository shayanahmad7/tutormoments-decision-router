"""Publish the complete all-520 comparison without held-out claims."""
from pathlib import Path
import importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('report_full_run',H/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 r=m.m.load(H/'results.json');cfg=m.checked();raw=r['selection']['best_raw']['candidate'];tuned=r['selection']['best_tuned']['candidate']
 lines=['# Jev: all six prompts tested on all 520 moments','',
 '**Coverage is complete: 520/520 records for every prompt.** This experiment only asks Jev to choose scaffolding or rigor. It does not generate a tutor response or use another model to judge correctness. Each decision is compared directly with the published category.','',
 f"The best raw prompt was **{raw}: {r['raw'][raw]['correct']}/520 ({100*r['raw'][raw]['accuracy']:.1f}%)**. The best probability-threshold rule was **{tuned} at {r['best_threshold']:.2f}: {r['threshold_fitted'][tuned]['correct']}/520 ({100*r['threshold_fitted'][tuned]['accuracy']:.1f}%)**. None reached 100%.",'',
 '## Every prompt, same 520 records','',
 '| Prompt | Description | Coverage | Raw Jev matches | Best fitted threshold | Matches after threshold |','|---|---|---:|---:|---:|---:|']
 for c in m.specs():
  v=r['raw'][c];t=r['threshold_fitted'][c]
  lines.append(f"| {c} | {r['candidates'][c]} | 520/520 | {v['correct']} ({100*v['accuracy']:.1f}%) | {t['threshold']:.2f} | {t['correct']} ({100*t['accuracy']:.1f}%) |")
 v=r['raw']['mean'];t=r['threshold_fitted']['mean']
 lines.append(f"| Six-prompt mean | Average the six returned rigor probabilities | 520/520 | {v['correct']} ({100*v['accuracy']:.1f}%) at .50 | {t['threshold']:.2f} | {t['correct']} ({100*t['accuracy']:.1f}%) |")
 lines+=['','**Raw Jev matches** use the category returned by the API. **Threshold-adjusted matches** use its probability instead: choose rigor when `p_rigor >= threshold`, otherwise scaffold. At threshold .50, retain the API choice to handle probability ties consistently. The mean combines six calls per case; it is not a single Jev decision.','',
 'Every threshold from .05 to .95 in .01 increments was checked. Ties prefer the threshold closest to .50, then the lower value. The probabilities are averaged using decimal arithmetic so exact threshold boundaries do not depend on floating-point addition order.','',
 '**This round deliberately optimizes and measures performance on the same 520 records.** Its fitted thresholds and best prompt are exploratory full-benchmark results, not evidence of performance on unseen students. The earlier development/evaluation study is preserved separately and unchanged.','',
 '## Scaffold and rigor decisions','', '| Method | Scaffold matches / 260 | Rigor matches / 260 | Total matches / 520 |','|---|---:|---:|---:|']
 for label,v in [('Previous prompt A, raw',r['raw']['A']),('Best raw prompt '+raw,r['raw'][raw]),('Best fitted rule '+tuned,r['threshold_fitted'][tuned])]:
  p=v['per_label'];lines.append(f"| {label} | {p['scaffolding']['correct']} | {p['rigor']['correct']} | {v['correct']} |")
 lines+=['',f"Relative to raw A, the best raw prompt fixes {r['selection']['best_raw']['wins_vs_A']} cases and loses {r['selection']['best_raw']['losses_vs_A']}. The best fitted rule fixes {r['selection']['best_tuned']['wins_vs_A']} and loses {r['selection']['best_tuned']['losses_vs_A']}. These are paired descriptive changes on the optimization set, not a significance claim.",'',
 '## What the optimization found','',
 'The structured full-history prompt remains the strongest tested option. Shortening the context, repeating the latest exchange, emphasizing opportunities for independent work and adding the new balanced comparison prompt did not surpass it. Averaging six prompts also failed to beat the best one-prompt threshold rule. More prompt variants did not produce a large accuracy jump.','',
 'For this benchmark, the best fitted one-call rule is the structured prompt followed by a .55 rigor-probability cutoff. Keep its raw choice and probability alongside the adjusted decision. It still mismatches 138/520 references and has not established a new generalizable improvement over the previously tested method.','',
 'The published labels remain unchanged. Three pairs have identical model-visible inputs but opposite categories. A consistent context-only decision rule can match at most 517/520 in this file, even in principle. This does not explain away the remaining mistakes. The earlier [source audit](../jev-decision-study/label-audit.json) and [annotation-note review](../jev-decision-study/annotation-note-audit.json) remain available.','',
 '## Exactly what was run','',
 '- A and C already had 520 first-run decisions each. B, D and E each had 138; this round completed their remaining 382 each.',
 '- F is the new balanced-comparison prompt, run on all 520.',
 '- In total: **3,120 saved candidate-record decisions**, comprising **1,454 reused exact requests** and **1,666 fresh calls**. Reuse was checked against exact request hashes, not inferred from a previous score.',
 '- Every prompt got the past conversation only. Reference labels, teacher notes, IDs and future continuation were excluded from requests.',
 '- `jev-1.14.0` was pinned. The API returned only binary decisions and probabilities. No tutor, simulated student or evaluation-model calls.',
 f"- New cost: **${r['new_cost_usd']:.4f}**. The incremental cap was $1.50. No payment or top-up was made.",'',
 '## Files','',
 '- [All 520 decisions across six prompts](All%20520%20-%20Six%20prompt%20decisions.csv). One row per source record, with its reference, each actual decision, probabilities and fitted results.',
 '- [Best raw prompt errors](Best%20raw%20prompt%20-%20Errors.csv). Every mismatch, not only selected examples.',
 '- [Complete threshold search](Threshold%20search.csv), [machine-readable results](results.json), [best prompt](best-prompt.json), [best fitted rule](best-rule.json).',
 '- [Frozen plan](PLAN.md), [frozen inputs and reuse hashes](frozen.json), [verification](verification.json). Fresh raw requests and responses are in `traces/`; reused response paths are recorded in `frozen.json`.','',
 'Offline reproduction:','', '```sh','python3 experiments/jev-all-520-search/analyze.py','python3 experiments/jev-all-520-search/build_report.py','python3 experiments/jev-all-520-search/verify.py','```','',
 'Only `run.py run` makes live requests. Preserve this archive when running another experiment. The older [decision study](../jev-decision-study/README.md) and [tutoring-response pilot](../routing-pilot/RESULTS.md) are separate.','',
 'Source conversations: AllenAI and collaborators, [TutorMoments-Preview](https://huggingface.co/datasets/allenai/tutormoments-preview), CC BY 4.0, pinned revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`. The CSV reorganizes source records and adds our predictions without changing labels. [Jev Choice API](https://docs.typesafe.ai/primitives/choice), [model/pricing](https://docs.typesafe.ai/models).','']
 (H/'README.md').write_text('\n'.join(lines))
 m.m.save(H/'best-prompt.json',m.specs()[raw])
 m.m.save(H/'best-rule.json',{'model':'jev-1.14.0','candidate':tuned,'question':m.specs()[tuned]['question'] if tuned!='mean' else None,
 'threshold':r['best_threshold'],'rule':'rigor if returned p_rigor >= threshold, otherwise scaffolding','input':'Full pre-cut conversation; never include reference labels or future continuation.',
 'fit_scope':'Chosen on all 520 records; exploratory, not independently validated.','all_520_matches':r['threshold_fitted'][tuned]['correct'],'tutor_generation':False})
 print('Wrote report, best prompt, and explicit decision rule.')
if __name__=='__main__':main()
