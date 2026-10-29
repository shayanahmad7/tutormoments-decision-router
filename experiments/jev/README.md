# Jev: Scaffolding or Rigor?

## What we wanted to find out

At a particular point in a math tutoring conversation, should the tutor make the task more accessible, or ask the learner to do more independent thinking? We tested whether Jev can make that choice using the preceding conversation.

This experiment measures **choice of instructional direction**. It does not generate hints, simulate learners or evaluate a completed tutoring exchange. The earlier OpenAI router is separate.

## Data and inputs

We used 520 moments from the pinned TutorMoments-Preview release: 260 scaffolding and 260 rigor. Each moment supplies the full released conversation up to its stopping point. The publisher's `dimension` label is the scoring reference.

Each request uses `jev-1.14.0`, the conversation as state, and one Choice question named `next_move`, with options `scaffolding` and `rigor`. Teacher rationales, reference labels, future human continuations and learner personas are excluded from requests. All 520 records are retained, including duplicate stopping points and ambiguous examples.

## Original prompt

We preserved the publisher's evaluation-aware tutoring instructions and platform metadata substitution, then added a short instruction to return a decision instead of a tutor response. Option descriptions were empty because the original instructions already explain the distinction.

Read [Exact prompt.txt](Exact%20prompt.txt), [the plan](Experiment%20plan.md), [the findings](Jev%20results%20-%20Read%20me%20first.md) and [Results.json](Results.json). Jev matched **367 / 520 labels, or 70.6%**.

## Context-focused prompt comparison

Eighteen students, accounting for 138 moments, were assigned to development. The other 71 students, accounting for 382 moments, were reserved for evaluation. Previously inspected example students were placed in development. No student appears in both sets.

Three candidates were frozen initially; a fourth was added after reviewing development disagreements. Selection used development balanced accuracy, then macro F1, accuracy and the stated tie-breakers. Candidate A was selected and frozen before new evaluation requests. Its 138 development predictions were reused, and 382 new requests completed its 520-case result.

The selected prompt asks Jev to follow the current mathematical task, distinguish student reasoning from tutor-supplied reasoning, and interpret recent contributions in context. A student's yes after an explanation is not independent mastery; an earlier mistake does not imply a permanent need for help.

The revised prompt matched **375 / 520 labels, or 72.1%**. On the evaluation cases, the original matched 277 and the revision matched 280. The dataset and original predictions had been inspected previously, so these cases were held out from this prompt-selection round, not from all earlier exposure.

Read [the selected prompt](Context-focused%20prompt%20test/Selected%20prompt.txt), [all candidates](Context-focused%20prompt%20test/Frozen%20candidate%20prompts.json), [the paired CSV](Context-focused%20prompt%20test/All%20520%20-%20Original%20versus%20optimized.csv) and [the complete findings](Context-focused%20prompt%20test/Prompt%20test%20-%20Results.md).

## Files

| File or folder | Contents |
|---|---|
| `Jev decisions.csv` | Original choices, labels, probabilities, confidence, timing and token usage. |
| `Reference labels.csv` | Zero-based moment indices and upstream identifiers. |
| `Requests.jsonl` | Exact original payloads for all 520 moments. |
| `Responses/` | All 520 original API responses and request hashes. |
| `Context-focused prompt test/Development/` | All 138 responses for each of four candidates. |
| `Context-focused prompt test/Full rerun/` | All 520 selected-prompt records, including 138 reused predictions, with exact payloads. |
| `Context-focused prompt test/Final comparison.json` | Overall, per-label, development and evaluation counts. |
| `Context-focused prompt test/Student-cluster uncertainty.json` | Bootstrap seed, method and evaluation interval. |
| `provenance/publication_manifest.json` | SHA-256 hashes for copied experiment files. |
| `provenance/original_source/` | Unmodified experiment scripts. |

`correct` means agreement with the publisher label, not a new human validation. Top-option probability and the API confidence field are distinct values.

## Reproduce the calculations

From the repository root, without a key or network:

```sh
python3 tools/verify_jev_archive.py
```

For full source and student-group verification:

```sh
python3 tools/fetch_jev_data.py
python3 "experiments/jev/Context-focused prompt test/verify_comparison.py"
```

Set `TM_MOMENTS` and `TM_TRANSCRIPTS` to use existing source files instead of `data/jev/`. Source-data paths are the only adaptations to the archived scripts. Verification recomputes local summary JSON files without calling Jev.

To reconstruct original payloads and scores from saved responses:

```sh
python3 experiments/jev/jev_experiment.py prepare
python3 experiments/jev/jev_experiment.py score
python3 "experiments/jev/Context-focused prompt test/optimize_jev.py" report
```

A deliberate paid rerun should use a separate copy so this completed archive remains intact. Set `TYPESAFE_API_KEY` in the environment and use the script's `run`, `development` or `full` command. Saved responses are reused by default. The original runner's `--budget-usd` is a per-launch byte-based guard; the optimization runner checks accumulated recorded token usage against $1. Neither is a provider-side account cap. No API call is needed to inspect or reproduce the existing calculations.

## What the results mean

The revision gained 12 rigor matches and lost four scaffolding matches. In evaluation, 33 decisions improved and 30 worsened. The student-cluster bootstrap interval includes no change. Confidence increased much more than accuracy. These findings motivate another experiment; they do not establish better learning.

Observed median request times were 209 ms for the original and 195 ms for the selected prompt. This was not a controlled latency trial. Total usage across both rounds was approximately $0.448 at the documented input-token rate, not a final invoice.

The publisher's appropriate-scaffolding and appropriate-rigor scores also penalize over-scaffolding. They are not the same as this label-agreement measure. A tutor response may contain both strategies; Jev selected one direction.

See the [root README](../../README.md#sources-and-attribution) for sources and attribution.
