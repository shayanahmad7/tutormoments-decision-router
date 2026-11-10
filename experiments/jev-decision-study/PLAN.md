# Jev alone: choosing scaffolding or rigor

## Material Passport
Public, de-identified TutorMoments preview; 520 publisher records. Separate decision-only experiment dated 10 November 2026. No tutor responses, simulated students or model judges are generated. The target is agreement with the released `dimension` field, not proof of ideal teaching. The paper describes labels derived from teachers' annotations through a classifier.

## Question and boundary
Can clearer decision instructions and better presentation of conversation context improve Jev's scaffold/rigor classification? Can it approach perfect agreement? We will report errors and contradictory input labels rather than promise 100% or keep tuning on evaluation results.

The source contains 260 scaffold and 260 rigor records. Before any new calls, audit exact model-visible context duplicates, cross-label conflicts, source hashes and student grouping. Never send `dimension`, `rubric`, provenance, row IDs, future continuation or teacher explanations as decision evidence. A record can lack information needed to recover its annotation; a disagreement is not automatically bad pedagogy.

## Fixed development process
Reuse the previous 138 development moments from 18 students and 382 evaluation moments from 71 other students. This preserves student separation. The corpus and prior outputs were already explored, including yesterday's response pilot, so this is internal evaluation held out from this round's prompt selection, not a pristine external test.

Freeze five candidates before any new model call:
1. A: the previous selected current-learner-evidence prompt, freshly rerun as control.
2. B: instructional-opportunity framing, distinguishing need for access from a chance to increase independent thinking.
3. C: structured contrasting criteria with illustrative invented examples, using the full history.
4. D: the same structured criteria with only a bounded recent/current-task window, testing whether old context distracts.
5. E: the same structured criteria with the full history plus a repeated recent window at the end, testing attention to the stopping point without removing history.

No examples copied from evaluation rows. Read development mistakes only for prompt design. Select using development balanced accuracy, then macro F1, accuracy, shorter serialized prompt and candidate ID. Include A as an eligible candidate, so a worse new prompt does not automatically replace it. Freeze the winner before new evaluation predictions. Report all development scores and the winner on all 520 rows. Reuse its actual development outputs and run the other 382. Fresh A is also evaluated on all 520, providing a same-model contemporary control; if A wins, those are the same outputs, not a second run.

## Execution and accounting
Pin `jev-1.14.0` through the TypeSafe Choice API. Exactly one binary decision per request. No tutor generation and no LLM-based correctness scoring. Cost cap $2, no purchases or top-ups. Use the existing private credential. Concurrency four, exact-payload resumability, at most three logged transient HTTP retries, preserve every failure, never regenerate a completed answer to improve accuracy. Requests and responses contain no credential headers. All 520 records get a saved decision in the selected run; repeated contexts may be sent more than once and consistency is audited.

## Measures
Main: selected versus fresh A on the 382 evaluation rows, with counts, accuracy difference and student-cluster bootstrap interval (10,000 resamples). All-520 results are descriptive because 138 records selected the prompt. Report scaffold/rigor recall, precision, F1, confusion matrix, Brier score and prespecified probability thresholds .75/.90/.95/.99. Threshold summaries always include coverage; they do not imply accuracy on rejected cases. Compare archived original and selected prompts separately, with a same-prompt repeatability check.

Audit identical-input opposite labels and compute the maximal agreement of a deterministic context-only classifier. Retain all records in the main result. Separately report one representative per non-conflicting context, 514 records after removing conflicting pairs if verified, and any known non-math sensitivity without pretending all records were manually domain-screened. Inspect improvements and regressions by a fixed rule (highest selected confidence, then index); export all 520 decisions and every error for review. No outcome-based exclusions or post-evaluation retuning.

Report timing descriptively because concurrent API calls are not a production latency benchmark. Verify exact prompt hashes, returned model, split separation, input allowlists, CSV arithmetic, total cost and old archive preservation. Keep this run separate from the tutor-response pilot.

## Sources checked today
- [TutorMoments paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), especially Figure 1 and Sections 2.1 and 3; [data](https://huggingface.co/datasets/allenai/tutormoments-preview).
- [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice): options and structured contrasting criteria.
- [TypeSafe models](https://docs.typesafe.ai/models): pinned Jev 1.14.0, $0.042 per million input tokens, free outputs.
