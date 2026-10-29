# Jev: scaffolding or rigor?

This experiment asks whether Jev can select the publisher's scaffolding-versus-rigor label from the dialogue available at the selected stopping point. It generates no tutor responses, simulated students, or judge evaluations.

## Fixed design

- Model: `jev-1.14.0`, pinned rather than a moving alias, subject to authenticated availability verification.
- Data: all 520 records from the existing pinned TutorMoments preview, 260 scaffolding and 260 rigor. The original data remain unchanged.
- Prompt: the publisher's original `scaffolding_rigor.txt` evaluation-aware tutor instructions, with the original student-context substitution. Add only a request to return a decision instead of a tutor response.
- Jev interface: one Choice question per moment; options `scaffolding` and `rigor`, with no added option descriptions. The original prompt already defines both.
- Input: the complete released pre-cut conversation, with roles and original turn numbers. Do not send the benchmark label, teacher rationale, rubric, original future continuation, student persona, identifiers, or annotation metadata.
- No prompt tuning against the benchmark. All outputs, probabilities, confidence, model identity, usage, timing and exact request hashes are saved.
- Initial technical checks use the same frozen prompt. Successful predictions remain in the final results; they are not discarded or rerun to improve the score.
- Network: TypeSafe's documented API only. No OpenAI calls. The per-launch spending ceiling is $1 of existing account credit; no purchase, subscription or automatic top-up is authorized by the program.

## Evaluation

Primary: reference-label agreement across all 520 published records. Report the confusion matrix and separate scaffolding/rigor recall, macro F1 and balanced accuracy. The balanced benchmark's constant-label baseline is 50%.

Secondary: probability/Brier summaries; accuracy and coverage at prespecified top-probability thresholds of .75, .90 and .95; a duplicate-cut sensitivity analysis retaining the first record of each consistently labelled cut and excluding conflicting-label cut groups; and the same first 49 records used in the earlier Decisions experiment. The earlier model received a different prompt, so this is a descriptive comparison, not an isolated model-effect estimate.

Accuracy means agreement with the publisher's labels. It does not establish the best possible teaching action or effects on student learning. Records share students and sessions, so they are not 520 independent participants. Inspect examples and ambiguity after predictions are frozen; do not rewrite the prompt to fix observed errors in this run.

## Reproducibility

`Frozen experiment.json` records source/template/request hashes. `Requests.jsonl` contains the exact payloads; `Reference labels.csv` is kept separate and is used only by local scoring. `Responses/` preserves the returned API JSON. `Jev decisions.csv` is the readable case-level result, and `Results.json` contains aggregate results. Credentials belong only in a local `.env` file, excluded from Git.

The original template is an unchanged Allen Institute for Artificial Intelligence TutorMoments resource, Apache-2.0. See the preserved publisher repository and its LICENSE/NOTICE in the adjacent decision experiment.

## Documentation checked on 29 October 2026

- https://docs.typesafe.ai/introduction/quickstart
- https://docs.typesafe.ai/primitives/choice
- https://docs.typesafe.ai/api/system-one
- https://docs.typesafe.ai/api/list-models
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/confidence
- https://docs.typesafe.ai/api/errors

The official documentation is saved in `Documentation/`. Jev's structured question API differs from a chat API: the tutor instructions are placed in the Choice instructions and the conversation in state. The tutoring prompt text is preserved; only the output task and API packaging change.
