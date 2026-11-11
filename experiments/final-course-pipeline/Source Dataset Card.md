---
pretty_name: "TutorMoments-Preview"
license: cc-by-4.0
language:
  - en
  - es
size_categories:
  - 1K<n<10K
task_categories:
  - text-classification
  - text-generation
tags:
  - education
  - tutoring
  - k-12
  - mathematics
  - pedagogy
  - scaffolding
  - rapport
  - dialogue
  - benchmark
configs:
  - config_name: transcripts
    data_files:
      - split: train
        path: transcripts.jsonl
  - config_name: annotations
    data_files:
      - split: train
        path: annotations.jsonl
  - config_name: ground_truth
    data_files:
      - split: train
        path: ground_truth.jsonl
  - config_name: moments
    data_files:
      - split: train
        path: moments.jsonl
  - config_name: benchmark_520
    data_files:
      - split: train
        path: benchmark_520.jsonl
  - config_name: action_taxonomy
    data_files:
      - split: train
        path: action_taxonomy.jsonl
---

# TutorMoments-Preview

462 real K–12 math tutoring sessions (student and tutor) with human annotations, plus a benchmark of
7,280 AI-tutor attempts scored the same way. A preview release from TutorMoments, a project on how well
tutors — human and AI — scaffold, push for rigor, and build rapport. From one K–12 tutoring program
(anonymized as `tutoring_provider_a`).

- **Paper:** [*When Help is Unhelpful: Evaluating AI Tutors for Productive Struggle*](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf)
- **Code:** https://github.com/allenai/tutormoments
- **Contact:** Ryan Knight (ryangknight@gmail.com), Lucy Li (lucyli@cs.wisc.edu), Kyle Lo (kyleclo@cs.washington.edu), Kajal Patel (kajal.patel@wisc.edu), Albert Zhang (albert.z.zhang@gmail.com)

## Subsets

| Config | Rows | Unit |
|---|---|---|
| `transcripts` | 462 | one tutoring session |
| `annotations` | 1,584 | one annotator pass over a session (263 transcripts; 79 caption / 704 scaffolding / 801 rapport) |
| `ground_truth` | 207 | one session's labeled key moments (10,685 moments: 5,378 scaffolding / 5,307 rapport) |
| `moments` | 520 | one frozen, runnable key moment (260 scaffolding / 260 rigor) — the set the benchmark replays |
| `benchmark_520` | 7,280 | one AI-tutor replay (520 moments × 7 models × 2 prompts) |
| `action_taxonomy` | 51,246 | one decomposed tutor action classified A–M (10,674 human / 40,572 AI tutor; model-generated labels) |

```python
from datasets import load_dataset
transcripts = load_dataset("allenai/tutormoments-preview", "transcripts")["train"]
```

Fields are defined by the bundled JSON Schemas (`transcripts.schema.json`,
`annotations.schema.json`, `ground_truth.schema.json`, `moments.schema.json`,
`benchmark_520.schema.json`, `action_taxonomy.schema.json`). Common join key: `transcript_id`
(= `conversation_id` in ground_truth; in moments and benchmark_520 it is the
trailing UUID of `conv_id`, a `{tutor_id}_{student_id}_{transcript_id}` composite).

## moments

The runnable benchmark set: 520 human-annotated key moments (260 scaffolding / 260 rigor), each
frozen at its resolved cut point and packaged self-contained for replay — the pre-cut transcript
context, the gold dimension, the real human continuation that guides the oracle synthetic student,
the frozen `student.trait` persona, and provenance back to the source transcripts (annotator cut
votes, moment ids). This is the set the benchmark harness consumes; `benchmark_520` holds its
replays (`moments.id` = `{set_name}:{scenario_id}`, so it joins to `benchmark_520.scenario_id`
by stripping the `balanced_520:` prefix). The companion `moments.manifest.json` carries integrity
hashes: `content_hash` over the canonical records and `file_sha256` over `moments.jsonl`'s exact
bytes.

## benchmark_520

The AI-tutor benchmark behind the paper's leaderboard: from the 520 balanced key moments in
`moments`, each transcript is cut at the moment, a tutor model continues (≤5 turns) with an oracle
synthetic student, and the annotator pipeline scores it. 7,280 rows = 520 × 7 tutor models × 2 prompt
modes (plain, evaluation-aware). Each row carries the scenario, the AI `exchange`, and its `annotation`.

Each row also embeds `student_trait` — the exact persona its simulated student ran with, recovered
from the original run's trait cache with provenance (`generator_model`, `generated_at`). All rows for
the same scenario share one persona, so every tutor model faced the same students. Re-running the
benchmark with these personas reproduces the paper's setup; freshly generated traits would be a
different student population.

## action_taxonomy

The tutor actions of every scaffolding moment, classified into the 13-category
A–M action taxonomy (scheme `lm_extended_v1`): one row per
`action_decomposed` item, for the human tutors (`ground_truth`,
10,674 rows over 4,709 moments) and the AI tutors
(`benchmark_520`, 40,572 rows over 7,279 replays). The
categories are **model-generated**: `claude-opus-4-8` with provider-native parameters
`{"thinking": {"type": "disabled"}}`, batches of 50, human and AI statements
classified in separate pools. Facets removed by the pre-classification filter
(statements whose subject is not the tutor, bare stances, and descriptions of
what the tutor did *not* do) are kept as rows with `category: null` and an
`excluded_reason`; distributions use the classified rows only, as a macro mean
over moments. `moment_id` joins AI rows to `moments.id`; human rows join to
`ground_truth` by `transcript_id` (= `conversation_id`) and `key_moment_index`.

These labels were **regenerated in October 2026** from this dataset at
revision `66058b4c7ef5e7631b3c4d39a1dfa8172e36d8bc`; they are not the classification run behind the paper. The
paper classified a smaller sample — 100 moments per AI cell — so this config
does not exactly reproduce the paper's action-distribution figure or its
KL-divergence table. The paper's AI cells are recoverable from
`benchmark_520` by filtering `source_round` to `s42`, `s43` and `topup`
(100 moments per cell, 50 scaffolding / 50 rigor). The paper's canonical
numbers are
`analysis/working-paper-20260630/v1_action_taxonomy_distribution.csv` and
`kl_divergence_table.tex` in the code repository. `action_taxonomy.manifest.json`
records the input revision and file hashes, the classifier configuration and
prompt hash, counts, token usage and cost. One `benchmark_520` replay has no
rows because its scoring failed in the source data (`action_decomposed` is
empty).

## Deidentification

Involves minors in an educational setting; treat accordingly.

- IDs (`transcript_id`, `session_id`, `tutor_id`, `student_id`, `annotator_id`) are UUIDv5 surrogates.
- The partner program appears only as `tutoring_provider_a`.
- Free-text PII is replaced with fabricated surrogates or tags (e.g. `<Name>`); names/emails in the
  text are not real. Absolute session datetimes are removed.
- Automated and reviewed but imperfect — report residual PII (contact above); do not redistribute
  affected records.

## Limitations

English-dominant with some Spanish; a single program; annotation is subjective; `ground_truth` labels
are LLM-assisted and not infallible. Not for re-identification.

## License

This dataset is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode.txt). It is intended for research and educational use in accordance with Ai2's [Responsible Use Guidelines](https://allenai.org/responsible-use).

## Source Attribution
The replay data includes synthetic tutor/student conversations between LMs generated from third-party models, which are subject to the respective model providers' terms and conditions. We used the following models to generate the replay data: Claude Opus 4.8 and Sonnet 4.6 (provided by Anthropic); DeepSeek v4 Pro (provided by Hangzhou DeepSeek Artificial Intelligence Co.), Gemini 2.5 Pro and 3.5 Flash (provided by Google), and GPT 5.5 and 5.4 mini (provided by OpenAI). The `action_taxonomy` categories were generated with `claude-opus-4-8` (provided by Anthropic). 

## Acknowledgements
This project has been made possible in part through support from the Gates Foundation and Learning Commons.

## Citation

A paper is in preparation; this citation will be updated when it is published. Until then, cite the
dataset directly:

```bibtex
@misc{zhang2026whenhelp,
  author       = {Zhang, Albert and Ross, Alexis and Patel, Kajal and Bernado, Julian and
                  Bowie, Rebecca and Trindade Ribeiro, Ana and Halper, Daniel and
                  Valayaputtur, Haripriya and Andreas, Jacob and Loeb, Susanna and
                  Lucy, Li and Lo, Kyle and Knight, Ryan},
  title        = {When Help is Unhelpful: Evaluating AI Tutors for Productive Struggle},
  year         = {2026},
  publisher    = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/allenai/tutormoments-preview}}
}
```
