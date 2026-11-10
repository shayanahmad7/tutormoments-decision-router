# Can Jev choose scaffolding or rigor accurately?

Completed 10 November 2026. This is a separate decision-only experiment. Jev receives the past conversation and returns a category. No tutor reply, student simulation or model judge is involved. Correctness here means agreement with the released reference label.

**The new prompt did not establish a reliable improvement.** Its first run matched 376/520 labels. A development-fitted probability threshold reached 382/520, but only two more evaluation cases than the fresh control. Both paired uncertainty intervals include no improvement. We did not reach 100%, and identical-input label conflicts prevent a consistent context-only classifier from doing so on the unmodified file.

## Full comparison

| Version | All 520 records | Separate 382 evaluation records |
|---|---:|---:|
| Original publisher-style prompt, archived | 367/520 (70.6%) | 277/382 (72.5%) |
| Previous selected prompt, archived | 375/520 (72.1%) | 280/382 (73.3%) |
| Previous selected prompt, fresh control | 372/520 (71.5%) | 278/382 (72.8%) |
| New structured prompt C, first run | 376/520 (72.3%) | 274/382 (71.7%) |
| New prompt + development threshold .55 (postprocessing) | 382/520 (73.5%) | 280/382 (73.3%) |

The all-520 number includes 138 development cases and is descriptive. The evaluation column excludes those students from this round’s prompt selection. The corpus was already explored in previous work, so it is not an unseen external benchmark.

## What changed in the decisions

| Version | Scaffolding matched / 260 | Rigor matched / 260 |
|---|---:|---:|
| Previous selected prompt, fresh control | 203/260 | 169/260 |
| New structured prompt C, first run | 181/260 | 195/260 |
| New prompt + .55 threshold | 190/260 | 192/260 |

The structured prompt shifted toward rigor. It found more rigor opportunities but missed more scaffolding needs. The threshold changes the rule to choose rigor only when its returned probability is at least .55; it is not Jev’s raw returned choice and is reported separately.

## How the prompt was selected

We kept the previous split: 138 moments from 18 development students, and 382 moments from 71 other students. Five candidates were frozen before live calls. Selection used development balanced accuracy, which gives each category equal weight despite the development set containing 51 scaffold and 87 rigor cases.

| Candidate | Input and instructions | Correct / 138 | Balanced accuracy |
|---|---|---:|---:|
| A | Previous selected prompt, fresh control | 94/138 | 67.4% |
| B | Instructional opportunity | 92/138 | 57.3% |
| C | Structured criteria and illustrative examples | 102/138 | 69.6% |
| D | Structured criteria, current-task window | 101/138 | 68.6% |
| E | Structured criteria, full history plus recent focus | 99/138 | 67.0% |

C was frozen before new evaluation predictions. It uses full history, separate descriptions of the two choices, boundary cases and invented illustrative examples. The shorter context and repeated recent-context versions did not beat it on development. Exact instructions are in [selected-prompt.json](selected-prompt.json); all candidates are in [frozen.json](frozen.json).

## Does the evaluation support improvement?

| Comparison on the 382 evaluation records | Net accuracy change | Student-cluster 95% interval | Fixed / newly wrong |
|---|---:|---:|---:|
| New prompt versus fresh control | -1.05 pp | -3.98 to +1.66 pp | 16 / 20 |
| New prompt + threshold versus fresh control | +0.52 pp | -2.52 to +3.23 pp | 16 / 14 |

Intervals resample whole students, 10,000 times. The threshold was fitted using development only, after the main prompt selection and before examining evaluation scores. It was a secondary amendment. Its leave-one-student-out development balanced accuracy was 64.2%, indicating unstable threshold selection across this small development group. These results do not justify declaring a new superior classifier.

## Repeatability, without choosing the best run

| Unchanged new-prompt run | All 520 | Evaluation 382 |
|---|---:|---:|
| Run 1 | 376/520 (72.3%) | 274/382 (71.7%) |
| Run 2 | 378/520 (72.7%) | 275/382 (72.0%) |
| Run 3 | 375/520 (72.1%) | 274/382 (71.7%) |
| Majority vote of three | 374/520 (71.9%) | 273/382 (71.5%) |
| Mean probability of three, cutoff .50 | 375/520 (72.1%) | 273/382 (71.5%) |

The three runs agreed on 507/520 decisions. The two extra repeats were an explicitly post-primary stability check; no prompt was changed and no best-run score was substituted for the first run. Voting and averaging did not improve the result. The earlier selected prompt’s archived and fresh calls agreed on 495/520 decisions.

## Why 100% is the wrong target for this released file

The 520 records contain 491 distinct conversation inputs. Three identical-input pairs have opposite labels: indices 69/70, 366/367 and 410/411 (zero-based). A consistent context-only decision cannot match both members of any pair. Its theoretical maximum agreement on this file is therefore 517/520, or 99.4%. This is an upper bound, not performance achieved by Jev. It does not explain the many remaining mismatches.

Removing the six conflicting records leaves 373/514 (72.6%) for the new prompt. Keeping one representative of each non-conflicting context gives 349/488 (71.5%). The main score retains every record.

A separate note screen found 37 records mentioning only the opposite category. Assistant reading flagged 23 as explicit opposite recommendations; the others involve negation, prior help or descriptions of tutor behavior. This is not an exhaustive semantic audit or human adjudication. For example, record 375 has the category rigor, while its representative note recommends scaffolding for confusion. Record 332 has the category scaffolding while its note recommends rigor.

The [publisher schema](https://huggingface.co/datasets/allenai/tutormoments-preview/blob/main/moments.schema.json) says the category is an aggregate judgment and the note is one representative annotator’s situation text. A disagreement is a reason to trace the original annotations, not permission to silently flip the label. We kept all labels unchanged. See [Annotation notes for review.csv](Annotation%20notes%20for%20review.csv).

## Confidence is useful but not a guarantee

| Minimum returned top probability | Correct / accepted, all 520 | Coverage | Correct / accepted, evaluation |
|---|---:|---:|---:|
| 0.75 | 262/323 (81.1%) | 62.1% | 196/238 (82.4%) |
| 0.9 | 127/147 (86.4%) | 28.3% | 95/107 (88.8%) |
| 0.95 | 64/73 (87.7%) | 14.0% | 52/56 (92.9%) |
| 0.99 | 7/7 (100.0%) | 1.3% | 5/5 (100.0%) |

At .99 the seven accepted records happen to be correct, but 513 records are not covered. That is not 100% accuracy on the dataset, and such a small subset cannot establish a dependable guarantee. These thresholds were specified before the run.

## What to keep for the study

Use this as the separate decision-classification experiment. The practical finding is roughly 72–73% agreement with the released labels, with a support-versus-challenge trade-off and some unstable decisions. Better wording alone has not solved the task. Do not replace the existing prompt on the strength of these small changes.

A useful next step is to review source-label disagreements with human raters, then test a selective system that makes confident decisions and defers uncertain ones. Any prompt or threshold revisions should be fitted on development data and checked on fresh students or another corpus. The question of whether a selected decision improves the generated tutoring response remains the separate [routing pilot](../routing-pilot/RESULTS.md).

## Files, cost and reproduction

- [All 520 decisions.csv](All%20520%20decisions.csv): reference, raw Jev choices, repeats, thresholded choices and probabilities.
- [Errors for review.csv](Errors%20for%20review.csv): all first-run new-prompt mismatches, without deleting difficult records.
- [Case examples](CASE-EXAMPLES.md): source exchanges selected by the fixed example rule.
- `review.html`: download and open locally to inspect any of the 520 conversations and the saved decisions.
- [Plan](PLAN.md), [execution notes](EXECUTION-NOTES.md), [analysis checks](ANALYSIS-CHECKS.md), [machine-readable results](results.json).
- `traces/`: every exact request and response. No credentials or future continuations were sent.
- Source conversations and annotations: AllenAI and collaborators, TutorMoments-Preview, CC BY 4.0. Pinned revision `3bb0c104d65e29facffca7ba864ef10fa22d0e78`. CSV/HTML files reorganize excerpts and add our predictions; original source labels are unchanged. [Dataset license and attribution](https://huggingface.co/datasets/allenai/tutormoments-preview).

There were 2,494 successful Jev calls: 690 development calls, 764 evaluation calls and 1,040 unchanged repeat calls. The selected and control full runs each reuse their 138 actual development outputs. Total estimated input-token cost was **$0.7652**, below the $2 cap. No tutor-generation or judge calls. Median primary selected-request time was 192 ms; concurrent service timing is descriptive only.

Offline reproduction, with the pinned source files present:

```sh
python3 experiments/jev-decision-study/analyze.py
python3 experiments/jev-decision-study/annotation_audit.py
python3 experiments/jev-decision-study/build_report.py
python3 experiments/jev-decision-study/verify.py
```

Paid commands are explicitly separate (`run.py develop`, `run.py evaluate`, `repeat.py`). Do not overwrite this archived run to test another prompt. The raw API model was pinned to `jev-1.14.0`. [TypeSafe Choice documentation](https://docs.typesafe.ai/primitives/choice), [model and pricing](https://docs.typesafe.ai/models), [TutorMoments paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [dataset](https://huggingface.co/datasets/allenai/tutormoments-preview).
