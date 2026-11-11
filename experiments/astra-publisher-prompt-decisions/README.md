# Astra: publisher prompt, decision output only

This is the requested decision-only test. No tutoring replies, student simulator or judge were used. We preserved the publisher's evaluation-aware teaching guidance and student metadata, removed only the multiple-message output instruction, supplied the complete pre-cut conversation, and asked for one word: scaffolding or rigor.

## Results on the same 20 moments

| Prompt | Correct /20 | Accuracy | Scaffolding /10 | Rigor /10 |
|---|---:|---:|---:|---:|
| Publisher prompt adapted for a decision | 14 | 70% | 6 | 8 |
| Previous revised decision prompt | 13 | 65% | 5 | 8 |

Previous errors corrected: 1; new errors introduced: 0; changed decisions: 1. Exact paired two-sided p=1.0000; the small sample does not establish general superiority or equivalence.

New token cost: **$1.2145**, below the $2.50 ceiling. 0 invalid outputs and 0 incomplete responses. Largest output including reasoning: 360 tokens against the 4096-token ceiling. No additional runs or prompt variants were launched.

## What changed

Only the API input text changed relative to the earlier decision run. Model, endpoint, reasoning effort, output ceiling and other request settings were identical: official OpenAI Responses API, gpt-6-astra, high reasoning, 4096 output tokens including reasoning, default service tier, explicit cache mode without breakpoints and store=false. Each prompt is supplied as one input string. The original publisher prompt places instructions before context; this ordering is retained in the adaptation.

The following instruction replaces the tutor-message output requirement:

> Using the tutoring instructions above and the conversation so far, choose the approach for the tutor's next move. Return exactly one word: scaffolding or rigor. Do not generate a tutor response or an explanation.

There are no supplied teacher labels, hints, post-cut turns, prior predictions or oracle student traits. The 20 moments and their order are exactly the earlier frozen sample, ten per category from 20 distinct students. They were not selected again using model correctness. These are previously examined development materials, so the result is exploratory rather than held-out validation.

This remains a forced binary decision task. The publisher's approximately 92.7% Astra website score comes from a multi-turn tutoring task with different outcome scoring; this adaptation does not make those percentages interchangeable. The four tutoring replays run before this clarification are a separate, unintended-task experiment and are excluded from this decision result.

## Artifacts

- [Adapted prompt template](Adapted%20prompt.txt) and [exact output instruction](decision-instruction.txt).
- [All 20 decisions](All%2020%20decisions.csv), [results](results.json), [frozen plan](PLAN.md), [hashes](frozen.json).
- `traces/` preserves every actual request and response. Only this model was called.

Offline verification: `python3 experiments/astra-publisher-prompt-decisions/analyze.py`. Existing successful traces are never regenerated for reporting.

[Publisher prompt](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/prompts/tutor/scaffolding_rigor.txt), [TutorMoments](https://tutormoments.allen.ai/), [official Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra).
