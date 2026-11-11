# Four-case original-prompt tutoring replay

The user asked to use the official OpenAI API, finish the test properly, and avoid wasting credits. Run only four moments, first two per category in the previous frozen sample: 309, 250, 325, 376 (zero-based). Do not choose cases based on observed success and do not add cases after seeing scores.

Astra uses api.openai.com, high reasoning, original evaluation-aware tutor instructions, complete pre-cut conversation and student metadata. Do not ask for a binary label. Retain original Claude Opus 4.6 oracle student (thinking disabled), and Claude Opus 4.6 adaptive-thinking judge, accessed through OpenRouter pinned to Anthropic. Use all original student/scorer prompts and scoring formulas, five speaking calls and original stop/message-splitting rules.

Explicit budget adaptation: new calls have an 8192-token output ceiling instead of 128000. The already completed first Astra reply for moment309 at 128000 is reused unchanged, with its actual request and response retained. It used627 output tokens and finished normally. Do not claim exact reproduction of every generation setting. Reject truncated/incomplete replies and stop, with no automatic cap increase or model substitution. Original prompt words, full supplied input and reasoning settings are unchanged.

Budget ceiling $3 including the reused $0.1410575 call, enforced by conservative per-request reservations. No automatic retries. No new condition, prompt tuning, routing, classifier test or full520 run. The earlier blocked20-case experiment remains untouched. No credit purchase or top-up is required or authorized by this run.

Primary result is publisher-rule success on these four replays, category breakdown, action labels and over-scaffolding. Four cases are an implementation check, not an accuracy estimate or a refutation/confirmation of the published520-case leaderboard. Report actual usage, cap hits, costs and all prompt/model/infrastructure differences. Differences from publisher additionally include OpenRouter access for Claude, synchronous unbatched scoring/nonstreaming calls and possibly changed undated aliases. Do not compare latency.
