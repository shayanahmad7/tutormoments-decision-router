# Coding Mathematical Work in Tutor Responses

Version 2.0. Frozen before the independent coding round on October 21, 2026.

## Task and unit

Read the preceding mathematics conversation and each candidate tutor response. Code what the response explicitly asks or leaves the learner to do next. The unit is the first tutor response block, ending at the next learner message or observed learner action. Consecutive tutor utterances are merged. Screen annotations and pauses are excluded from the response text. The original preceding context can include them as context, not spoken words.

The packets do not identify response sources. Do not use guesses about the tutor source as a coding criterion. Complete your first pass before opening another coder's worksheet, the AI-coded results, or the source key. Each response needs your own judgment, a short exact excerpt, and a reason. Do not copy a label from a similar-looking response without reading its context.

The 24-record context window is a reading aid, not an information restriction. Consult Full Preceding Contexts.json for a case whenever the task, a number, previous answer, or a diagram is unclear. Do not use future learner behavior or publisher evaluative labels.

## Work left

- W0: no new mathematical action is elicited. Confirmation, passive listening, assent, copying, repeating an answer, or choosing an answer already supplied. A complete explanation ending in 'Does that make sense?' is W0 unless a separate mathematical task remains.
- W1: execute a specified calculation or recognize a heavily cued fact. A specified operation that still requires computation is work, even if easy. Identifying a result that has already been written is W0.
- W2: infer, compare, connect a representation, or explain within a narrowed path. The learner supplies a mathematical relationship or reason, not only an arithmetic result.
- W3: choose a strategy, generate an argument, diagnose an error, or plan a solution with meaningful discretion. A generic 'why?' can be W2 or W3 depending on how much of the reasoning the preceding response supplies.
- NA: the mathematical demand cannot be established from the available text, including a wholly nonmathematical exchange. Explain the missing context. Do not use NA just because the answer involves a diagram if the demand itself is clear.

Judge the most substantive unsupplied mathematical demand in the response. A question supplied with its own answer is not an unsupplied demand. A correct answer can be followed by a genuinely new explanation request. If the response moves entirely to a new problem, code the work requested in that new problem and mark new_task_shift = 1. We will analyze current-task and new-task responses separately. W3 is not automatically better than W1; appropriateness depends on learner need.

## Information supplied

answer_revelation is relative to the active mathematical demand in the preceding context, not to every possible extension.

- R0: no new answer information or confirmation only.
- R1: general concept, strategy, or representation.
- R2: a task-specific operation, intermediate value, or decisive relation.
- R3: the complete active answer or requested explanation. If the learner was asked for an equation, supplying the equation is R3 even without calculating its result.
- NA: cannot establish the demand or relevance.

## Other codes

elicitation: none, assent_or_repeat, calculation, recognition, reasoning, strategy_or_diagnosis, new_task, or uncertain.

answer_before_question: 1 if the response supplies the requested result or decisive reasoning and then asks only for an answer it has supplied; otherwise 0. A genuinely new justification or independent problem is not answer-before-question.

question_contains_answer: 1 if the tutor asks for an answer and supplies that answer in the same response, including stating both equivalent requested equations. Otherwise 0. Giving a useful clue without the requested result is not sufficient.

new_task_shift: 1 if the response moves to a different problem or mathematical task than the one at the cut; otherwise 0. A new explanation of the same result is not automatically a different problem.

correctness: correct, error, context_uncertain, or not_assessable. Check inspectable mathematics; do not assume the underlying tutor is correct. 'Not assessable' fits a response making no mathematical assertion. Mark context_uncertain if an omitted diagram or unclear transcript prevents checking.

confidence: high, medium, or low in the interpretation, not in the learning value of the response.

evidence: quote a short exact excerpt from the candidate response supporting the consequential code. rationale: explain what the learner must still supply. For an empty candidate response, use an empty evidence field and state missing spoken response in the rationale.

## Recorded coding and evidence

Two separate AI sessions applied the frozen definitions to 120 source-masked responses each. After excluding E20 and E24, the analysis uses 114 responses per run. Both original coding sets are in the results folder, with a short exact excerpt and rationale for every response. No human coding is represented in these files.

The completed response-level table retains response IDs, work-left codes, information supplied, requested action, answer-supply flags, task shifts, correctness, confidence, evidence, and rationale. Blank worksheets and training allocations are archived. They are not completed observations.

The original pre-coding manual and packets remain unchanged under Independent Coding/Blind Inputs. This reader-facing copy describes the same categories. Disagreements are retained rather than converted into a single agreed label.
