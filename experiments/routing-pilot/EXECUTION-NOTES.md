# Execution notes

The first six tutor requests were an infrastructure preflight: five returned and one was rate limited. Despite `reasoning.enabled=false`, DeepInfra returned reasoning content for every completed request, and two replies hit the cap. No quality scores were computed. These outputs are retained under `preflight/` and excluded from the specified non-thinking comparison.

Before the main run, add Qwen’s documented `/no_think` switch uniformly to every tutor request. This is a protocol correction to achieve the intended configuration, not a condition-specific improvement. The original-aware arm retains the publisher tutoring instructions but has this common model-control suffix. Reuse the 32 unchanged Jev calls. Preflight costs count toward the $5 pilot cap.

Source: https://qwenlm.github.io/blog/qwen3/

## Domain screening before scoring

Reading the sampled conversation tails revealed four non-math current tasks (growth mindset, vocabulary or reading comprehension). They remain in the original 32-case analysis. A math-only 28-case sensitivity analysis was specified before any judge calls, with reasons in `domain-screen.json`. This is a source-based domain screen, not an outcome-based exclusion. It reinforces the need to audit domains before the larger math study.

The two original-condition calls on case 434 were used to verify the uniform `/no_think` correction before resuming the randomized queue. Transient connection-level 429/502/503 errors now receive at most three logged retries with 5/10/15-second backoff. There is no automatic resampling of completed outputs.

DeepInfra Qwen3 32B repeatedly returned shared-pool rate limits, including one failure after all four connection attempts. Preserve that failed request in `failed-attempts/` and resume only incomplete requests. Later exhausted 429 requests are deferred while the remaining queue runs; they are not scored as bad tutoring. Successful outputs are never regenerated.

## Additional router control, specified before judging

Use Qwen3 14B as a decision-only router with the same frozen Jev instructions and two options. Its choices select the existing forced-policy replies. This costs 32 short-output calls, no new tutor replies, and tests whether any routing benefit requires Jev. It is a secondary diagnostic and does not change the two primary comparisons. See `secondary-router-plan.json`.

## Evaluator audit and extension after the first ratings

Case 18 exposed a concrete grounding error: the primary judge said the student had not selected B even though that is in the final source turn. Do not erase or selectively fix this rating. Extend the unchanged independent Claude judge from the prespecified eight cases to all 32 cases for both models, retaining the subset and reporting both evaluators. This is a post-results robustness extension, not a second preregistered primary test. See `judge-audit-extension.json`.

One Claude response included prose before its complete ratings JSON. The parser now reads the intact JSON object from that response; no replacement rating was purchased or invented.
