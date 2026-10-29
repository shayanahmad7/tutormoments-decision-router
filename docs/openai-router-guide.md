# TutorMoments Decision Router

A private, exploratory comparison of the same tutor model with and without an explicit teaching-decision layer. The current plan replays every record in the pinned 520-moment TutorMoments release under two conditions:

- `original_evaluation_aware`: the original publisher evaluation-aware tutor prompt.
- `evaluation_aware_plus_decisions`: the same prompt plus a separate next-reply instruction selected by Decisions at each tutor opportunity.

The tutor is `gpt-5.5-2026-04-23` with high reasoning; the router is `gpt-6-luna`. GPT-5.5 substitutes for the publisher's Claude oracle student and scorer. This is a prompt/protocol adaptation, not a direct leaderboard replication or evidence of real student learning. Final paper focus remains subject to user approval.

## Reproducibility

See [the method and provenance note](full520_method_and_provenance.md), [publisher protocol details](publisher_protocol.md), and the [exact prompt/source manifest](publisher_protocol_manifest.json). [configs/full520.json](../configs/full520.json) fixes the ordered 520 cases and two conditions; older 8-case configurations are separate pilots.

Python 3.11 or newer is required. Set `PYTHONPATH=src` or install the local package. Offline tests make no model calls:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

The source-parity regression test expects the hash-matching publisher archive at `../02 - Original Data/002 - TutorMoments-Preview/Publisher Repository.zip`. That external archive and the corpus are not bundled in this repository.

The runner requires `OPENAI_API_KEY` in the local environment and a separately acquired, hash-verified `moments.jsonl`. An authorized live run can use:

```sh
python3 run_pilot.py --source "$MOMENTS" --config configs/full520.json --workers 4 --stage all --retry-failed
```

Five speaking calls mean tutor,student,tutor,student,tutor, with earlier terminal stopping. Split messages do not add speaking calls. The 128000 output cap and source prompt text remain unchanged. Successful request traces support resume; terminal checkpoints and empty terminal rollouts follow publisher semantics. Report coverage and the common-scored-case comparison rather than treating partial unequal subsets as matched results. Initial route agreement is evaluated only at step 0; later choices can legitimately change.

## Local pipeline artifacts

The earlier OpenAI pipeline's local `data/`, `raw_responses/`, and `results/` contain private run states, corpus-bearing request/response traces, and outputs. None is committed. Credentials, environment files, local controller logs, and external source data also stay local. Use an explicit reviewed file allowlist when publishing; The separate Jev archive is described in the root README.

Public upstream sources are [AllenAI TutorMoments](https://github.com/allenai/tutormoments) and the [TutorMoments preview release](https://huggingface.co/datasets/allenai/tutormoments-preview). Public publisher prompt/code excerpts retain their Apache2.0 attribution under `third_party/tutormoments/`.
