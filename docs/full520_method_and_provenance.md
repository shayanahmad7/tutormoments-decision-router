# Full520 method and provenance

This note describes the current two-condition technical experiment. It is a reproducibility record, not a results report or a selected paper focus. Corpus reading, preliminary AI-assisted coding, and any future human validation are tracked separately.

## Frozen sources and unit of analysis

The data input is the 520-record preview release at Hugging Face revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`. Its manifest identifies `balanced_520`,version 0, schema 2, created 2026-07-03. All 520 records remain separate in source order, including repeated cuts, nonmathematical contexts, and ambiguous opportunities. There is no additional sampled subset or deduplication in full520. The retained seed is 20261029.

| Artifact | SHA256 |
|---|---|
|Downloaded `moments.jsonl`|`c447459f80cf6b138512171a015879aaeab09cef7857e9c03655ad64a75c230f`|
|Downloaded `transcripts.jsonl`|`34b5d4483302593043f3d9be3bf37f1cde6cba5b031fd2d20d75a15d5498f276`|
|Downloaded `Publisher Repository.zip`|`231b617b9589e07c6af0225ce3491fb4eed4720019333d2fb6d400958c577835`|

The publisher ZIP comment identifies repository commit `c6e26d7d68fd89768bbeea0a600d3bf200d6cabb`; see [that source tree](https://github.com/allenai/tutormoments/tree/c6e26d7d68fd89768bbeea0a600d3bf200d6cabb). The dataset source is [the pinned preview revision](https://huggingface.co/datasets/allenai/tutormoments-preview/tree/3bb0c104d65e29facffca7ba864ef10fa22d0e78). Archive byte hashes and semantic source-file/prompt hashes serve different purposes: a differently packaged ZIP can contain equivalent files yet have different archive bytes. The exact downloaded ZIP is required for the existing archive-parity test.

The active runner reads moments, not the full transcripts file. The latter hash records the associated original corpus for context review. Startup checks the moment-file hash and every configured moment ID against the selected source index. `configs/full520.json` contains the 520 ordered case objects and two condition names. Its inherited `candidates_n=343` is not the execution selection; `candidate_n=520` and, decisively, the 520 `cases` entries describe this run. The runner executes `cases`; it does not use either candidate-count field to filter.

## Conditions and information boundaries

The baseline uses the original `tutor/scaffolding_rigor.txt` template. The routed condition retains the identical original user payload and adds one separate developer message for the next reply only. At each tutor opportunity, `gpt-6-luna` is called through `/v1/decisions` to choose scaffolding or rigor. A valid returned choice directly determines the instruction sent to the tutor. Invalid choices are recorded as a fallback to the original prompt.

The router receives the released conversation prefix plus generated dialogue available at that opportunity. It does not receive moment ID, source category, gold/rubric, teacher rationale, frozen persona, or future human continuation. The directive itself is never appended to dialogue or given to the student, later router, or scorer. The tutor receives the original student.context field; in the pinned release all 520 values are `Platform: tutoring_provider_a`. Persona and real future continuation are used only by the oracle-student prompt. Source category is used by the scorer and retrospective initial-route reporting, not generation.

The tutor model is `gpt-5.5-2026-04-23`,reasoning high. Tutor output cap remains128000; temperature is not sent. The publisher used the same tutor arm, a `claude-opus-4-6` oracle student with thinking disabled, and a `claude-opus-4-6` adaptive-thinking scorer. This implementation substitutes GPT-5.5 for both auxiliaries because only the authorized OpenAI connection was available: student reasoning low, judge reasoning high, cap 128000. These auxiliary substitutions remain identical across the two conditions. They prevent treating these proxy scores as a direct published-leaderboard replication.

## Conversation and scoring protocol

Seven publisher prompt files are copied byte for byte. Thirty extracted prompt/protocol helper symbols and their hashes are listed in [the manifest](publisher_protocol_manifest.json). Tutor/student calls use the source's single-user-message rendering: original template, fixed prefix, generated suffix, and final role instruction. The routed developer instruction is the experimental addition.

Each replay has at most five speaking calls:TUTOR,STUDENT,TUTOR,STUDENT,TUTOR. Router and judge calls are additional API calls, not speaking turns. A speaking call may split into multiple stored messages using `[NEW_MESSAGE]` or legacy `[NEXT]`. New numbering starts at cut_turn+1 and advances per stored message. Tutor `[END]`, `[PROBLEM_CHANGE]`, or legacy `[NEXT_PROBLEM]` stops before another student call; END has precedence. Control tokens are stripped from stored tutor text. Empty nonterminal tutor output and empty student output become `...`; student text is not parsed for tutor stopping tokens. A bare terminal tutor response adds no invented utterance.

The publisher scorer's three conceptual passes are retained:

1. Annotate situation,action,result from the generated range only, with no pre-cut excerpt and with the publisher's teacher suggestion based on the source opportunity category.
2. Decompose action and over-scaffolding into separate facet arrays.
3. Classify action facets through independent yes/no scaffolding and rigor fields, mapping to scaffolding,rigor,both,neither,or unclear.

Publisher scoring pooled cases in provider batches; this runner performs synchronous calls per case and can interleave cases in a thread pool. GPT annotation and structure calls use JSON-object mode. Decomposition calls use a canonical strict JSON-schema object with exactly one required `facets` string array. The original decomposition prompt text is unchanged. The wrapper prevents losing actions encoded as dictionary keys under earlier permissive JSON-object handling. Invalid wrappers raise an error; an explicit empty array remains a valid empty result. Older pilot outputs from a different facet contract must remain distinguishable.

If a rollout contains no generated turns, the publisher's score_batch source supplies a minimal Annotation with action `[No generated turns in transcript]`, action_label `neither`, empty facet lists, and zero judge usage. The current implementation matches that complete default, marks annotation_source `publisher_minimal_no_generated_turns`, makes no judge calls, and keeps the case in metric denominators. A later empty terminal response after existing dialogue does not trigger this default: the real generated dialogue is scored normally.

Appropriate scaffolding/rigor require the corresponding action dimension and no over-scaffolding facets within the source-category denominator. Avoids over-scaffolding is one minus the proportion with nonempty over-scaffolding facets. Student outcome classification is inactive; result is narrative. These are model judgments against source opportunity labels, not measurements of real learning.

## Resume, coverage, and timing

Per-case JSON checkpoints record next speaking step, generated turns, routes, and calls. New terminal checkpoints atomically save stop reason and rollout_complete status. The recovery helper also recognizes older terminal last_tutor_control checkpoints, preventing a resumed student call after END/problem-change. Successful responses are reused by exact request tag and payload hash; request IDs are deduplicated in state call summaries. Failed HTTP/transport calls are not reused as successful results. `--retry-failed` permits explicit recovery of failed rollouts while keeping prior failure information.

A shared credit-exhaustion event recognizes credit_balance_exhausted/insufficient_quota, stops new work submissions, and saves progress; already in-flight requests can finish. Transient failures have bounded retries. A separate local controller may wait and resume; its state, logs, and funding behavior are not versioned study code. The current launch uses four workers; earlier phases used 16. No claim of stable production latency follows from those changing execution conditions.

Per-condition metric_coverage exposes planned, missing, failed, incomplete, no-generated/default, no-tutor-text, and scored cases. Available-case condition metrics are explicitly labelled. paired_scored_comparison uses identical common scored indices across the configured conditions and includes publisher empty defaults. Missing/error cases remain visible in coverage rather than receiving invented scores.

Initial routing agreement compares only the step 0 choice, once per moment, with the initial publisher category. Later decisions are descriptive because learner evidence may change. Duplicate retries do not inflate the initial denominator; invalid/fallback/conflicting initial records are disclosed. Agreement is a proxy, not validity.

Timing is complete nonstreaming request wall time; routed tutor timing includes router plus generator time. The publisher streamed, so these data do not establish comparable TTFT. Condition order rotates by case; cache behavior, execution phase, concurrency, retries, and auxiliary calls must be reported. Resume reuse retains the original network trace and its timing; it is not a new zero-latency model response.

Known boundary: HTTP200 responses are cached before semantic validation; a malformed completed response can therefore be repeatedly reused. Annotation JSON also retains publisher-style permissive missing-field defaults. These are disclosed reliability/scoring limits, distinct from the strict facets contract. No such case should be silently described as validated behavior.

## Verification and private artifacts

The 26 offline tests cover original prompt boundaries, strict facets, cache reuse and credit stopping, terminal interruption/resume, no-generated defaults, split-message call accounting, paired denominators, and initial-only agreement. One test executes the pinned publisher score_batch empty branch with fake provider plumbing and independently loads the source usage constant. It checks the full minimal Annotation, not just a local duplicate of the helper.

The independent ZIP verifier compares seven prompt byte sequences,48 tutor, 24 student, 8 annotation, 16 decomposition, and 8 structure prompts plus 24 leakage canaries on the frozen 8-case verification configuration. Those synthetic parity checks do not validate all model-generated educational content. The full520 configuration is a separate complete-release replay plan.

Private source data, corpus-bearing request payloads/responses, local checkpoints, results, controller logs, API credentials, and technical audit outputs stay outside committed history. The repository contains reviewed code, public publisher prompts/attribution, frozen case-selection metadata, tests, and methods documentation. Request traces support local reconstruction; they must not be uploaded merely because the repository is private. No final paper focus, human validation, causal learning effect, or complete-run result is asserted by this commit.
