# Scaffold or rigor: Decisions API versus a one-word LLM

All **520 moments** were tested in each OpenAI condition. The saved Jev prompt C results provide the third comparison. Every method received the same full pre-cut conversation and decision criteria. No tutoring response was generated.

| Method | Correct /520 | Accuracy | Scaffold /260 | Rigor /260 | Median latency | Token cost |
|---|---:|---:|---:|---:|---:|---:|
| Jev 1.14.0, prompt C (saved first run) | 376 | 72.3% | 181 | 195 | 0.192s | $0.1686 |
| OpenAI Decisions, GPT-6 Luna | 386 | 74.2% | 204 | 182 | 0.333s | $0.3503 |
| GPT-6 Luna, one-word response | 373 | 71.7% | 213 | 160 | 0.922s | $0.3523 |

Jev cost and latency describe its earlier saved run. **New spending for both OpenAI runs: $0.7026**. Cost is calculated from recorded usage at published prices. No caching was used in either OpenAI condition. All completed requests, including preflight calls, are included.

## Paired differences

| Comparison | Net additional matches | First only correct | Second only correct | Difference (percentage points), student-cluster 95% interval |
|---|---:|---:|---:|---:|
| decisions versus llm | +13 | 48 | 35 | +2.50 [-0.86, +6.31] |
| decisions versus jev | +10 | 61 | 51 | +1.92 [-1.93, +6.08] |
| llm versus jev | -3 | 47 | 50 | -0.58 [-3.85, +2.74] |

## What this comparison measures

This measures agreement with the published scaffolding/rigor category at the stopping point. It does not measure the quality of a generated tutor response or student learning. The published labels are unchanged, including three identical-context pairs with opposite labels.

Prompt C was selected during earlier exploration of this corpus. These are full-benchmark exploratory results, not a new held-out test. Raw API choices are compared; the previously tuned Jev threshold is not substituted into the main table. The LLM baseline uses reasoning none and a 32-token output ceiling, so the result does not represent all LLM prompting or reasoning settings.

The two new arms use GPT-6 Luna but different API interfaces. They receive identical evidence and instructional criteria; the LLM additionally receives a one-word formatting instruction. This compares two practical classification configurations, not an isolated causal estimate of one internal model mechanism.

## Timing and output checks

| Method | p95 latency | Retried requests | Invalid outputs |
|---|---:|---:|---:|
| Jev 1.14.0, prompt C (saved first run) | 0.279s | 0 | 0 |
| OpenAI Decisions, GPT-6 Luna | 0.618s | 0 | 0 |
| GPT-6 Luna, one-word response | 2.420s | 0 | 0 |

Timing measures complete HTTP requests, not time-to-first-token. The OpenAI conditions were interleaved; Jev ran earlier. Service/network load can change timings.

## Files and reproduction

- [All 520 decisions](All%20520%20decisions.csv): one row per record, all three predictions, correctness, probabilities, cost and timing.
- [Frozen plan](PLAN.md), [frozen hashes](frozen.json), [machine-readable results](results.json), [verification](verification.json).
- `traces/`: exact OpenAI requests, responses, usage and timings; saved Jev trace hashes point to `../jev-decision-study/traces/C-*.json`.

Offline: `python3 experiments/openai-decision-comparison/analyze.py`. This recomputes results and verifies full context, source, prompt and response hashes without API calls.

Paid rerun: `python3 experiments/openai-decision-comparison/run.py run`. Completed identical requests resume without new charges. Budget cap $2. Credentials are read from the environment or a private env file and are not included in this archive.

## Sources

- [TutorMoments dataset](https://huggingface.co/datasets/allenai/tutormoments-preview), pinned revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`.
- [OpenAI Decisions documentation](https://developers.openai.com/api/docs/guides/decisions), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing).
- [Jev models and pricing](https://docs.typesafe.ai/models).

## Material Passport

Public TutorMoments-Preview source; automated classification only. 1,040 new OpenAI calls and 520 saved Jev calls. Status: completed, results recomputed from archived responses. No human validation claimed.
