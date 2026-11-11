# What this means for the study

## Material Passport

This assessment uses the completed 20-moment Astra pilot, previously saved 520-case classifier results, the earlier tutoring-response pilot, the transcript review and the primary sources linked below. No new human validation, fine-tuning or additional model runs were performed. Findings, interpretations and proposed work are separated.

## The central result

GPT-6 Astra with high reasoning did not dominate the cheaper classifiers in the matched decision-only pilot. It matched 13 of 20 reference labels, the same count as OpenAI Decisions. Jev and ordinary Luna each matched 12. The sample contained ten scaffolding and ten rigor moments from 20 distinct students, chosen before looking at their model errors. All four configurations received the same latest prompt and complete pre-cut conversation.

Astra cost $1.388 for the 20 requests, compared with $0.0118 for the saved Decisions requests and $0.0057 for Jev. Its median complete request took 4.61 seconds, compared with 0.35 seconds for Decisions and 0.26 seconds for Jev. These are observed component timings from different runs and concurrency settings, not a controlled serving benchmark. Still, the claim that the large model is necessarily just as fast is not supported by this pilot. The website's tutoring time-to-first-answer-token plot is a different measurement.

The 65% binary-label result is neither a replication nor an estimate of the website's approximately 93% tutoring-replay score. The two tests use different prompts, tasks and scoring rules, so this result must not be interpreted as contradicting the leaderboard. There is also no evidence that its true accuracy equals the cheaper models: twenty cases are too few for that conclusion. Astra's descriptive 95% accuracy interval is approximately 43–82%. The matched comparisons have only three or four discordant cases. None establishes an accuracy advantage.

Prompt choice remains a substantial issue. On these same 20 cases, the saved earlier Decisions prompt scored 17/20, earlier Luna 15/20, and earlier Jev 14/20. Those are not prompt-matched Astra comparisons and must not be presented as proof that Decisions beats Astra. They show why a final study should cross a small set of fixed prompts with model configurations rather than rely on one heavily revised prompt.

## Has the experiment failed?

The existing work has not established the original engineering claim that adding a decision model improves a tutor's replies. The earlier matched response-quality pilot also did not establish a robust advantage over fixed policies and ordinary LLM routing. A successful label prediction and a good tutoring response are separate outcomes.

The broader research question remains useful. The observed cost difference is large, while the decision-accuracy difference in this pilot is small and uncertain. That supports studying the cost and reliability of pedagogical decisions. It does not support saying that decision models are useless, or that cheap models are equivalent to Astra.

A fair course-report statement is:

> In an exploratory matched sample of 20 mathematical tutoring moments, a high-reasoning general LLM did not show a decision-label advantage over a much cheaper Decisions API configuration. Simple escalation and voting strategies produced limited gains. These results motivate a larger evaluation of when lightweight pedagogical decision models are sufficient and when escalation is useful.

This wording reports what happened without claiming a completed technical breakthrough or a negative result about all decision models.

## Does a cascade help?

We fixed a simple rule before Astra predictions: accept Jev when its maximum class probability is at least 0.90; otherwise ask Astra. This is selective classification, not a pipeline in which Jev tells a tutor how to respond.

The primary rule kept only one of the 20 decisions with Jev and sent 19 to Astra. It matched Astra's 13/20 score, saving approximately 3.5% of estimated token cost. Estimated median sequential latency increased slightly because the router added a step. The predeclared 0.80 sensitivity rule kept five cases with Jev, matched the same score and saved 15.5%. These savings come from component-trace calculations, not a deployed cascade.

The larger existing Jev run gives a reason to investigate selective use: at the 0.90 threshold it matched 66/70 labels, but covered only 13.5% of the corpus. At 0.80 it matched 170/196, covering 37.7%. At 0.95 it matched 24/24, covering only 4.6%. These are development-corpus descriptions, not guaranteed calibration. The 0.95 subset also contains only four scaffolding cases and twenty rigor cases. A perfect score on that small selected subset is not a perfect classifier.

We additionally checked an unweighted majority vote of Jev, Decisions and Luna after the pilot. The latest-prompt vote scored 387/520, fixing 43 errors from the previous best Decisions run but introducing 42. The earlier-prompt vote scored 381/520. Three calls therefore have not established a meaningful improvement over the previous single Decisions score of 386/520. This exploratory ensemble analysis was not part of the predeclared pilot.

## Is the context window the main obstacle?

Our actual Jev requests contained 1,352–21,518 input tokens, with a median of 7,164. Its documented default limit is 32,000 tokens per question and 64,000 per request. No request in this run hit that ceiling. The ordinary Luna requests had a maximum of 19,288 tokens; its documented window is 1,050,000. The small model's input capacity is not the immediate mechanical bottleneck in these experiments. [Jev documentation](https://docs.typesafe.ai/models), [Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).

Understanding the supplied context can still be difficult. Jev's accuracy across increasing length quartiles was 69.2%, 72.3%, 70.8% and 70.0%, showing no clear length gradient. Decisions and Luna performed worse in the longest quartile, but task difficulty and student behavior vary with length, so this does not establish causation. Earlier Jev full-history and current-task-window prompts scored 376/520 and 375/520 respectively; simply shortening the transcript did not improve the score.

Long-context research distinguishes fitting information into a model from reliably using it. That motivates a controlled context experiment, not an assumption that a bigger window solves the problem. [Lost in the Middle](https://arxiv.org/abs/2307.03172).

If we test a compact learner-state representation, it should preserve the current task, what the student independently demonstrated, what help the tutor supplied, the unresolved obstacle and evidence of recent transfer. It should cite source turns and never contain the teacher's answer label. If an LLM produces that representation, its cost and delay count toward the pipeline, and the same LLM directly returning a decision is an essential control.

## Fine-tuning is possible, but it is not the first next step

An open-weight model could be adapted with a method such as LoRA. This is technically feasible; it does not mean these labels are sufficient to train a reliable pedagogical classifier. [PEFT documentation](https://huggingface.co/docs/peft/main/package_reference/lora), [example open-weight model](https://huggingface.co/Qwen/Qwen3-4B).

The 520 rows contain only 491 distinct contexts and come from 89 students. A random row split would put closely related conversation prefixes on both sides of training and evaluation. Three identical-context pairs also have opposing labels. All 520 cases have now influenced prompt development and source review. Training on all of them and reporting accuracy on them would measure fitting, not generalization.

Any supervised study should split by student before training, keep all related prefixes together, tune only on training/development students and use a fresh independently annotated test set for the strongest claim. Grouped cross-validation on the existing corpus can provide a clearly labeled retrospective estimate, but cannot erase prior human/AI exposure to the cases. Teacher labels and independent adjudication should anchor evaluation; agreement with Astra-generated training labels is not the same as pedagogical correctness.

The current official Astra and Luna model pages list fine-tuning as unsupported. A concrete training plan would therefore need a supported model/provider, not an assumption that the present API model can be fine-tuned. [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).

## Recommended next experiment

The most useful next question is: **When can a lightweight model make a sufficiently reliable pedagogical decision, and is escalation worth its additional cost?**

1. Freeze two prompts before any new test: the earlier structured prompt and the general prompt from the latest review. Cross them with Jev, Decisions, Luna without reasoning, Luna with a fixed reasoning budget, and Astra. Reasoning-enabled Luna is an important missing control; otherwise model size and reasoning configuration are confounded.
2. Use all 520 for a clearly labeled benchmark comparison, with student-cluster analysis, and add a genuinely new set of mathematical moments for generalization. Obtain blinded independent review of ambiguous cases while retaining the original benchmark scores separately. Do not rewrite labels to favor a model.
3. Choose cascade thresholds on development students and freeze them. Compare always-cheap, always-Astra, fixed-rate/random escalation at the same budget, and confidence-gated escalation. Report accuracy versus coverage and cost, rather than choosing one favorable threshold after the test. Use noninferiority language only with a prespecified margin and enough data to support it.
4. If routing shows a credible trade-off, test its effect on a single small tutor. Compare direct tutoring with equally detailed instructions, predicted routing, teacher-label routing as a diagnostic upper reference, and fixed scaffold/rigor policies. Evaluate the actual replies with blinded judges, including human review, and account for all stages' latency and cost.

No additional inference or training was launched for these proposed steps. A larger run should have a separate fixed design and spending estimate.

## What could be a contribution?

Generic LLM routing and cascades already exist. RouteLLM studies learned selection between strong and weak models, and FrugalGPT studies cost-aware model cascades. Combining two models alone is not a new method. [RouteLLM](https://arxiv.org/abs/2406.18665), [FrugalGPT](https://arxiv.org/abs/2305.05176).

The useful contribution would be specific evidence about pedagogical decisions: whether a cheap decision model can recognize when it is reliable, which learner situations require escalation, whether context representations help, and whether any decision gain survives when an actual tutor generates a response. A careful negative result could also be valuable: a router might save classification cost yet add little instructional value, or its confidence might fail on the moments where help is most important.

For the current course report, we have a reproducible preliminary comparison and useful limits. We do not yet have evidence strong enough to promise a successful conference-paper method. The next study should discriminate among these possibilities rather than keep modifying prompts until a favorable number appears.
