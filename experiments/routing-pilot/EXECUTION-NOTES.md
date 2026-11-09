# Execution notes

The first six tutor requests were an infrastructure preflight: five returned and one was rate limited. Despite `reasoning.enabled=false`, DeepInfra returned reasoning content for every completed request, and two replies hit the cap. No quality scores were computed. These outputs are retained under `preflight/` and excluded from the specified non-thinking comparison.

Before the main run, add Qwen’s documented `/no_think` switch uniformly to every tutor request. This is a protocol correction to achieve the intended configuration, not a condition-specific improvement. The original-aware arm retains the publisher tutoring instructions but has this common model-control suffix. Reuse the 32 unchanged Jev calls. Preflight costs count toward the $5 pilot cap.

Source: https://qwenlm.github.io/blog/qwen3/

## Domain screening before scoring

Reading the sampled conversation tails revealed four non-math current tasks (growth mindset, vocabulary or reading comprehension). They remain in the original 32-case analysis. A math-only 28-case sensitivity analysis was specified before any judge calls, with reasons in `domain-screen.json`. This is a source-based domain screen, not an outcome-based exclusion. It reinforces the need to audit domains before the larger math study.

The two original-condition calls on case 434 were used to verify the uniform `/no_think` correction before resuming the randomized queue. Transient connection-level 429/502/503 errors now receive at most three logged retries with 5/10/15-second backoff. There is no automatic resampling of completed outputs.
