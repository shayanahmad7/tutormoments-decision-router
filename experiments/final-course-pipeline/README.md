# Full-preview first-reply policy comparison

This experiment asks whether choosing scaffolding or rigor before generation helps a small tutor more than giving it the same detailed instructions and letting it choose. The frozen plan preceded all new generation. We did not revise prompts after seeing these results.

## Read the study

- [Results](RESULTS.md): every condition, source-category split, student-cluster uncertainty and sensitivity analysis.
- [Actual replies](replies-and-ratings.csv): 1,560 generated first replies with the evaluator's item-level ratings and reasons.
- [Paired policy results](case-results.csv): all 520 cases under seven conditions. Conditions reuse the same three replies; these are not seven independent generations.
- [Illustrative contrasts](Illustrative%20Cases.md): correct route with failed execution, wrong category with a passing reply, and a positive routed contrast. Selection rules are explicit.
- [Evaluator audit](Evidence%20and%20Evaluator%20Audit.md): the same 32 cases under both evaluators, quotation-provenance checks and unchanged ratings.
- [Frozen design](PLAN.md), [math-frame addendum](ANALYSIS-ADDENDUM.md), [execution record](EXECUTION-NOTES.md), and [source attribution](Dataset%20Attribution.md).

The full preview contains 520 moments across 89 students, 260 per assigned category. The pre-existing strict matched mathematics frame contains 346; it also requires suitable conversational cuts and usable replies across 15 original conditions and excludes duplicates. The 174 other records must not be described as all non-mathematical.

## Interpretation

Jev-directed selection passed 379/520 and detailed self-choice 357/520, but fixed rigor passed 385/520. In the matched math frame these were 252/346, 249/346 and 263/346. Neither tested router established an advantage over the fixed rigor policy. This is useful evidence about the need to evaluate routing, actual tutoring moves and fixed-instruction controls separately.

On the fixed 32-case audit, the Jev-versus-self contrast changed direction between Gemini and Claude. No human validation, learning improvement, benchmark victory, unseen test set or measured deployment speedup is claimed.

## Reproduce and inspect

`python3 experiments/final-course-pipeline/verify.py` reconstructs all exact tutor and judge inputs and recomputes scores from saved raw outputs. `python3 experiments/final-course-pipeline/analyze.py` recomputes the statistics without paid calls. Both use the repository's original public source file at `data/jev/moments.jsonl` and archived routing experiments. `export_package.py` makes the complete course review bundle with the original 520 records, cached router outputs and a standalone `reproduce_summary.py` requiring only the Python standard library. The bundle can be inspected and recomputed without private paths, credentials or network access.

All paid work is complete: 1,560 tutor generations, 520 primary judge calls and 32 second-evaluator calls. Accounted new spending is $3.002861866, including interrupted-call reservations. Raw trace and rating files are in `traces/` and `ratings/`; `failed-attempts/` preserves the seven interrupted or failed attempts. One audit response required a documented JSON quotation syntax repair; values and scores were not changed. See `parse-repair.json`.

Prompts and provider settings are in `frozen.json` and each exact trace. Hidden labels, teacher hints, future transcript and student persona never enter deployable tutor requests. Archived routers received the same complete pre-cut transcript as the tutor, while the tutor additionally received publisher student metadata. Both cached router inputs were checked across all 520 records in `archived-router-input-audit.json`.
