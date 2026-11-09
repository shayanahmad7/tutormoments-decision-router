# Does a separate teaching decision improve a small math tutor?

## Material Passport
Public, de-identified TutorMoments preview; pinned source hashes verified locally. Exploratory code experiment, specified 9 November 2026 before new tutor outputs. Earlier Jev decisions and corpus analyses have already been inspected. This is not a previously unseen benchmark. No student learning outcomes or human validation are claimed.

## Why this experiment
Our previous experiment measured Jev's agreement with teachers' scaffold/rigor labels. That is only the first link in a tutoring system. A correct label might produce a bad hint, while a wrong label might still produce a useful reply. We now test the reply itself and separate the effects of routing from the effects of a better prompt.

**Primary question:** With a fixed small tutor model, does a Jev-selected teaching instruction produce more appropriate first replies than giving that tutor the same instruction menu and letting it choose?

**Secondary questions:** Does routing add anything beyond a short label? How much of the achievable improvement is lost to routing errors? Is the benefit different for Qwen3 14B and 32B? What are the extra cost and response delay?

## Frozen pilot
32 moments, 16 scaffold and 16 rigor, one moment per student. Draw deterministically with seed 20261109 from the previous 382 evaluation records; do not select on Jev correctness, confidence, output quality, or transcript length. Exclude cuts that have conflicting teacher categories, and keep an exclusion ledger. Use the full pre-cut text without truncation. Teacher labels and later human continuation never reach the tutor or Jev, except for the explicitly labelled teacher-route diagnostic.

Run Qwen3 14B and 32B through DeepInfra via OpenRouter, FP8, no provider fallback, non-thinking, temperature zero, 384 output-token cap. The same limit applies to all tutor conditions. These are two model sizes within one family, not a general test of all small models. Send only public corpus excerpts to providers. Freeze exact prompts and input hashes before live generation. Maximum new pilot spend: $5 including routing, generation and judging; no credit purchase or top-up.

| Condition | What changes | What it tells us |
|---|---|---|
| Original aware | Publisher evaluation-aware instructions | Starting point |
| Detailed self-choice | Both detailed teaching policies; tutor chooses privately | Prompt-quality control |
| Jev label only | Original prompt plus Jev's short direction | Whether the decision alone helps |
| Jev detailed | Jev chooses one detailed policy | Proposed system |
| Teacher detailed | Teacher label chooses the same detailed policy | Correct-label diagnostic, unavailable in deployment |
| Opposite teacher | Opposite label chooses the same detailed policy | Sensitivity to wrong instructions |
| Fixed scaffold / fixed rigor | Same detailed policy on all cases | Whether context-sensitive routing beats a fixed habit |

Generate each forced-policy reply once and evaluate it once. Derive Jev, teacher, opposite and fixed policies by selecting the corresponding saved reply. These derived conditions are correlated views of two potential outputs, not independent replications. Both policies run for every moment, not just Jev's choice. This is a cost-saving paired experimental design, not invented data. A fixed confidence fallback (top choice probability at least .80: route; otherwise use detailed self-choice) is secondary and will not be tuned on this pilot.

Reuse the frozen Jev prompt A from the earlier round, but make 32 fresh Jev calls to measure current routing latency. Do not tune it in this experiment. Separately compare these decisions with the archived choices.

## Evaluation
The intervention applies to the **first tutor reply only**, matching the user's proposed design. The pilot does not replay five speaking turns and must not be labelled an official TutorMoments score.

A separate Gemini 2.5 Flash judge sees the full pre-cut conversation and anonymized replies in a seeded random order. It does not see teacher labels, Jev choices, prompts, model names or condition names. It rates each reply on observed scaffolding, observed rigor, over-helping, mathematical error, context fit and a concise evidence reason. Scaffolding and rigor can both occur. Require literal text evidence; an arbitrary question mark does not establish rigor. No judge-generated student outcomes.

Primary local outcome: reply exhibits the teacher-required direction, without over-helping, without a detected mathematical error, and with adequate context fit. Report the simpler direction-plus-no-over-help outcome separately. These are local first-reply measures, not the paper's multi-turn measure. Report each component, by teacher category as well as overall. Empty, truncated, failed or malformed generations are visible failures; never silently drop them. Failed judging remains missing with coverage reported, not a negative quality judgment.

Cross-check a prespecified eight cases (four per category) for each tutor using Claude Sonnet 4.6, within budget, in a different reply order. This checks model-judge sensitivity, not human agreement. All coding is model-assisted. The conference study needs blinded independent human ratings of a stratified subset and adjudication of ambiguous cases.

## Analysis and timing
Primary comparison is Jev detailed minus detailed self-choice, paired by moment within each model. Report counts, difference in percentage points, paired stratified bootstrap intervals (10,000 resamples), exact McNemar tests and Holm correction across the two primary model comparisons. Because there is one case per student, resampling moments also resamples students. Model-size interaction is a paired difference of differences, exploratory. Report all conditions regardless of direction.

Decompose errors: router agrees/disagrees with teacher; selected reply passes/fails; teacher-policy reply passes/fails. Compare predicted branch to both alternatives and report teacher-policy minus Jev-policy performance. Do not assume teacher-policy is a guaranteed performance ceiling: response generation can fail or the annotation can be ambiguous.

Stream tutor outputs and record time to first non-whitespace answer content, excluding reasoning, plus full-call latency. Add fresh Jev latency to routed replies. This addition is an explicitly reconstructed serial-system estimate, not a separately instrumented deployed pipeline. Do not count local archive cache lookup as router latency. Randomize model/condition order, retain provider, usage and finish reasons. Use a concurrency of two for affordable throughput; timing is exploratory and must be repeated sequentially for a speed claim. Record experiment spending separately from the estimated per-deployed-reply cost. Judge costs are evaluation costs, not deployment costs.

## What would justify a conference paper
A useful contribution is a controlled study of when separating a pedagogical decision from response generation helps or hurts, with error propagation and quality/cost/latency results. Simply adding Jev is not novel by itself. Related work already steers pedagogical plans, routes prompts and screens generated replies.

After this pilot, freeze the design on development students, then run the remaining evaluation students with adequate coverage, repeated generation seeds and a second tutor family. Add the original five-speaking-call replay and original scoring pipeline as a secondary benchmark outcome. Apply the initial decision only to the first reply; a separately named adaptive-routing arm would re-decide later and must not reuse the initial teacher label as later ground truth. Compare with a cheap LLM classifier using the identical branch policies and with fixed-policy controls. Use calibrated confidence or abstention only if fitted on development data. Add blinded human review, duplicate/conflicting-cut sensitivity, and a power analysis based on paired discordance and student clustering before the larger run. Do not keep changing the system on the test cases until a significant result appears.

## Sources
- [TutorMoments project and current evaluation definition](https://tutormoments.allen.ai/), [working paper](https://tutormoments.allen.ai/static/paper/tutormoments-preview.pdf), [publisher code](https://github.com/allenai/tutormoments), [dataset](https://huggingface.co/datasets/allenai/tutormoments-preview).
- Puech et al. (2025), [Towards the Pedagogical Steering of Large Language Models for Tutoring](https://aclanthology.org/2025.findings-acl.1348/): strategy graphs and prompt steering already exist. Our proposed distinction is a low-cost binary decision component evaluated with matched instruction controls and routing-error analysis.
- Chang et al. (2026), [Learning to Prompt](https://arxiv.org/abs/2606.20138): adaptive prompt selection evaluated in simulation and with high-school students. Our pilot does not reproduce their learning/engagement claims.
- Li and Zhao (2026), [SocraGate](https://doi.org/10.3390/app162110561): output screening for answer leakage, distinct from selecting the policy before generation.
- [Jev model and prices](https://docs.typesafe.ai/models), [Choice API](https://docs.typesafe.ai/primitives/choice).
- [Qwen3 models](https://qwenlm.github.io/blog/qwen3/), [OpenRouter streaming](https://openrouter.ai/docs/api/reference/streaming), [provider selection](https://openrouter.ai/docs/guides/routing/provider-selection).
