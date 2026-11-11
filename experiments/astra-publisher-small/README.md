# Astra with the original TutorMoments tutoring prompt

## Result

All four planned replays completed. **3/4 passed the publisher scoring rule.** This is a four-case implementation check, not an estimate of overall benchmark accuracy.

| Situation | Passed | Total |
|---|---:|---:|
| Scaffolding | 2 | 2 |
| Rigor | 1 | 2 |

The scorer found over-scaffolding in 1 of four replays. One replay was classified as scaffolding and three as both scaffolding and rigor. The failed rigor case included a rigor move, but the scorer judged that continued task setup and confirmation provided too much guidance despite the student's success.

## What we ran

Astra was called directly through the official OpenAI API with high reasoning and the publisher's unchanged evaluation-aware tutoring prompt. It generated real tutor replies, alternating with the original Claude Opus 4.6 oracle student for up to five speaking calls. The judge was also Claude Opus 4.6, using the original annotate/decompose/classify pipeline and scoring formulas. The student and judge were accessed through OpenRouter, pinned to Anthropic. These are simulated student replies, not new observations of human learners.

The same pre-cut transcript and released student metadata were supplied to the tutor. Gold labels, rubric hints, student persona and future transcript were not supplied to Astra. The oracle student received the released persona and reference continuation, as in the original benchmark. The judge received the teacher-category hint as the publisher specifies.

The first two moments per category in the earlier frozen 20-case order were used, without selecting by performance: source indices 309,250,325,376 (display moment numbers 310,251,326,377). No cases were added after results. All four use the original five-call protocol.

## Budget adaptation and verification

New requests had an **8,192-token output ceiling**, instead of the publisher's 128,000. The first Astra reply already paid for was reused with its original ceiling. No completed response was truncated or incomplete. The largest observed outputs, including any reasoning tokens, were {'tutor': 627, 'student': 68, 'judge': 1054}. This ceiling change is disclosed; the run is not a bit-exact reproduction of every publisher setting.

All seven prompt files were verified against publisher source. Offline parity checks covered tutor, student and scorer prompt construction. The completed requests were then reconstructed from the saved dialogue prefixes and checked for exact agreement. Successful replies ended normally, Claude requests used the specified model and Anthropic provider, and all OpenRouter billed usage matched our cost calculations.

Additional infrastructure differences: Claude via OpenRouter rather than direct Anthropic; synchronous unbatched judging and nonstreaming requests; potentially changed undated model aliases. No speed comparison is claimed.

## Cost

**New inference: $1.0515.** Including the $0.1411 previously saved reply, these four replays cost $1.1926 in token usage, below the $3 ceiling. There were 35 new successful API calls and 0 failed calls in this small run. No top-up, additional condition or larger evaluation was launched.

## How to interpret this alongside our earlier test

The earlier 65% result came from a different prompt asking Astra for a single exclusive scaffold-or-rigor label. This run uses the publisher's natural tutoring task, allows the model to respond to student feedback, and applies the publisher's behavior-based score. An exchange can contain both scaffolding and rigor and still pass when it contains the required action without over-scaffolding. The per-case sheet includes the older classification outputs for transparency; they are different outcomes, not a paired accuracy comparison.

The website reports 93.8% appropriate scaffolding and 91.5% appropriate rigor for Astra across 520 moments, approximately 92.7% overall. This tiny check does not reproduce that percentage or establish model superiority. It establishes that the original tutoring task must be evaluated directly before making claims about whether a decision router helps. No Jev intervention was run here.

## Inspect and reproduce

- [Readable conversations and scorer judgments](Readable%20replays.md).
- [Four-case results](Four%20replay%20results.csv), [machine-readable results](results.json).
- [Frozen plan](PLAN.md), [frozen configuration](frozen.json), [source-parity verification](protocol-verification.json).
- `traces/` preserves actual requests, responses, usage and provider metadata; `cases/` preserves the replay state.

Offline verification: `python3 experiments/astra-publisher-small/analyze.py`. Regenerate this report: `python3 experiments/astra-publisher-small/build_report.py`. Do not launch more paid inference merely to reproduce the tables.

## Sources

[TutorMoments website](https://tutormoments.allen.ai/), [published leaderboard data](https://tutormoments.allen.ai/static/data/leaderboard.json), [paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [original tutor prompt](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/prompts/tutor/scaffolding_rigor.txt), [original configuration](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/default_config.yaml), [original metric formulas](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/report.py).
