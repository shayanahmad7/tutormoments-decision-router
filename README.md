# TutorMoments: Choosing When to Help and When to Challenge

This project asks a practical question about AI math tutoring: **does deciding how to teach before generating a reply improve a small tutor?** Jev reads the conversation, chooses scaffolding or rigor, and selects detailed instructions for the tutor. We use real tutoring conversations from TutorMoments and evaluate the actual generated replies, alongside our earlier decision-only experiment.

## Latest: all six decision prompts on all 520 records

The [full-520 Jev search](experiments/jev-all-520-search/README.md) is complete: **520 decisions for each of six prompts**, or 3,120 candidate-record decisions. This extension completed the previously untested records for B, D and E and ran the new F prompt on every record. It added 1,666 Jev calls, costing **$0.45**, with no tutor generation or model judging.

Raw matches were A 372, B 329, C 376, D 375, E 373 and F 368, each out of 520. The structured prompt C remains best at **72.3%**. Searching probability thresholds gives **382/520 (73.5%)** with C and a .55 rigor cutoff. The six-prompt probability average does not beat it. All records, labels, decisions and threshold results are included in the [single comparison CSV](experiments/jev-all-520-search/All%20520%20-%20Six%20prompt%20decisions.csv).

This latest round explicitly optimizes against all 520 labels and reports full-set accuracy. It is exploratory, not a held-out validation result. The earlier split-based study and tutoring-response pilot below remain unchanged and separate.

## Separate decision experiment, 10 November 2026

The [new decision-only study](experiments/jev-decision-study/README.md) tests Jev against all 520 released scaffold/rigor labels, without generating tutor replies. Five prompt/context candidates were compared on development students, then the selected prompt and a fresh control were evaluated on the other students. Two unchanged full repeats check stability.

| Version | All 520 | Separate evaluation 382 |
|---|---:|---:|
| Previous prompt, fresh control | 372/520 (71.5%) | 278/382 (72.8%) |
| New structured prompt, first run | 376/520 (72.3%) | 274/382 (71.7%) |
| New prompt + development threshold .55 | 382/520 (73.5%) | 280/382 (73.3%) |

The new wording did not establish an improvement on evaluation students. Thresholding is separately reported probability postprocessing, not Jev's raw choice. The two additional raw repeats scored 378 and 375; voting did not improve accuracy. Three identical-input pairs carry opposite reference labels, so a consistent context-only classifier cannot reach 520/520 on this unchanged file. All labels are retained.

The study contains [all 520 decisions](experiments/jev-decision-study/All%20520%20decisions.csv), [every first-run error](experiments/jev-decision-study/Errors%20for%20review.csv), exact prompts and responses, a source-label audit, and a local conversation viewer. Total new cost: **$0.77**, 2,494 Jev requests, no tutor-generation or evaluator calls. The response-quality pilot below remains a separate experiment.

The completed [matched tutoring pilot](experiments/routing-pilot/RESULTS.md) compares a Jev-directed policy with a tutor that receives the same detailed policies and chooses for itself. Qwen3 14B and 32B provide a within-family model-size comparison. The [design](experiments/routing-pilot/PLAN.md) was frozen before generation; [execution notes](experiments/routing-pilot/EXECUTION-NOTES.md) record every correction and extension.

## New pilot: what happened

We generated 320 replies across 32 distinct students and had two independent model judges evaluate every reply. Four sampled stopping points concern non-math tasks, so the math comparison contains 28 cases. All original cases and results are retained.

| Tutor and evaluator | Detailed self-choice | Jev + detailed policy | Always use rigor policy |
|---|---:|---:|---:|
| Qwen3 14B, Gemini judge | 14/28 | 17/28 | 19/28 |
| Qwen3 14B, Claude judge | 15/28 | 19/28 | 19/28 |
| Qwen3 32B, Gemini judge | 17/28 | 23/28 | 20/28 |
| Qwen3 32B, Claude judge | 14/28 | 19/28 | 21/28 |

These are passes on our first-reply rubric, not official TutorMoments scores. Both judges favor Jev over detailed self-choice, but Jev does not consistently beat a fixed policy or a cheap LLM router. No math-only paired exact comparison above establishes a significant Jev benefit at .05. We also found no evidence of a special advantage for the smaller model or lower end-to-end delay than one tutor call. Total accounted pilot spending was **$2.59**, including evaluator checks, setup and conservative failed-request reservations.

**Interpretation:** worthwhile preliminary evidence for the course, not yet proof that context-sensitive routing improves tutoring. The strongest follow-up tests the value of the decision itself against fixed-policy and equally detailed prompting controls. Read the [findings and recommended study](experiments/routing-pilot/FINDINGS.md), [complete results](experiments/routing-pilot/RESULTS.md), and [related work](experiments/routing-pilot/RELATED-WORK.md).

Actual [replies and both judges' ratings](experiments/routing-pilot/replies-and-ratings.csv), [case-level policy results](experiments/routing-pilot/case-results.csv), and an offline [conversation reader](experiments/routing-pilot/review.html) are included. Exact requests, responses, prompt hashes, and offline verification scripts make the run auditable. Download `review.html` and open it locally; GitHub displays its source.

```mermaid
flowchart LR
    A[Conversation up to the stopping point] --> B[Jev chooses scaffold or rigor]
    B --> C[Select matching teaching instructions]
    C --> D[Small tutor generates a reply]
    D --> E[Blinded response evaluation]
```

The crucial test is whether this system beats **the same tutor with equally good instructions**, including routing delay and cost. Teacher-label routing is a diagnostic: it shows what happens when the intended category is known, but that label is unavailable in deployment. No student learning gains are measured.

There are three related experiments here:

1. **Matched Jev tutoring pilot:** first-reply quality, controlled prompts, both forced-policy outputs, routing errors, model size, cost and streaming latency. [Plan](experiments/routing-pilot/PLAN.md).

2. **Jev decision classification, completed:** give Jev the conversation available at the stopping point and ask it to choose `scaffolding` or `rigor`. Compare its choice with the dataset label. No tutor response is generated.
3. **OpenAI decision-router pilot, earlier work:** use a separate decision model to instruct a tutor LLM's next reply. This tests a different question. Its [runner and method guide](docs/openai-router-guide.md) remain available.

## Jev results

We tested **Jev 1.14.0** on all **520 moments**, evenly split between scaffolding and rigor. The first version used the publisher's evaluation-aware instructions with a short addition asking for a decision. We then compared four context-focused prompts on development cases and evaluated the selected version on the remaining students.

| Cases | Original prompt | Revised prompt |
|---|---:|---:|
| All 520 moments | 367 / 520, **70.6%** | 375 / 520, **72.1%** |
| Scaffolding moments | 200 / 260, 76.9% | 196 / 260, 75.4% |
| Rigor moments | 167 / 260, 64.2% | 179 / 260, 68.8% |
| Evaluation cases reserved for this round | 277 / 382, 72.5% | 280 / 382, 73.3% |

The revision recognized more rigor opportunities but lost a few scaffolding matches. It gained eight matches overall and three on the separate evaluation cases. The student-cluster bootstrap interval for the evaluation accuracy change was **−3.5 to +5.4 percentage points**. This is a small observed improvement, not evidence of better student learning.

## Start here

- [Jev experiment guide](experiments/jev/README.md): question, inputs, method, prompts and reproduction.
- [Original 520 decisions](experiments/jev/Jev%20decisions.csv): labels, choices, probabilities and timing.
- [Original versus revised decisions](experiments/jev/Context-focused%20prompt%20test/All%20520%20-%20Original%20versus%20optimized.csv): all paired results and development/evaluation membership.
- [Detailed prompt-comparison results](experiments/jev/Context-focused%20prompt%20test/Prompt%20test%20-%20Results.md): every candidate, examples, uncertainty, confidence, cost and timing.
- [Aggregate results](experiments/jev/Context-focused%20prompt%20test/Final%20comparison.json): machine-readable counts and confusion matrices.

## What is included

`experiments/jev/` contains the scripts, exact prompts, all four development candidates, frozen selection and split, request payloads and saved response JSON. There are 520 original responses, 552 development responses and 520 selected-prompt records. Of those selected-prompt records, 138 reuse development predictions. There were **1,454 unique successful classification requests**, rather than 1,592 new requests.

Unmodified experiment scripts are preserved under `experiments/jev/provenance/original_source/`. The runnable copies only adapt source-data locations to this repository. Predictions and result files retain their original bytes. A publication manifest records their hashes.

The repository remains private. API keys, console screenshots and billing/access records are excluded. The Jev request payloads contain excerpts from the public, de-identified TutorMoments corpus. The full upstream source is fetched separately. The older pipeline's local run directories are not part of this Jev update.

## Verify without an API key

Python 3.11 or newer. The Jev check uses only the standard library:

```sh
python3 tools/verify_jev_archive.py
```

This independently recomputes the headline counts, checks every paired CSV row and validates request hashes. It makes no network or model calls.

To check against the original source and student grouping:

```sh
python3 tools/fetch_jev_data.py
python3 "experiments/jev/Context-focused prompt test/verify_comparison.py"
```

The second command recomputes local verification summaries and the bootstrap interval. It makes no paid API calls. Source data defaults to `data/jev/`; set `TM_MOMENTS` and `TM_TRANSCRIPTS` to use existing copies. See the experiment guide before intentionally rerunning a paid experiment.

The earlier pipeline's offline tests remain:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Its source-parity test expects the original publisher ZIP at the workspace location recorded in the manifest. The Jev archive check does not require that ZIP.

## Sources and attribution

- Zhang et al. (2026), [When Help is Unhelpful: Evaluating AI Tutors for Productive Struggle](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf). [Website](https://tutormoments.allen.ai/), [dataset](https://huggingface.co/datasets/allenai/tutormoments-preview), [code](https://github.com/allenai/tutormoments).
- TypeSafe: [Jev introduction](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [quick start](https://docs.typesafe.ai/introduction/quickstart), [Choice primitive](https://docs.typesafe.ai/primitives/choice), [models](https://docs.typesafe.ai/models).

TutorMoments supplies the upstream prompts and conversation excerpts. Its Apache 2.0 license and notice remain under [third_party/tutormoments](third_party/tutormoments/). This is an independent course research project, not an official AllenAI or TypeSafe evaluation.
