# Context-focused Jev prompt test

29 October 2026

The question is whether clearer instructions about the learner's current mathematical work improve Jev's agreement with the TutorMoments labels. Model, full conversation text, endpoint and two possible outputs remain the same as the original 520-case experiment. Only the classification prompt and descriptions of its two options change.

## Development and evaluation

The original transcript metadata link 520 benchmark records to 89 students. Eighteen students, accounting for 138 moments, form the development set. All students from the specific examples already inspected in the first round are assigned to development. The remaining students are assigned using seed 2026102902. The evaluation set contains 382 moments from 71 different students. No student or duplicate conversation cut appears on both sides.

The full corpus and original predictions were reviewed earlier. Evaluation is held out from this round's prompt selection; it is not a pristine, previously unseen external test set.

Three candidate prompts are written and frozen before any new calls. They differ in how explicitly they define evidence of unresolved difficulty, demonstrated understanding, independent work and the current task. One uses structured criteria supported by the TypeSafe Choice API. They contain no source-case quotations, record IDs, teacher rationales, reference labels or case-specific overrides.

Candidate selection uses development balanced accuracy, then macro F1, overall accuracy, shorter prompt and candidate name. Balanced accuracy is used because the development set is not balanced between labels. At most four candidates are permitted; any added candidate must be documented as a development-only revision before evaluation. The selected wording is frozen before any new evaluation predictions. Evaluation results will not be used to alter it in this round.

The selected prompt receives a decision for every one of the 520 moments. Exact matching development predictions are reused rather than charged twice. The 382 evaluation predictions are new calls made after selection. The old 520 decisions remain unchanged.

## Comparison

Report overall and per-label agreement, confusion matrices, and paired cases that improve or worsen. Report the evaluation subset separately from all 520. Keep the publisher labels unchanged, including ambiguous or contradictory records. A student-cluster bootstrap may describe uncertainty in the evaluation gain; it does not remove the limits of prompt selection on an already-explored dataset.

Keep the combined original and optimization API usage below the previously approved $1 cap, with no credit purchase or top-up. API failures are not valid decisions. Save raw returned JSON and exact request payloads. Credentials are loaded privately from the existing local file and never logged.

No tutor replies, student simulations or LLM judges are generated. Existing submitted reports, slides and coding workbooks are not edited.
