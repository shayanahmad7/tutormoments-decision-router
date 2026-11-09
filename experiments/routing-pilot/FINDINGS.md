# What we learned, and the experiment worth taking forward

## The question

**Does selecting a teaching approach before generating a reply help a smaller math tutor, beyond giving it better instructions?**

That is stronger than asking whether Jev can guess the teacher's scaffold/rigor label. Label agreement is one part of the system. The student receives a reply, not a label, so the main outcome must concern that reply.

The proposed system is simple: Jev reads the conversation available at the stopping point, chooses scaffold or rigor, and supplies the corresponding detailed policy to the tutor. A scaffold policy asks for the smallest useful support while leaving work for the learner. A rigor policy asks for appropriate independent reasoning, justification or connection without giving that reasoning away. Neither policy tells the tutor to be unhelpful or to force difficulty.

## What we actually ran

We sampled 32 different students, balanced by the source's two labels, from the earlier evaluation split. This corpus has already been explored in our previous work, so it is not a fresh blind test. We used the full conversation up to the stopping point, without giving Jev or the tutor the teacher label or future human continuation. A source screen before judging identified four non-math current tasks. We keep the full sample and separately report the 28 math cases.

For each case, Qwen3 14B and 32B each generated five actual replies: the publisher's evaluation-aware prompt, detailed self-choice, Jev's short label, detailed scaffold policy, and detailed rigor policy. That makes 320 unique replies. Jev's chosen branch selects one of the two saved policy replies. Teacher-label, opposite-label and fixed-policy comparisons select from those same replies. Reusing those outputs saves money and makes the comparisons paired; it does not create extra independent observations.

The repository also implements the real route-then-generate function in `pipeline.py`. It generates only Jev's selected branch. Tests verify that Jev's output, rather than the hidden teacher label, controls the instructions.

Two model judges rated all 320 replies with anonymized condition names and shuffled orders. They judged observed scaffold/rigor behavior, over-helping, mathematical error and context fit. A pass combines the required behavior with no over-helping, no detected mathematical error and adequate context fit. This is a first-reply measure, not the publisher's multi-turn score or a measure of student learning.

## The useful findings

**Better instructions help substantially.** Both judges preferred detailed self-choice over the original-aware condition. That is why comparing only Jev's enhanced prompt against the original prompt would exaggerate what we know about the decision model.

**Jev plus detailed instructions improves on detailed self-choice in this sample.** On the 28 math cases, the gain is 3 or 4 passing replies for 14B, depending on the evaluator, and 5 or 6 for 32B. The exact paired tests do not establish a math-only benefit at .05. The full 32-case primary analysis gives a stronger result for 32B, but it includes four non-math tasks and is weaker under the second evaluator. We should lead with the math evidence for this project.

**We have not established that adaptive routing is necessary.** A fixed rigor policy scores 19/28 under both judges for 14B, versus Jev's 17/28 and 19/28. For 32B, Jev beats the fixed policy under Gemini, but loses under Claude. A cheap Qwen14B decision-only router also performs similarly. Jev agreed with 23/32 teacher labels; the Qwen router agreed with 24/32. Those differences are too small to call one more accurate.

**The smaller-model hypothesis is still open.** The observed gains are larger for 32B, not 14B. Two sizes in one model family cannot support a general claim about small tutors.

**Jev is a faster router here, but adding a router is not a free speedup.** Median Jev routing took about 184 ms, versus 750 ms for the Qwen decision-only call. The estimated combined Jev systems were slower than the single-call self-choice systems. The combined estimates add original route and generation timings, and shared-provider rate limits make them exploratory. A paper about speed needs a separate sequential timing experiment.

**Evaluation needs human calibration.** The judges agreed on 243/320 pass/fail decisions, about 76%. In one case, Gemini claimed the student had not chosen answer B even though the student had just said B. We retained that score and expanded the independent check to every reply. We did not replace unfavorable judgments or describe automated ratings as human coding.

One concrete improvement is case 18 with Qwen14B: the self-choice reply returns to an earlier apples problem, while the Jev-selected reply addresses the current paperclip problem. Another informative case is 396 with Qwen32B: Jev selects scaffold at a teacher-labelled rigor moment, yet the resulting reply asks the learner to use ten-times-five to reason about nine-times-five. A wrong route label can still produce useful mathematical work. These cases show why we must separately inspect the decision, the behavior actually produced, and the quality of that behavior.

## Recommended larger experiment

Keep the main research question above. Use these comparisons, with the same conversation, generator, output budget and teaching policies:

1. **Detailed self-choice:** the tutor receives both policies and decides for itself.
2. **Jev-directed:** Jev chooses one policy before the tutor replies.
3. **Cheap LLM-directed:** a small LLM chooses between the same two policies.
4. **Fixed policy:** choose scaffold or rigor on development data and freeze that choice before evaluation. Retain both fixed policies as diagnostics.
5. **Teacher-directed:** use the source label to show what the same generator can do with the intended direction. This is a diagnostic, not a deployable system or a guaranteed ceiling.

Keep the original prompt and Jev-label-only conditions as secondary checks if the budget allows. The essential comparison is not Jev versus a weak original prompt. It is Jev versus equally detailed self-choice and a strong fixed policy.

First, have two people independently rate a balanced blinded set of the existing replies. Include both teacher categories, route disagreements and evaluator disagreements. Use their actual ratings to clarify what counts as helpful support, productive challenge and over-helping. Keep all revisions on development data; do not relabel existing automated results to improve the headline.

Next, freeze the policies and scoring rules. Use student-separated math evaluation cases, another tutor family and repeated generation seeds. The source has only 89 students, so 520 moments are not 520 independent learners. Use student-cluster uncertainty estimates and plan sample size from paired discordance rather than treating repeated outputs as extra students. Any further use of this already explored preview should be described as internal evaluation, with an external corpus or fresh expert examples strengthening generalization.

Evaluate two levels: the immediate reply and the publisher's multi-turn continuation. Initially apply the route only to the first reply, matching our intervention. A system that re-decides later is a separate experiment; the initial teacher label is not ground truth for every later turn.

Run a separate sequential latency test with pinned providers, repeated trials and both time to first answer and completion time. Compare quality at similar cost as well as raw delay. Do not use concurrent, rate-limited pilot timing to claim production speed.

## What would count as a contribution

A useful technical contribution would show **when separating a teaching decision from generation improves the reply, how routing mistakes affect that gain, and what the trade-off costs**. It could also show that a cheap fixed policy explains much of the apparent improvement. Either is a meaningful result if the controls and evaluation are sound.

The current pilot is sufficient for a preliminary course report with concrete data, methods, results and open questions. It is not sufficient to claim a new superior tutoring method. Existing pedagogical steering, prompt-routing and TutorMoments work already covers parts of this idea; see [related work](RELATED-WORK.md). A conference submission would need the larger controlled evaluation and independent human evidence described above.

All numerical results, including weaker controls and evaluator disagreement, are in [RESULTS.md](RESULTS.md). Total accounted spending was $2.59. No additional paid run is required to inspect or reproduce those calculations.
