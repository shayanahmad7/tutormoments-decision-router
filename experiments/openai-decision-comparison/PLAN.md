# OpenAI Decisions versus a one-word LLM classifier

## Material Passport

Public, deidentified TutorMoments-Preview conversation excerpts. Decision classification experiment, 10 November 2026. Prior Jev results reused with exact trace hashes. No human coding, generated tutor response or simulated student in this round.

## Question and design

Does OpenAI's Decisions endpoint classify these same 520 scaffold/rigor opportunities more accurately, cheaply or quickly than its inexpensive GPT-6 Luna model returning a single word through the Responses endpoint?

Both new conditions use the full pre-cut context from the saved Jev C requests and exactly the same instruction and category-description content. The structured instructions/criteria are serialized to text because OpenAI's choice schema expects text. The LLM receives that same question plus a formatting instruction to return only `scaffolding` or `rigor`. No source label, teacher annotation, future continuation, ID or Jev prediction is sent. No context truncation. All 520 records, including duplicate and conflicting contexts, are retained.

- Decisions: gpt-6-luna, choice question, use returned choice directly.
- One-word LLM: gpt-6-luna, Responses API, reasoning none, temperature 0, max output 32 tokens, no tools, store false. Its output is stripped/lowercased and must equal one allowed label. Invalid outputs count as incorrect; no semantic repair.
- Jev comparator: saved first-run C predictions, jev-1.14.0. No additional Jev calls or threshold tuning. The earlier .55-threshold Jev result can be supplementary but is not the raw-choice baseline.

Primary outcome: correct source-label matches / 520. Also report each class /260, confusion matrix, invalids, macro F1 and all case-level predictions. Keep the previous 138/382 student split for descriptive subgroup results. Prompts were previously explored on this corpus; none of these full-set results is a fresh generalization test.

Freeze source, prompt, runner and request hashes before calls. Shuffle/interleave the two new arms with a fixed seed. Four concurrent HTTP workers. Preflight first two records in each condition, retain these results in the final 520. Successful traces are resumed without paying again. Log transient 429/5xx retries, stop on quota/auth errors; do not automatically repeat a completed prediction.

Explicit caching mode with no breakpoints disables prompt caching in both OpenAI arms, preventing shared-prefix cache advantages. Report measured request latency (median and p95), retry counts and billed-token cost at official rates. Latency is an observed API measurement; Jev was measured earlier and is not a simultaneous provider benchmark. Rate-limit waits must be separated from clean request latency.

Budget guard: $2 total across both OpenAI conditions, with conservative reservations for in-flight/failed requests. Estimated uncached cost is approximately $0.37 per condition. No top-ups or purchases.

If comparing accuracy differences, report paired discordant cases and a student-cluster bootstrap interval. Do not select new prompts, decision thresholds or exclusions based on this comparison. Benchmark label agreement is distinct from tutoring response quality and student learning.

Official documentation: https://developers.openai.com/api/docs/guides/decisions ; https://developers.openai.com/api/docs/models/gpt-6-luna ; https://developers.openai.com/api/docs/pricing . Source: https://huggingface.co/datasets/allenai/tutormoments-preview revision 3bb0c104d65e29facffca7ba864ef10fa22d0e78.
