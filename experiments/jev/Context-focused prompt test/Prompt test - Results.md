# Jev prompt optimization: results

29 October 2026

The revised prompt matched **375 of 520 published labels (72.1%)**, compared with **367 of 520 (70.6%)** using the original evaluation-aware prompt. The observed gain is eight additional correct decisions, or 1.5 percentage points. It mostly comes from recognizing more rigor opportunities.

The gain is smaller on the cases reserved for evaluation in this round: **280 / 382 (73.3%)**, compared with **277 / 382 (72.5%)**. That is three additional correct decisions. The result supports a small observed improvement, not a strong claim that prompt optimization has made Jev substantially more reliable.

## What changed in the prompt

The selected prompt asks Jev to identify the current mathematical task, follow the sequence of learner contributions and tutor help, and distinguish who supplied the reasoning. It gives recent substantive work greater weight while retaining the earlier conversation needed to interpret it.

Two boundaries are explicit: a student saying yes after the tutor explains is not independent evidence of understanding; and an earlier error does not justify continuing to help after the student has independently corrected and explained it. The two option descriptions distinguish a current unresolved obstacle from readiness for independent work, explanation, connections or transfer.

The complete selected wording is in **Selected prompt.txt**. Its instructions begin:

> Which next tutoring move best fits what the learner has demonstrated on the current math task? Read the sequence of student work, tutor help, and described screen actions. Give greatest weight to the current task and the most recent substantive student contribution, using earlier turns to interpret it.

The model remained Jev 1.14.0. Each moment retained exactly the same full conversation text as the original run. Only the classification instructions and the two option descriptions changed. No benchmark label, teacher rationale, future continuation or learner persona was sent to Jev.

## How the wording was chosen

The 520 moments represent 89 students. Eighteen students, accounting for 138 moments, were assigned to development. The 71 remaining students, accounting for 382 moments, were reserved for evaluation. Students from specific examples already inspected in the first round were placed in development. No student appears in both sets.

Three versions were frozen and tested first. One final version was then written after examining development-only disagreements. All four were compared on the same development cases. The final selection used balanced accuracy so that the more common rigor label in the development set would not dominate the choice.

| Development prompt | Correct / 138 | Accuracy | Balanced accuracy |
|---|---:|---:|---:|
| Original evaluation-aware prompt | 90 | 65.2% | 65.1% |
| A: Current learner evidence, selected | 95 | 68.8% | 67.2% |
| B: Explicit context checks | 92 | 66.7% | 63.4% |
| C: Observable evidence criteria | 96 | 69.6% | 66.9% |
| D: Support versus demonstrated readiness | 75 | 54.3% | 62.2% |

C had one more correct development decision than A, but A balanced the two labels slightly better, so A was selected under the rule set before testing. D strongly favored scaffolding: it matched 47 / 51 scaffolding cases but only 28 / 87 rigor cases. Making the wording more detailed did not consistently help.

A was frozen before any new evaluation predictions. Its 138 exact development responses were reused, and 382 new evaluation requests completed the 520-case result. No evaluation results were used to change the wording.

The corpus and original predictions had been reviewed previously. These 382 cases were held out from this round's prompt selection, not from all earlier exposure to the dataset. This remains an exploratory comparison.

## All 520 moments

| Measure | Original | Revised |
|---|---:|---:|
| Overall agreement | 367 / 520, 70.6% | 375 / 520, 72.1% |
| Scaffolding agreement | 200 / 260, 76.9% | 196 / 260, 75.4% |
| Rigor agreement | 167 / 260, 64.2% | 179 / 260, 68.8% |
| Macro F1 | 0.705 | 0.721 |

The revised prompt matched 12 more rigor labels and four fewer scaffolding labels. Looking at the paired records, it corrected 49 previous disagreements but changed 41 previous matches into disagreements. Both prompts matched the reference on 326 cases, and both disagreed with the reference on 104 cases.

## Separate evaluation cases

| Measure | Original | Revised |
|---|---:|---:|
| Overall agreement | 277 / 382, 72.5% | 280 / 382, 73.3% |
| Scaffolding agreement | 167 / 209, 79.9% | 165 / 209, 78.9% |
| Rigor agreement | 110 / 173, 63.6% | 115 / 173, 66.5% |

In evaluation, 33 cases changed from disagreement to agreement and 30 changed in the opposite direction. A 10,000-replicate student-cluster bootstrap gives a descriptive 95% interval of **-3.5 to +5.4 percentage points** for the evaluation accuracy change. This interval includes no change. It accounts for shared students within this sample, but not all uncertainty from prompt selection, previous benchmark exposure or repeated API sampling.

## What changed in actual conversations

The following are evaluation cases, selected after the wording was frozen. The indices are zero-based, matching the CSV. Two high-probability examples were inspected in each paired outcome direction.

- **Index 298, a corrected disagreement:** the student confidently says area involves adding sides and perimeter involves multiplying them. The original prompt selected rigor. The revised prompt selected scaffolding, with probability .90, matching the reference. This illustrates the intended distinction between speaking confidently and showing correct mathematical understanding.
- **Index 199, a corrected disagreement:** after discussing angle definitions, the student says an acute and an obtuse angle are the same size. The original selected rigor; the revised selected scaffolding, with probability .88, matching the reference.
- **Index 89, a lost match:** after initially guessing and then calculating an addition, the student gives 920 for 872 + 48. The original selected rigor; the revised selected scaffolding, with probability .80. The published label is rigor and calls for verifying through calculation. Reading the stopping point matters: the calculation is already present in the available context, so the disagreement is not simply evidence of an obviously inappropriate teaching decision.
- **Index 244, a lost match:** following substantial tutor modelling of 2 × 3 using dots, the student answers six. The original selected scaffolding; the revised selected rigor, with probability .78. The reference calls for scaffolding. The revised prompt still sometimes treats a correct response after heavy guidance as sufficient readiness for challenge.

The publisher labels were retained unchanged. These are label-agreement counts, not measures of subsequent learning or a new adjudication of the reference labels.

## Confidence, speed and cost

Average top-option probability rose from **67.6% to 79.4%**, while agreement rose from 70.6% to 72.1%. The revised prompt became more confident by much more than it became accurate. Its rigor-probability Brier score nevertheless improved slightly, from 0.204 to 0.197.

At top-option probability of at least .90, the revised prompt retained 175 cases and matched 150 (85.7%). At .95, it retained 97 and matched 79 (81.4%). Higher reported probability was therefore not a guarantee of higher observed accuracy in these subsets.

The selected prompt's median measured request time was **195 ms**, versus 209 ms in the original run. This is one observed timing comparison, not a controlled latency benchmark.

The new round used **934 new classification API calls**: 552 development requests across four candidates, plus 382 evaluation requests for the selected prompt. The selected prompt's 138 development decisions were reused rather than charged twice. The usage-based estimate for this round is **$0.286**. Combined with the original 520-case experiment, the total is **$0.448**, below the approved $1 cap. No credit purchase or automatic top-up was performed by the experiment.

## Saved evidence

- **All 520 - Original versus optimized.csv** contains the paired decisions, subset membership, labels, correctness and revised probabilities.
- **Selected prompt.txt** contains the full instructions and criteria actually sent.
- **Final comparison.json** contains all aggregate results and all development scorecards.
- **Full rerun/Requests.jsonl** and **Full rerun/Responses/** preserve the exact selected-prompt requests and returned JSON.
- **Development/** preserves the other candidate runs.
- **Final verification.json** records the checks across all 520 selected-prompt decisions and all 552 development decisions.

All 520 selected-prompt states were verified as identical to the original conversation inputs. Selection preceded every new evaluation request. The original 524 result and response files retain their saved hashes. The original dataset, submitted report, presentation and coding workbook were not edited.
