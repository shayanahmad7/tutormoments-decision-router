# Fresh Astra agents: decision-only replication

**14/20 correct (70%): scaffolding 6/10; rigor 8/10.** The same-input official API test also scored 14/20. Predictions agreed on 18/20. Moment 246 changed from wrong to right; moment 440 changed from right to wrong. This small diagnostic does not establish a population ranking or a significant improvement.

## What was held fixed

The existing twenty-case pilot sample and each exact API input string were retained. The sample contains ten reference categories of each kind and twenty different students. Each file includes the publisher's evaluation-aware guidance adapted to request only `scaffolding` or `rigor`, the released student metadata, and the full conversation prefix. No gold label, teacher hint, student persona or future transcript was added. The two labels in the instructions are possible outputs, not reference answers.

Before sending cases, their input hashes and source indices were saved in `frozen-inputs.json`. One fresh subagent was spawned per file, sequentially, explicitly requesting `gpt-6-astra`, high reasoning and `fork_turns=none`. The spawn message named only a neutral file, asked for one full-file read with a 20,000-token output allowance, prohibited all other files/tools/history, and requested one word. The balance and prior predictions were not disclosed. Answers were saved in sequence and scored only by the parent. Inputs are preserved under `inputs/`; responses and the scored CSV are retained separately.

This is procedural blinding, not a filesystem sandbox: subagents share the machine but were instructed to read only their assigned file. Their parent conversation was not inherited. Codex supplies its own system/tool environment, so the request text is identical but the overall inference setup is not identical to a direct API call. We did not measure or compare latency or cost across these environments. No new paid API calls were launched.

## Interpretation

The publisher's roughly 92.7% is success over a short generated tutoring exchange, allowing actions classified as both scaffolding and rigor, provided there is no over-scaffolding. It is not exclusive one-word reference-label accuracy. This diagnostic does not reproduce or refute that leaderboard result.

The same twenty cases were used in earlier exploratory tests. Treat this as a reused diagnostic sample, not a new held-out evaluation. The fixed sample and all results, including failures, are retained.

See [the complete error review](../decision-error-review/README.md) for the full-520 archives and full-context casebook.
