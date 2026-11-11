# One final prompt revision: scaffold or rigor

All 520 published moments were classified once by each method using one frozen revised prompt and the complete conversation up to the cutoff. No tutoring responses were generated.

The best revised score is 377/520 from GPT-6 Luna, one-word answer. The previous best was 386/520 from OpenAI Decisions (GPT-6 Luna). The revision did not improve that previous best. Retain the earlier Decisions prompt as the strongest observed configuration; the small LLM gain is not a demonstrated generalization improvement.

| Method | Previous correct | Revised correct | Revised accuracy | Change | Scaffold /260 | Rigor /260 | New token cost | Median request latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jev 1.14.0 | 376/520 | 367/520 | 70.6% | -1.73 pp | 147 | 220 | $0.1673 | 0.279s |
| OpenAI Decisions (GPT-6 Luna) | 386/520 | 372/520 | 71.5% | -2.69 pp | 210 | 162 | $0.3503 | 0.356s |
| GPT-6 Luna, one-word answer | 373/520 | 377/520 | 72.5% | +0.77 pp | 224 | 153 | $0.3514 | 1.035s |

Total new token cost: **$0.8690**. Costs use recorded token usage and published rates, not an invoice. All 1,560 completed decisions, including preflight responses, are included. No probability thresholds were fitted and no completed predictions were rerun.

## What changed

The new prompt judges the current instructional need across the learning episode. It distinguishes an unresolved obstacle from a reachable opportunity to explain, attempt or self-correct. It tracks which work the student actually produced, fades help when the obstacle is resolved, and does not equate every error with a need for help or every correct substep with understanding. Specific examples from the previous prompt were removed. See [the exact prompt](prompt.json).

## Review and evidence limits

The primary agent and three review subagents reviewed all pre-cut turns in the 112 distinct conversation prefixes that contain these 520 moments, with markers at every earlier cutoff. Repeated shared prefixes were read once. Notes are AI-assisted review, not human adjudication; the source labels were never changed. See [review synthesis](Review%20findings.md) and the per-conversation JSONL notes.

The full source file includes some literacy and vocabulary moments as well as mathematics. The requested all 520 comparison retains them and should be described as a TutorMoments benchmark result, not an exclusively math result. Domain notes are descriptive and were not used to select or exclude cases.

All 520 cases and previous errors informed prompt development. This is an exploratory full-benchmark revision, **not an unseen-data test**. The prompt contains no case IDs, answer lookup rules, teacher hints, expected labels or case-specific examples, but those safeguards do not remove development-set bias. A new held-out corpus is needed to test generalization.

The reference category is aggregated teacher annotation. A representative hint can disagree with that aggregate, and some hints describe later exchanges unavailable to a classifier at the cutoff. Three identical-context pairs have opposite categories, limiting a consistent deterministic context-only classifier to 517/520. Neither that ceiling nor a higher agreement score establishes the best teaching action or student learning.

## Paired changes from the previous prompt

| Method | Previously wrong, now correct | Previously correct, now wrong | Net change | 95% student-cluster interval for change (pp) |
|---|---:|---:|---:|---:|
| Jev 1.14.0 | 29 | 38 | -9 | [-5.41, +2.07] |
| OpenAI Decisions (GPT-6 Luna) | 49 | 63 | -14 | [-6.89, +1.76] |
| GPT-6 Luna, one-word answer | 34 | 30 | +4 | [-1.93, +3.54] |

Intervals use 10,000 paired bootstrap resamples of 89 student clusters. They describe uncertainty in the observed paired differences, not prompt-selection bias or generalization.

## Comparison among the revised methods

| Comparison | Net correct advantage | Difference (pp) | 95% student-cluster interval (pp) |
|---|---:|---:|---:|
| decisions versus llm | -5 | -0.96 | [-4.78, +2.97] |
| decisions versus jev | +5 | +0.96 | [-4.11, +6.36] |
| llm versus jev | +10 | +1.92 | [-2.89, +6.74] |

## Which decisions changed

- Jev 1.14.0: scaffolding matches 181 to 147 (-34); rigor matches 195 to 220 (+25).
- OpenAI Decisions (GPT-6 Luna): scaffolding matches 204 to 210 (+6); rigor matches 182 to 162 (-20).
- GPT-6 Luna, one-word answer: scaffolding matches 213 to 224 (+11); rigor matches 160 to 153 (-7).

The same instruction and criterion strings were used through provider-specific request schemas. The two OpenAI arms use the same named model through different interfaces; this is a practical configuration comparison, not an isolated causal test of internal architecture. LLM reasoning was disabled and output capped at 32 tokens. Four HTTP workers interleaved all three methods; latency includes network and service conditions.

## Files

- [All 520 decisions](All%20520%20decisions.csv): previous and revised predictions, reference, errors, timing and cost.
- [Exact prompt](prompt.json), [frozen plan](PLAN.md), [request hashes](frozen.json).
- [Results](results.json), [verification](verification.json), `traces/` for exact requests and responses.
- [Review findings](Review%20findings.md), `review-notes.jsonl` and `review-agent-*.jsonl` for full review notes.

Offline verification: `python3 experiments/final-prompt-revision/analyze.py`. The runner resumes completed identical requests without new charges. Do not alter the frozen plan or prompt.

## Sources

- [TutorMoments project](https://tutormoments.allen.ai/), [paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [dataset](https://huggingface.co/datasets/allenai/tutormoments-preview). Source revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`.
- [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing).
- [Jev models and pricing](https://docs.typesafe.ai/models).

## Material Passport

Public, deidentified source conversations; automated classification and AI-assisted review. No new human participants, human validation, tutoring response generation or learning-outcome measurement.

## Transport recovery

Failed transport attempts with no model response: 1. This is preserved separately in traces. Their actual billed cost is unknown; a conservative $0.004533 reservation brings total budget-accounted cost to $0.8736. Only unfinished requests were resumed with identical payloads. Successful-request timing is reported above; retry-inclusive timing and failure overhead are in results.json. See EXECUTION-NOTES.md.
