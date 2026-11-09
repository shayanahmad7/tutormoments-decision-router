# Jev-directed math tutoring: pilot results

This experiment tests whether a separate scaffold/rigor decision changes the quality of a small tutor’s next reply. Every comparison uses the same conversation inputs. The original 32-case sample contains four non-math current tasks; the math-only results below contain 28 cases from 28 students. All ratings are model-generated and remain open to human review.

## Math cases

| Condition | Qwen3 14B | Qwen3 32B |
|---|---:|---:|
| Original aware | 7/28 (25.0%) | 11/28 (39.3%) |
| Detailed self-choice | 14/28 (50.0%) | 17/28 (60.7%) |
| Jev label only | 15/28 (53.6%) | 16/28 (57.1%) |
| Jev + detailed policy | 17/28 (60.7%) | 23/28 (82.1%) |
| Teacher label + policy | 20/28 (71.4%) | 26/28 (92.9%) |
| Opposite teacher label | 17/28 (60.7%) | 14/28 (50.0%) |
| Always scaffold | 18/28 (64.3%) | 20/28 (71.4%) |
| Always rigor | 19/28 (67.9%) | 20/28 (71.4%) |
| Jev with .80 fallback | 17/28 (60.7%) | 20/28 (71.4%) |
| Qwen 14B router + policy | 19/28 (67.9%) | 23/28 (82.1%) |

The table above uses Gemini 2.5 Flash. The following table uses independent Claude Sonnet 4.6 ratings of the same replies.

| Condition | Qwen3 14B, Claude judge | Qwen3 32B, Claude judge |
|---|---:|---:|
| Original aware | 2/28 (7.1%) | 4/28 (14.3%) |
| Detailed self-choice | 15/28 (53.6%) | 14/28 (50.0%) |
| Jev label only | 11/28 (39.3%) | 12/28 (42.9%) |
| Jev + detailed policy | 19/28 (67.9%) | 19/28 (67.9%) |
| Teacher label + policy | 20/28 (71.4%) | 23/28 (82.1%) |
| Opposite teacher label | 17/28 (60.7%) | 13/28 (46.4%) |
| Always scaffold | 18/28 (64.3%) | 15/28 (53.6%) |
| Always rigor | 19/28 (67.9%) | 21/28 (75.0%) |
| Jev with .80 fallback | 18/28 (64.3%) | 16/28 (57.1%) |
| Qwen 14B router + policy | 19/28 (67.9%) | 18/28 (64.3%) |

A pass means the reply shows the teacher-required direction, avoids over-helping and detected mathematical errors, and fits the context. This is our first-reply measure, not the published five-speaking-turn TutorMoments score. Neither this measure nor label agreement establishes student learning.

## Math-only paired comparison

| Tutor / judge | Jev minus detailed self-choice | Paired 95% interval | Wins / losses | Exact p |
|---|---:|---:|---:|---:|
| qwen3-14b / Gemini | +10.7 pp | -3.6 to +25.0 | 4 / 1 | 0.375 |
| qwen3-14b / Claude | +14.3 pp | -3.6 to +32.1 | 6 / 2 | 0.289 |
| qwen3-32b / Gemini | +21.4 pp | +3.6 to +39.3 | 7 / 1 | 0.070 |
| qwen3-32b / Claude | +17.9 pp | -3.6 to +35.7 | 7 / 2 | 0.180 |

These exploratory sensitivity tests are unadjusted. Percentile bootstrap intervals and discrete exact tests need not give identical threshold decisions on a sample this small. The exact tests govern any significance statement.

## Primary comparison on the frozen 32-case sample

| Tutor | Jev detailed minus detailed self-choice | Paired 95% interval | Wins / losses | Holm-adjusted exact p |
|---|---:|---:|---:|---:|
| qwen3-14b | +12.5 percentage points | +0.0 to +28.1 | 5 / 1 | 0.219 |
| qwen3-32b | +28.1 percentage points | +12.5 to +46.9 | 10 / 1 | 0.023 |

The primary test was frozen on all 32 cases. The domain screen was recorded before any judging, and the 28-case math-only table is a sensitivity analysis. Small samples leave wide uncertainty. All derived policies reuse the same two forced-policy replies, so they are paired comparisons, not additional independent samples.

## What each control tells us

- Original aware versus detailed self-choice: whether the detailed instructions help by themselves.
- Jev detailed versus detailed self-choice: whether choosing the policy outside the tutor adds value.
- Jev detailed versus Jev label only: whether detailed branch instructions add value beyond the short decision.
- Teacher policy versus Jev policy: how much the routing errors change the outcome under these particular generated replies.
- Fixed and opposite policies: whether the generator follows the policy and whether matching the situation matters.
- Confidence fallback: a fixed .80 probability rule, specified before results; lower-confidence cases use the self-choice reply. This is not a fitted or calibrated deployment rule.

## Route accuracy

The Qwen3 14B decision-only control matched 24/32 teacher labels.
Fresh Jev decisions matched 23 of 32 teacher labels. Median routing call time was 184 ms. This is separate from reply quality.

## Delay and estimated deployment cost

| Tutor and condition | Median first answer | p95 first answer | Cost per 1,000 replies |
|---|---:|---:|---:|
| qwen3-14b: Original aware | 1.02s | 7.37s | $0.829 |
| qwen3-14b: Detailed self-choice | 0.76s | 2.16s | $0.848 |
| qwen3-14b: Jev + detailed policy | 1.01s | 4.37s | $1.121 |
| qwen3-14b: Jev with .80 fallback | 1.08s | 4.37s | $1.129 |
| qwen3-14b: Qwen 14B router + policy | 1.71s | 4.71s | $1.653 |
| qwen3-32b: Original aware | 1.71s | 17.50s | $0.564 |
| qwen3-32b: Detailed self-choice | 1.71s | 18.58s | $0.571 |
| qwen3-32b: Jev + detailed policy | 2.48s | 12.68s | $0.850 |
| qwen3-32b: Jev with .80 fallback | 4.22s | 18.77s | $0.856 |
| qwen3-32b: Qwen 14B router + policy | 3.29s | 13.13s | $1.383 |

Routed timing adds the fresh Jev call to the saved generator call. It is a reconstructed serial estimate. Shared-provider rate limits and concurrent execution make this a diagnostic, not a speed benchmark. Costs include only the route and delivered reply; generating both potential replies and judging them are experiment costs.

## Evaluation checks

- qwen3-14b: the two judges agreed on 122/160 reply pass/fail ratings across 32 cases. Primary judge passes: 83; secondary judge passes: 75.
- qwen3-32b: the two judges agreed on 121/160 reply pass/fail ratings across 32 cases. Primary judge passes: 95; secondary judge passes: 72.
- Eight second-judge cases were prespecified. After detecting a primary-judge context error, the check was extended to all 32 cases, without changing prompts or selecting favorable ratings. Both evaluations are reported. See `judge-audit-extension.json`.
- Truncated main-run replies: 3. They count as failed replies.
- Unexpected non-whitespace reasoning outputs: 0.
- Evidence-quote issues flagged for review: 14.
- Successful experiment calls: 512. Main trace cost: $2.557. Including setup and conservative failed-request reservations: $2.592.

## Files and reproduction

- [Study design](PLAN.md), [execution changes](EXECUTION-NOTES.md), [frozen settings](frozen.json).
- [Replies and ratings](replies-and-ratings.csv): the actual generated text with individual rubric judgments and evidence.
- [Condition results by case](case-results.csv): which saved response each policy selected and how it scored.
- [Machine-readable totals](results.json), [second-judge ratings](judge-comparison.json).
- `review.html`: download and open locally to read each conversation and all five generated replies side by side.
- Exact API requests and returned data are in `traces/`; setup calls and failed attempts are kept separately. No credentials are included.

Offline reproduction:

```sh
python3 experiments/routing-pilot/analyze.py
python3 experiments/routing-pilot/verify.py
python3 experiments/routing-pilot/build_report.py
```

A live rerun costs money. Preserve this run; use a new output directory or checkout for a new study. Supply `OPENROUTER_API_KEY` and `TYPESAFE_API_KEY` privately, then use `run.py prepare` and `run.py run`. Already successful requests are reused only when their exact payload hash matches. The $5 client guard includes setup and failed-attempt reservations.

## Next study

The conference claim should concern the effect and limits of separating instructional choice from generation, not the invention of pedagogical routing. Before treating this as paper evidence, expand beyond this small, previously explored preview; keep student-separated evaluation, add repeated generation seeds and another tutor family, repeat the cheap LLM-router control at scale, perform blinded human review, and evaluate multi-turn behavior with the publisher pipeline. Freeze the choices before the larger run. See the linked plan for related work and the analysis strategy.
