# What the transcript review changed

## Scope and method

The 520 released moments reuse portions of 112 conversation histories. We reviewed each longest pre-cut history and marked every earlier stopping point within it, verifying that the shorter contexts were exact prefixes. This avoids rereading the same conversation for every moment while retaining every turn available at every cutoff. We did not treat later turns in a shared history as information available to an earlier classification request.

The primary agent reviewed groups 0–34; three review agents covered 35–60, 61–86 and 87–111. The per-conversation JSONL files record coverage, domain, reasoning and annotation concerns. This is AI-assisted source review, not human validation. Every published label is retained. Prior predictions from all three methods were examined, including errors shared by all methods.

These notes inform one revised prompt. They do not constitute a new empirical coding study: error themes were not independently human-coded, and no prevalence estimates are claimed for them.

## Main distinction: what does the learner need next?

The old prompt can encourage a focus on the last answer rather than the learning episode. The important distinction is whether an obstacle remains that calls for targeted support, or whether the learner can productively attempt, explain or check something themselves.

Two opposite errors appear repeatedly:

- A student says a correct number or agrees after the tutor supplied the reasoning. The classifiers treat this as readiness for rigor even though the central difficulty remains.
- A student demonstrates new understanding or successful transfer after struggling. The classifiers keep recommending help because they overweigh earlier difficulty.

The revised prompt therefore tracks the obstacle, the help already given, and the student's own contribution after that help. It asks for the next instructional direction rather than a global judgment about the student's ability.

## Specific distinctions supported by the review

| Distinction | Why it matters | Illustrative source moments, numbered from 1 |
|---|---|---|
| Student reasoning versus tutor-supplied answers | Agreement after a worked solution is not evidence that the student can make the key connection. | 426: the tutor supplies the fraction solution and the student agrees. All three earlier classifiers selected rigor; the reference is scaffolding. |
| Fade help after genuine progress | A previous difficulty should not permanently determine the next move. | 427: the student independently solves a related subtraction after instruction. Decisions and the ordinary LLM previously continued scaffolding; the reference is rigor. |
| Correct substep versus unresolved representation | Correct arithmetic can coexist with difficulty mapping quantities, fractions, bars or equations. | 284 and 418: a small correct contribution does not establish understanding of the larger representation. |
| Explanation is a rigor opportunity | Rigor includes asking why or inviting self-checking, not only raising numerical difficulty. | 302 and 420: the next useful move can be learner reasoning after recent progress. |
| Alternative methods and answer formats | A valid method need not match the tutor's wording or the platform's expected syntax. | 387: a different valid sequence strategy. 445: a mathematically valid equation is rejected by the platform. |
| Reading options versus endorsing them | Spoken distractors are not necessarily student misconceptions. | 393: all three previous classifiers chose scaffolding while the student was reading options; the reference is rigor. |
| Administrative or technical difficulty versus conceptual difficulty | Asking to use a whiteboard or a tutor's mistaken click does not show a math gap. | 311 and 322. |
| Local learning rather than global ability | Earlier addition fluency need not imply fraction-model understanding; earlier difficulty need not imply later inability. | Recurs across the conversation notes; no topic-specific rule was added. |

These examples appear only in this review report. They are not included in the final prompt or model requests.

## Where the reference evidence is less clear

The published paper describes teacher identification of instructional opportunities, followed by aggregation into the released categories. A record's `rubric.hint` is a representative annotation, not necessarily a complete or unanimous explanation of its final label. The original scaffold and rigor judgments are not inherently mutually exclusive; the current experiment asks a forced binary question.

We found several kinds of uncertainty:

- **Opposite labels for identical inputs.** Source index pairs 69/70, 366/367 and 410/411 have identical pre-cut contexts but opposite categories. In the CSV's one-based numbering these are 70/71, 367/368 and 411/412. A consistent deterministic context-only classifier can match at most 517 of 520 unchanged labels.
- **Hints describing future events.** For example, moment 421's hint cites later quiz performance, but the cutoff is before that quiz. Moment 271's hint invokes a self-correction that occurs later. Those events cannot legitimately inform the classifier at the earlier cut.
- **Hints disagreeing with the aggregate category.** Some hints recommend the opposite direction, mention both or neither, or contain only a fragment. We do not change labels to fit the hint or introduce rules to reproduce these cases.
- **Unreliable screen or transcript details.** Some descriptions show wrong arithmetic, stale boards, bundled actions, speaker confusion or incorrect platform feedback. The prompt asks models to weigh attributed learner work and avoid inventing unseen details. It still receives the unmodified source context.
- **Cuts without a substantive learning decision.** Some records end during setup, reconnection or social talk. A forced choice can still be returned, but the input may not support a strong instructional judgment.

These observations explain why agreement with the source category is not the same as proving the pedagogically best action. They are not reasons to remove difficult records from the primary score.

## The corpus is not exclusively mathematics

The full 520 includes reading comprehension, vocabulary, sentence writing and orientation/reflection moments. Examples include source indices 137–139, 206, 223–228, 265–269, 275–276, 305–306 and 327–329; index 307 involves time inference within a reading passage. Some other cuts are noninstructional transitions within math sessions.

We retain all 520 because that is the requested benchmark. Domain notes are descriptive rather than a validated exhaustive exclusion scheme. The overall score should not be called exclusively math accuracy. The prompt uses the same general instructional distinction for every subject; it contains no domain-to-label mapping.

## What the revised prompt deliberately leaves out

No case-specific examples, names, source IDs, reference labels, teacher hints, future continuation, probability thresholds or label-distribution targets appear in the model-visible instructions. The full pre-cut conversation is preserved. The revision focuses on the learner's current need, attribution of work, meaningful progress, productive attempts, and appropriate fading of support.

Reviewing all 520 still means the prompt was developed on this corpus. Avoiding explicit answer leakage does not turn the subsequent score into a held-out test. The next scientific validation would freeze this prompt and test it on genuinely new conversations, or obtain independent human review of ambiguous cases. This round does neither and will report the observed result without further tuning.

## Sources

- [TutorMoments paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), sections 3.3–3.4 and appendices C–D.
- [Dataset and data card](https://huggingface.co/datasets/allenai/tutormoments-preview).
- [Schema](https://huggingface.co/datasets/allenai/tutormoments-preview/blob/main/moments.schema.json).
- Local source and review hashes are recorded in `frozen.json`; index references above use the pinned source revision documented in the plan.
