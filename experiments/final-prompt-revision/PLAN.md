# Final decision-prompt revision

## Question

Can a clearer account of the learner's current instructional need improve agreement with TutorMoments' scaffolding/rigor labels, using one final prompt and one full run per method?

## Review before execution

Read every turn of the longest available pre-cut prefix in each of the 112 conversations containing the 520 records. Earlier cuts are marked within those prefixes; nested prefixes are verified against the source. The primary agent reviews groups 0–34, and three review subagents cover 35–60, 61–86 and 87–111. These are AI-assisted review notes, not human coding or adjudication. Check prior errors from all three methods and teacher annotation procedures. Reconcile all 520 indices before enabling any paid calls.

Use the review to improve general instructional distinctions. Do not add case IDs, student names, problem-specific examples, topic-to-label rules, expected answers, label frequencies, teacher hints or future dialogue to the prompt. Do not change the reference labels. Distinguish a representative teacher hint from the aggregated reference label.

## Fixed comparison

- Jev 1.14.0 through the System One endpoint.
- OpenAI GPT-6 Luna through the Decisions endpoint.
- GPT-6 Luna through Responses, returning exactly one word. Reasoning none, temperature 0, maximum output 32 tokens, store false.

Each method receives the complete pre-cut conversation with the same turn ordering, role labels and screen descriptions as the earlier comparison. The same revised instruction and two criterion strings are supplied through each provider's schema. The ordinary LLM additionally receives a one-word formatting instruction. No context truncation or repeated recent-window supplement. No human response, future student continuation, synthetic student traits, rubric, source ID, prior prediction or expected category is sent. The model-visible state is constructed only from context turn number, role and text.

All 520 records remain in the primary analysis, including duplicates, conflicting labels, noninstructional transitions and non-math records. Review domain notes are descriptive, not grounds for a post hoc exclusion or a claim of math-only accuracy. The previous 138/382 division no longer constitutes held-out evaluation because all records have informed prompt development.

## One-shot execution and budget

Freeze source, review notes, prompt, plan, runner and all 1,560 request hashes before API execution. Use exactly one revised prompt, no sweep and no prompt changes after predictions. Six preflight requests (first two records per arm) are part of the final 520, not extra tests. The remaining jobs are shuffled with seed 20261111 and interleaved through four HTTP workers. Completed requests are never repeated. Failed transport/API requests stop execution for inspection; no automatic retry or substituted prediction.

Use raw returned choices. No probability threshold fitting, majority vote, output repair or post-result exclusions. Invalid output counts as incorrect. OpenAI explicit caching mode with no breakpoints disables caching. No tools or tutor-response generation. The revised prompt's intended length is roughly 500 words, with no illustrative examples.

Total cap: $2, including conservative reservations for in-flight or failed requests. Expected total is below $1 using prior measured context token counts. No credit purchases or top-ups. Compute costs from recorded usage: Jev input $0.042/million, output free; GPT-6 Luna input $0.10/million, Responses output $0.50/million, Decisions output free. Record actual cache tokens and apply published cache prices if unexpectedly present; flag the comparison rather than hide a cache difference.

## Outcomes and comparison

Primary: unchanged source-label matches out of 520. Also report scaffolding and rigor matches out of 260 each, confusion matrices, macro F1, invalid outputs, usage cost, median and p95 HTTP latency.

Compare each revised method with its saved earlier result: Jev prompt C first run (376/520), Decisions (386/520), and one-word Luna (373/520). Report cases fixed and cases regressed, net change and paired student-cluster bootstrap intervals (89 student clusters, 10,000 resamples, fixed seed). Compare the three revised methods with the same paired procedure. No significance-based winner selection. These intervals do not account for full-corpus prompt development or annotation uncertainty.

Audit all saved payloads against their frozen hashes; recompute predictions from raw responses, all counts from predictions, and cost from usage. Verify 520 completed records per method, unique arm/index keys, full input preservation and complete review coverage. Keep the prior experiments intact. Archive the exact prompt, requests, responses, review notes, plan, CSV and offline verifier in the existing private repository.

## Interpretation

This is exploratory benchmark agreement after development on the full corpus. No claim of unseen-data performance, better tutoring responses or student learning is supported by this round. Identical inputs with opposite source labels preclude perfect agreement for a consistent deterministic context-only classifier. Report any failure to improve directly; do not run another prompt after seeing the final results.

## Sources

- [TutorMoments paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), sections 3.3–3.4 and appendices C–D.
- [Dataset](https://huggingface.co/datasets/allenai/tutormoments-preview), revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`.
- [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions), [model](https://developers.openai.com/api/docs/models/gpt-6-luna), [pricing](https://developers.openai.com/api/docs/pricing).
- [Jev models and pricing](https://docs.typesafe.ai/models).

## Material Passport

Public, deidentified source data; AI-assisted transcript review and automated classification. No new human participants or human validation. No submission or changes to course deliverables in this round.
