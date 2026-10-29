# Publisher protocol extraction

The adapter copies seven public publisher prompts byte for byte and 30 prompt/protocol helper symbols unchanged from the local `Publisher Repository.zip`. The archive SHA-256 is `231b617b9589e07c6af0225ce3491fb4eed4720019333d2fb6d400958c577835`. [The manifest](publisher_protocol_manifest.json) records every prompt hash, full source-file hash, and extracted symbol's source line range and hash. Apache 2.0 license and original attribution are included under `third_party/tutormoments`.

`publisher_protocol.py` is an adapter: new dictionary/API wrappers surround unchanged extracted functions. It makes no API requests. Original baseline text remains unchanged; a routed condition adds one separate developer message scoped to the next tutor reply and removes that instruction from all subsequent dialogue, student and scorer inputs. The router allowlist contains only the actual available conversation entries and generated dialogue. It excludes source dimension, gold/rubric, rationale, persona and future continuation.

## Exact roles and stopping

The original tutor arm is `gpt-5.5-2026-04-23`, reasoning high. The publisher client uses Chat Completions with a **single user message**, concatenating rendered instruction template, fixed context, generated suffix and final role instruction. It sends no temperature. Its uncapped default resolves to 128000 output tokens; a lower pilot cap would be another deviation. Original execution streams, so a nonstreaming runner can report complete-call latency but cannot claim publisher-comparable TTFT.

The default five speaking turns mean **five LLM calls total**: tutor, student, tutor, student, tutor. Multiple `[NEW_MESSAGE]` or legacy `[NEXT]` splits count as several stored turns but one speaking call. Generated numbering starts at `cut_turn+1`. Tutor `[END]` ends the rollout; `[PROBLEM_CHANGE]` or legacy `[NEXT_PROBLEM]` also end it, with END taking precedence. Tokens are removed before storing tutor text. Empty nonterminal tutor output and empty student output become `...`. Student output is split without parsing tutor stop tokens.

The original oracle student is `claude-opus-4-6`, thinking disabled, and consumes the frozen released `student.trait.persona`, the real post-cut `student.reference`, and `student.context`. It must not regenerate traits. The real continuation and persona belong only to that oracle, never to the router or either baseline tutor.

## Scoring

The original scorer is `claude-opus-4-6`, adaptive thinking. It runs three pooled batch passes:

1. Annotate with `scorer/annotate/scaffolding.md`, producing situation/action/result strings. The excerpt includes **only generated turns**, with no pre-cut context, plus the publisher's gold-category teacher suggestion. The same scaffolding lens handles both categories.
2. Decompose tutor action and over-scaffolding into string arrays in two calls. The latter uses situation, action and result. Missing/junk input skips the appropriate call. A nonempty over-scaffolding array is the over-scaffolding indicator.
3. Classify action facets using `scorer/structure/classify_action.md`, giving independent yes/no scaffolding and rigor fields. These map to scaffolding, rigor, both or neither; missing fields map to unclear. No action facets defaults to neither.

The retained student-outcome prompt is **inactive** in this scorer. Effectiveness remains narrative in result; it is not a separate active numeric outcome. Appropriate scaffolding/rigor require the corresponding action dimension and no over-scaffolding spans within the appropriate category denominator. Avoids over-scaffolding is one minus the fraction with nonempty spans. These are model judgments against publisher opportunity labels, not validated student learning gains.

## Current pilot deviation

The authorized account currently has only OpenAI access. The runner therefore substitutes the same original GPT-5.5 model for the Claude oracle and judge, retaining their prompts and five-call protocol. Auxiliary model substitution, OpenAI reasoning parameters, synchronous scoring and nonstreaming timing must be reported. These results are a prompt/protocol adaptation and exploratory comparison, **not a direct replication of the published leaderboard**. The runner owns these choices and records actual request payloads locally outside Git.

## Verification

`tools/verify_publisher_protocol.py` independently executes source functions from the original archive and compares adapter outputs for all eight frozen pilot cases. The saved verification checks seven unchanged prompt byte sequences, 48 tutor prompts, 24 student prompts, 8 annotate prompts, 16 decomposition prompts, 8 structure prompts and 24 router leakage canaries. No corpus text is written to its result file. It also checks that adding routing leaves the original user payload unchanged.

Current full520 conditions, source hashes, proxy auxiliaries, canonical facets, terminal/default recovery, initial-only route agreement, coverage denominators, and private-artifact boundaries are recorded in [the full520 method and provenance note](full520_method_and_provenance.md). Corpus close-reading coverage is tracked separately outside this repository; replay completion is not human validation.


## Current reliability and output contract

The OpenAI decomposition adapter now requires a canonical strict facets-array wrapper while retaining the original prompt text. A bare terminal reply creates no dialogue message; an entirely empty rollout receives the publisher's minimal neither Annotation without judge calls and remains in the denominator. Terminal checkpoints are atomic and legacy last_tutor_control terminal checkpoints are recovered before another speaking call. Matched comparisons use the explicitly reported common scored set. Initial route/category agreement uses step 0 only; later choices are descriptive. See the linked method note for exact boundaries and known cache/annotation limitations.
