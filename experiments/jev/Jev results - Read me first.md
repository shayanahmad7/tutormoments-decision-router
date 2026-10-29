# Jev decisions on TutorMoments

29 October 2026

Jev 1.14.0 matched the published scaffolding-or-rigor label on **367 of 520 moments (70.6%)**. It was more successful on scaffolding cases than rigor cases. This was a standalone decision test: no tutor responses, simulated students or LLM judges were generated.

## What Jev received

We used the publisher’s original evaluation-aware tutoring prompt, with its original metadata substitution, and added only this decision instruction:

> For the conversation supplied in state, return the decision for the next tutor move: scaffolding or rigor. Make this choice using the tutoring instructions above. Return the decision rather than generating a tutor response.

The complete released conversation up to each stopping point was provided. The benchmark label, teacher rationale, rubric, future human continuation and learner persona were excluded. Jev returned one Choice answer with the two options `scaffolding` and `rigor`. Option descriptions were left empty because the original prompt already explains the distinction.

The tutoring prompt text was preserved. Its placement in Jev’s structured question API and the request for a decision replace a chat model’s response-generation interface. The exact rendered instructions are in `Exact prompt.txt`; all 520 actual request payloads are in `Requests.jsonl`.

## Results

| Published label | Correct Jev decisions | Accuracy |
|---|---:|---:|
| Scaffolding | 200 / 260 | 76.9% |
| Rigor | 167 / 260 | 64.2% |
| Overall | 367 / 520 | 70.6% |

The constant-label baseline is 50% because the release contains equal numbers of both labels. Macro F1 was 0.705.

| Published label | Jev chose scaffolding | Jev chose rigor |
|---|---:|---:|
| Scaffolding | 200 | 60 |
| Rigor | 93 | 167 |

Jev chose scaffolding 293 times and rigor 227 times. Its more common disagreement was choosing scaffolding for a record labelled rigor: 93 cases, compared with 60 in the opposite direction. These counts describe agreement with the benchmark labels, not proven teaching quality.

## Confidence, speed and cost

At a top-option probability of at least .75, Jev retained 145 / 520 cases and agreed on 116 / 145 (80.0%). At .90, it retained 31 / 520 and agreed on 26 / 31 (83.9%). At .95, it retained 11 / 520 and agreed on all 11. Those 11 cases are a small subset, so they do not establish perfect reliability.

Top-option probability and the API’s normalized confidence field are distinct. The complete values are retained in the CSV. The rigor-probability Brier score was 0.204; a constant probability of .5 would score .25 on this balanced binary task.

Median measured request time was **209 ms**. The API reported **3,853,182 input tokens**. At the documented $0.042 per million input tokens, the usage-based cost estimate is **$0.162**. This is calculated from the returned usage, rather than a final billing invoice. Output tokens are free under the documented model pricing. No OpenAI requests or credit purchases were made by the experiment.

## Comparison with the previous Decisions test

On the same first 49 source moments:

| Published label | Jev, original evaluation-aware prompt | Previous OpenAI Decisions prompt |
|---|---:|---:|
| Scaffolding | 22 / 29 (75.9%) | 27 / 29 (93.1%) |
| Rigor | 14 / 20 (70.0%) | 10 / 20 (50.0%) |
| Overall | 36 / 49 (73.5%) | 37 / 49 (75.5%) |

Jev recognized more rigor-labelled moments in this subset but fewer scaffolding-labelled moments. The previous classifier used different wording, so this is a descriptive comparison rather than a controlled estimate of which model is better. These classification scores must also be kept separate from the earlier scores for generated tutoring conversations.

## What individual cases show

The source indices below are zero-based, matching the saved CSV and publisher record order. Examples were selected by highest returned probability within each agreement/disagreement direction before interpreting their content.

- **Index 10, rigor correctly selected:** the student tests two proposed sequence rules across several terms and explains why one fails. Jev selects rigor with probability .94. The published rationale also identifies demonstrated reasoning and an opportunity to increase challenge.
- **Index 152, scaffolding correctly selected:** the tutor asks the place value of the final 9 in 599. The student says they do not know. Jev selects scaffolding with probability .98, matching the published label.
- **Index 52, scaffolding labelled but rigor selected:** the context ends with the student choosing the correct answer after a tutor’s triangle-area explanation. Jev selects rigor with probability .80. The published rationale describes uncertainty and a need for procedural support. The stopping point and the earlier difficulty need to be read together before interpreting this disagreement.
- **Index 284, rigor labelled but scaffolding selected:** the student asks for help and says they are confused. Jev selects scaffolding with probability .94. The label is rigor, but the saved teacher rationale explicitly says this is a good moment to scaffold. This is an observable label–rationale inconsistency. It remains counted as a disagreement in the prespecified results; the reference label was not changed.

These examples show why 70.6% should be described as benchmark-label agreement. Some disagreements appear to involve ambiguous timing or inconsistent references, rather than an obviously inappropriate model decision. We have not estimated the prevalence of such cases across all 520 records.

## Duplicate-cut sensitivity

The 520 published records represent 491 unique session/cut pairs. Three pairs have conflicting labels across duplicate records. Retaining the first record from each consistently labelled pair, and excluding those three conflicting groups, leaves 488 cases. Jev agrees on **341 / 488 (69.9%)**, close to the main result.

## Verification and boundaries

All 520 returned responses were verified against their exact saved request hashes. The source file remained unchanged, every payload retained its full released pre-cut context, and every returned model was `jev-1.14.0`. All 520 CSV decisions were independently checked against the raw responses and reference labels. There were no missing or failed predictions. The first two API checks are included in the 520, not counted as extra cases. No prompt changes were made after viewing predictions.

The benchmark shares students and sessions, and its labels are references rather than direct measures of learning. This experiment does not determine whether a Jev-routed tutor would teach better. The existing submitted report, presentation and coding workbook were not edited.

## Files

- `Jev decisions.csv`: all 520 decisions, reference labels, agreement flags, probabilities, confidence, timing and token usage.
- `Exact prompt.txt`: the rendered publisher prompt and the added decision instruction.
- `Results.json`: aggregate metrics.
- `Final verification.json`: completed checks across all 520 records.
- `Responses/`: original returned API JSON.
- `Requests.jsonl`: exact requests; reference labels are stored separately.

## Primary sources

- [TutorMoments dataset](https://huggingface.co/datasets/allenai/tutormoments-preview)
- [Original evaluation-aware tutor prompt](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/prompts/tutor/scaffolding_rigor.txt)
- [TypeSafe Choice API](https://docs.typesafe.ai/primitives/choice)
- [Jev model versions and pricing](https://docs.typesafe.ai/models)
- [TypeSafe probability and confidence definitions](https://docs.typesafe.ai/confidence)
