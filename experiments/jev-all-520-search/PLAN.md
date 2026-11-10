# Jev decisions: every candidate on all 520 moments

10 November 2026. The user explicitly requests full-520 prompt comparison and optimization. This is a separate exploratory extension of the preserved decision study. No tutor generation, synthetic student or evaluator model is called.

## Coverage

Every candidate A–F receives a decision for every one of the 520 published records. A and C already have 520 saved first-run decisions. B, D and E each have 138 saved decisions and need 382 more. F is a new candidate and receives 520 fresh decisions. Thus the comparison contains 3,120 candidate-record decisions: 1,454 reused exact requests and 1,666 new calls. Reuse is permitted only when the exact request payload matches; earlier repetitions are not substituted to improve scores.

A: prior selected prompt. B: instructional opportunity. C: structured criteria/examples. D: the same structured criteria with a current-task window. E: the same criteria with full history and a repeated recent exchange. F: compare a concrete support need with readiness to take responsibility, with balanced boundaries and no added examples. Freeze F before new calls.

Inputs contain only the pre-cut conversation. Never send the source category, annotation hint, IDs, future continuation or reference answer. The 260 scaffold and 260 rigor labels are used only in local scoring. Keep all 520, including duplicate/conflicting records and known non-math stopping points.

## Optimization and reporting

Report raw returned Jev choices first, with coverage, accuracy, scaffold recall, rigor recall and all errors. Select the highest raw full-520 accuracy; ties prefer shorter question then candidate ID. Also evaluate a fixed unweighted mean of all six prompts' rigor probabilities, at .50. For individual prompt ties at exactly .50, use the raw API choice. For ensemble ties, use A's choice.

Search fixed thresholds .05 through .95 in .01 increments for every prompt and the mean-probability ensemble. Choose by full-520 accuracy, then closeness to .50, then lower threshold. These are label-fitted decision rules, not raw Jev choices. They are optimization-set results, not held-out validation. No student IDs, lookup tables, per-record rules, corrected labels or arbitrary fitted model are allowed. Do not claim 100% or generalization from tuning and evaluating on the same 520.

Report all candidates, every threshold result, individual labels/probabilities, fresh-call and reused-call counts, exact payload hashes, cost and returned pinned model. Show a sensitivity excluding conflicting contexts without replacing the main score. Preserve earlier study files and their held-out-selection analysis unchanged.

## Execution

Pinned `jev-1.14.0`, existing TypeSafe key, four concurrent requests, $1.50 incremental cap. No purchases. Reuse the tested bounded client, preserve transient retries and failures, never resample completed calls for better scores. Freeze all request hashes before live requests. Raw replies, source data and reports remain in the existing private GitHub repo. All analysis is local and needs no model judge.

The three opposite-label identical-input pairs impose a consistent context-only ceiling of 517/520, but do not excuse the remaining errors. Some representative annotation notes disagree with aggregate labels; preserve the released labels and keep interpretation separate from correctness counts.

Sources: [TutorMoments dataset](https://huggingface.co/datasets/allenai/tutormoments-preview), [Choice API](https://docs.typesafe.ai/primitives/choice), [Jev version/pricing](https://docs.typesafe.ai/models). Public source excerpts are CC BY 4.0, credited to AllenAI and collaborators. See the preserved [prior decision study](../jev-decision-study/README.md) for source provenance and label audit.
