# Small Astra decision pilot and decision-model utility

## Material Passport

Public TutorMoments-Preview data; automated classification. A new 20-case pilot reuses saved cheap-model decisions. No human validation, tutoring replies, fine-tuning or new participant data. This plan is frozen before Astra predictions.

## Primary comparison

Run GPT-6 Astra with high reasoning on exactly 20 moments: ten published scaffolding labels and ten rigor labels, one moment per student. A seeded shuffle of all520 indices (20261110) is traversed, accepting the first eligible record until each label has ten. Selection uses only label, student identity and the fixed seed, never existing prediction correctness, confidence, length or annotation hints. Do not replace difficult or ambiguous sampled cases. All20 selected moments happen to be mathematical in the existing review notes.

Use the exact input string from the latest one-word Luna run: full unmodified pre-cut context plus the476-word revised prompt and one-word format instruction. Change model to gpt-6-astra, reasoning to high, output ceiling to4096 tokens, and omit temperature. Explicit caching mode has no breakpoints; store false; standard service tier. No tools, expected labels, teacher hints, future dialogue or previous predictions. This is a practical model/configuration comparison, including differing reasoning budgets, not an isolated test of model size.

Reuse Jev, OpenAI Decisions and one-word Luna predictions from final-prompt-revision on the same selected indices as primary controls. Also report their older prompt-C predictions on those indices as supplementary context; do not compare Astra's20-case accuracy directly with anyone's520-case accuracy. Do not tune the Astra prompt or expand the sample after seeing results. Count invalid/incomplete responses as failures and report them explicitly rather than silently replacing them.

One preflight record is included in the20; at most two concurrent calls. Completed outputs are never rerun. Stop and inspect API failures. Freeze source, selection, prompt, runner, baseline and payload hashes. Hard new-inference cap $6; estimate from saved token usage $1.18 input plus up to $4.096 output at standard $10/$50 per million. Reasoning tokens count toward cost and the4096 ceiling. This ceiling is deliberately budget-limited and must be disclosed if it truncates responses. No new credit purchase.

## Predeclared offline cascade

Primary rule: accept Jev's raw decision when its maximum class probability is at least0.90; otherwise use Astra's decision. Secondary sensitivity rules:0.80 and0.95, reported without selecting a winning threshold. This is selective escalation for classification; it does not pass a Jev decision to a tutor or evaluate tutoring quality.

Reuse the actual saved predictions to calculate counterfactual accuracy, fraction escalated, Jev cost plus Astra cost only on escalated cases, and sum of observed Jev and Astra request latency for escalated cases. These are estimated cascade costs/latencies from component runs, not a measured deployed pipeline. Compare with always-Astra. Report confident Jev errors left uncorrected and any Astra errors avoided. No threshold fitting against the20 labels.

## Context and confidence diagnostics

Across the existing520 results, describe token lengths, errors by length quartile, and Jev accuracy/coverage at the predeclared confidence thresholds. This is observational: a length/error association does not prove a context-window cause, and absence of association does not establish equivalent long-context reasoning. Contrast actual input lengths with documented context limits. Review prior full/window-context experiments before proposing another summarization or truncation experiment.

## Analysis and decision

Report correct/20, both class recalls/10, invalids, token costs, total request median/p95 and reasoning-token usage. Calculate paired discordant counts, exact two-sided McNemar/binomial tests and descriptive95% intervals; with20 distinct students, statistical precision is low. All source data have already informed prompt development, so this is an exploratory diagnostic rather than held-out validation. Do not manufacture a successful technical contribution: distinguish a measured trade-off, a failed approach and an untested proposal.

After the pilot, synthesize whether the evidence motivates cheap routing, an uncertainty-gated cascade, supervised adaptation, or a negative finding. Any fine-tuning proposal must split by student/conversation before training, avoid repeated-prefix leakage, retain an untouched test corpus and compare with equally detailed prompting and fixed-policy controls. No training or larger inference run is authorized by this plan.

## Sources

- https://developers.openai.com/api/docs/models/gpt-6-astra
- https://developers.openai.com/api/docs/guides/reasoning
- https://tutormoments.allen.ai/
- https://huggingface.co/datasets/allenai/tutormoments-preview
