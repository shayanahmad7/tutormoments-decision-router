# Astra decision-only pilot

## Material Passport

Public TutorMoments data. Twenty new Astra classifications; saved comparison decisions. Automated analysis, no human validation or generated tutor responses.

## Matched results

Each method uses the same latest prompt and the same 20 moments, with ten moments per category from 20 distinct students. Astra uses high reasoning; Luna uses none. Sample and cascade thresholds were frozen before Astra outputs.

| Method | Correct /20 | Accuracy | Scaffold /10 | Rigor /10 | Token cost for these 20 | Median complete request |
|---|---:|---:|---:|---:|---:|---:|
| GPT-6 Astra, high reasoning | 13 | 65.0% | 5 | 8 | $1.3880 | 4.61s |
| Jev 1.14.0 | 12 | 60.0% | 3 | 9 | $0.0057 | 0.26s |
| OpenAI Decisions, Luna | 13 | 65.0% | 5 | 8 | $0.0118 | 0.35s |
| GPT-6 Luna, one-word | 12 | 60.0% | 5 | 7 | $0.0119 | 1.01s |

New spending: **$1.3880**. All other model results are reused. Astra produced 3,990 reasoning tokens; 0 incomplete responses. Its output ceiling was 4096 tokens per request, including reasoning.

The small sample limits precision. Different reasoning settings mean this compares practical configurations, not model size alone. All records have previously informed prompt development. Latency includes the complete classification request and is not the website's tutoring time-to-first-answer-token metric. Cheap-model timings are historical.

## Paired accuracy differences

| Astra versus | Astra only correct | Comparator only correct | Net matches | Exact paired p | Holm-adjusted p |
|---|---:|---:|---:|---:|---:|
| Jev 1.14.0 | 2 | 1 | +1 | 1.0000 | 1.0000 |
| OpenAI Decisions, Luna | 2 | 2 | +0 | 1.0000 | 1.0000 |
| GPT-6 Luna, one-word | 2 | 1 | +1 | 1.0000 | 1.0000 |

## Jev first, Astra when uncertain

Primary threshold 0.90; 0.80 and 0.95 are predeclared sensitivity checks. Probabilities are model scores, not guaranteed correctness. These are offline estimates from actual component outputs, not a deployed pipeline.

| Accept Jev at | Correct /20 | Calls to Astra /20 | Estimated cost | Saving vs always Astra | Confident Jev errors |
|---|---:|---:|---:|---:|---:|
| 0.9 | 13 | 19 | $1.3397 | 3.5% | 0 |
| 0.8 | 13 | 15 | $1.1725 | 15.5% | 1 |
| 0.95 | 13 | 19 | $1.3397 | 3.5% | 0 |

## Older prompt on the same sample

These supplementary controls use an older prompt and are not prompt-matched to Astra. They help show whether the latest prompt artificially weakens a comparator.

| Method | Correct /20 | Accuracy |
|---|---:|---:|
| Jev 1.14.0, earlier prompt C | 14 | 70.0% |
| OpenAI Decisions, Luna, earlier prompt C | 17 | 85.0% |
| GPT-6 Luna, one-word, earlier prompt C | 15 | 75.0% |

## Context length across all 520

| Method | Minimum tokens | Median | Maximum | Accuracy from shortest to longest quartile |
|---|---:|---:|---:|---|
| Jev 1.14.0 | 1,352 | 7,164 | 21,518 | 69.2% / 72.3% / 70.8% / 70.0% |
| OpenAI Decisions, Luna | 1,102 | 6,329 | 19,300 | 76.2% / 76.2% / 70.8% / 63.1% |
| GPT-6 Luna, one-word | 1,090 | 6,317 | 19,288 | 78.5% / 71.5% / 73.1% / 66.9% |

These inputs fit the documented context limits. Length groups also differ in tasks, students and difficulty, so these descriptive associations do not identify a causal effect of context length. The earlier full-versus-window Jev comparison was 376/520 versus 375/520, offering no clear windowing gain.

## Jev selective coverage across all 520

| Probability threshold | Cases accepted | Coverage | Correct among accepted | Observed accuracy |
|---|---:|---:|---:|---:|
| 0.8 | 196 | 37.7% | 170 | 86.7% |
| 0.9 | 70 | 13.5% | 66 | 94.3% |
| 0.95 | 24 | 4.6% | 24 | 100.0% |

These are exploratory risk/coverage descriptions from the existing full-corpus run. High accuracy on a small accepted subset is not overall benchmark accuracy or guaranteed calibration. Category breakdowns are in results.json.

## Files and reproduction

- [All 20 decisions](All%2020%20decisions.csv), [results](results.json), [verification](verification.json).
- [Frozen plan](PLAN.md), [frozen hashes](frozen.json), `traces/` for complete requests/responses.
- [Research assessment](Research%20assessment.md): interpretation, contribution and next study.

Offline: `python3 experiments/astra-decision-pilot/analyze.py`. Paid: `python3 experiments/astra-decision-pilot/run.py run`; completed requests resume without another charge.

## Sources

- [Astra model and pricing](https://developers.openai.com/api/docs/models/gpt-6-astra), [reasoning limits](https://developers.openai.com/api/docs/guides/reasoning).
- [Jev context limits](https://docs.typesafe.ai/models), [Luna context limit](https://developers.openai.com/api/docs/models/gpt-6-luna).
- [TutorMoments](https://tutormoments.allen.ai/).
