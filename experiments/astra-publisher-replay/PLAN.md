# Astra with the original TutorMoments task

Use the same frozen 20 moments from the preceding binary-decision pilot, ten per category and twenty distinct students. No new selection by performance. One evaluation-aware condition, no prompt tuning and no Jev routing.

Use the publisher's unchanged tutor prompt and full pre-cut context with student metadata; do not expose labels, rubric, persona or future to Astra. GPT-6 Astra, high reasoning, 128000 output ceiling, Chat Completions and the publisher's explicit prefix-cache construction. No decision-only instruction. Run up to five speaking calls (tutor, student, tutor, student, tutor), respecting publisher message splitting and stop tokens.

Student: Claude Opus 4.6, thinking disabled, publisher oracle prompt with released persona and reference continuation. Judge: Claude Opus 4.6, adaptive thinking, original annotate/decompose-action/decompose-over-scaffolding/structure prompts and JSON system instruction. Original parser and metric: appropriate category action (including both) with no over-scaffolding.

Claude is accessed through OpenRouter's Anthropic Messages API, pinned to Anthropic without provider fallback. This provider access path differs from the publisher's direct Anthropic access. Calls are synchronous, non-streaming and scoring is not batched; no latency comparison will be made. Model aliases can have changed since the September leaderboard run. Therefore this is a small protocol-matched replication with stated infrastructure differences, not a bit-exact reproduction of their run. All seven bundled prompt files were checked byte-for-byte against live publisher source before inference.

Primary output: category rates and their equally weighted mean, plus avoids-over-scaffolding. Report all 20 cases, both-action frequency and per-case differences from the earlier binary task, without treating those outcomes as interchangeable. Their full520 score is a published comparison, not an expected exact small-sample result.

Budget ceiling $15 in token costs; reserve worst-case input bytes and 128000 output tokens before each call, stop on errors or exhausted budget, do not silently substitute models or lower output limits. Resume only exact successful cached requests. No automated retries or extra conditions. Fetching public website data costs no inference.
