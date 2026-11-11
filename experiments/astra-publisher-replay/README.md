# Astra under the original TutorMoments conditions

## Current status: awaiting OpenRouter credit

The original-protocol replication is prepared for the same 20 moments as the earlier decision-only pilot. One Astra tutor call completed with the publisher's exact evaluation-aware instructions. The first Claude student call was rejected before provider generation because OpenRouter's available balance did not cover the publisher's 128,000-token output ceiling. No complete replay has been scored. **There is no replication accuracy result yet.** Completed-call token cost: $0.1410575. The failed trace's $3.47235 value is a conservative worst-case reservation, not an observed charge.

The user was asked to add $5 OpenRouter credit. Do not lower the output ceiling, substitute a model, or automatically retry while awaiting the reply. The total planned token-cost ceiling is $15.

## Why the earlier 65% and the website's 92.7% differ

| Condition | Earlier test | Publisher evaluation-aware benchmark |
|---|---|---|
| Prompt | Our revised binary classification instructions | Their original tutoring instructions |
| Response | One scaffold-or-rigor label | Natural tutor replies |
| Interaction | One classification | Up to three tutor and two simulated student replies |
| Scoring | Exact label agreement | Matching pedagogical action, including `both`, and no over-scaffolding |
| Sample | 20 moments | 520 moments |
| Result | 13/20 labels, 65% | Scaffolding 93.8%, rigor 91.5%; rounded-rate mean 92.65% |

The earlier 65% does not contradict or reproduce the website result. A replay may scaffold and push for rigor within the same short conversation. Such an exchange can satisfy either category when the scorer finds no over-scaffolding. That differs from requiring one exclusive label before responding.

The website's 90%+ values are from later model runs. The working paper's original seven-model table does not include Astra. The live leaderboard identifies its evaluation-aware source run as `gpt-6-astra_scaffolding_rigor_tutormoments-preview_20260929`.

## What is matched

- Same fixed pre-cut histories, student metadata, original evaluation-aware tutor text, high reasoning and 128,000-token ceiling.
- Publisher explicit prompt-cache construction for Astra, extracted from current source.
- Original oracle student: Claude Opus 4.6 with thinking disabled, released persona and reference continuation.
- Original Claude Opus 4.6 adaptive-thinking scorer: annotate, decompose action and over-scaffolding, classify action; original prompts and metric formulas.
- Original message splitting, five-speaking-call limit, and early stopping rules.

All seven prompt files match live publisher source byte for byte. The offline parity verifier checked 120 tutor, 60 student and 80 scoring prompt constructions, plus 60 hidden-field exclusion checks, across all 20 cases.

Infrastructure differences remain explicit: Claude is accessed through OpenRouter's Anthropic Messages endpoint, pinned to Anthropic; requests are synchronous and non-streaming, and judging is not batched. No timing equivalence is claimed. The undated model alias may differ from the September run. This is a small protocol-matched replication, not a bit-identical rerun of their full benchmark.

## Files

- [Frozen plan](PLAN.md) and [request/source hashes](frozen.json).
- [Protocol verification](protocol-verification.json), [current status/results](results.json).
- `traces/` contains exact requests, responses and failure records; `cases/` contains resumable progress.
- `source/` preserves the fetched publisher code under the Apache 2.0 license in the repository's `third_party/tutormoments` folder. No source instruction files were executed.

Offline status: `python3 experiments/astra-publisher-replay/analyze.py`.

After the user confirms restored credit, preserve the rejected student request under a separate failure-history directory before resuming the frozen runner. Successful Astra calls must be reused, not regenerated. Resume remains subject to the budget reservation check.

## Sources

[Live leaderboard and task description](https://tutormoments.allen.ai/), [leaderboard data](https://tutormoments.allen.ai/static/data/leaderboard.json), [working paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [original configuration](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/default_config.yaml), [original tutor prompt](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/prompts/tutor/scaffolding_rigor.txt), [scoring formulas](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/report.py).
