# Analysis checks

This is an exploratory first-reply experiment, not a randomized classroom trial. The unit of comparison is a paired response to the same frozen conversation. One sampled moment per student avoids treating several moments from one learner as independent. The larger study will need student-clustered inference.

| Check | How it is handled |
|---|---|
| Aggregates hiding subgroup differences | Report scaffold and rigor cases separately, both model sizes, and the math-only subset. Do not infer a common improvement from an overall average alone. |
| Ecological inference | Claims concern generated replies in these moments, not improvements in particular students or schools. |
| Selection bias | The source is teacher-selected opportunities; the pilot additionally samples one moment per student and balances categories. It does not estimate the prevalence of needs in classrooms. |
| Collider adjustment | No regression adjustment or filtering on response success. Correct-route and incorrect-route groups are descriptive mechanism checks, not randomized subgroups. |
| Base rates | The full pilot is deliberately 16/16. The math-only subset has 15 scaffold and 13 rigor cases. Report counts with percentages. |
| Regression to the mean | Cases are not selected for low previous scores. No best-of-run output selection. The two old prompt runs remain separate from this new experiment. |
| Survivorship | Keep all planned cases. Infrastructure failures must be resolved or reported as missing coverage; truncations remain failed replies. Do not equate a failed API request with a bad teaching decision. |
| Multiple testing | Two primary comparisons, with Holm correction. Other conditions, confidence fallback, size interaction and math-only analysis are exploratory. Report all conditions. |
| Researcher flexibility | Freeze prompts, case IDs, seed, rubric and primary comparison before quality scoring. Keep the preflight correction and later pre-scoring additions in execution notes. This is not a public preregistration. |
| Causal scope | Matched prompt manipulation supports a local comparison under these model/provider settings. It does not establish learning gains or general effects of model size. |
| Reverse causality | The routing decision precedes generation and is never based on a generated reply. Source labels are only used for evaluation and the explicitly named teacher-policy diagnostic. |

## Remaining threats

- Teacher labels can be ambiguous, and the pre-cut transcript may omit visual or interpersonal information. Excluding conflicting duplicate cuts does not make every remaining label certain.
- Judge ratings may reward familiar phrasing or confuse asking a question with genuine mathematical challenge. The blinded second judge is a sensitivity check; it cannot replace independent human coding.
- Replies in a batch may influence one another's ratings. Randomized candidate order and an independent judge help diagnose this, but do not eliminate it. The larger study should check individually rated replies as well.
- The two policies are potential responses generated once each. Reusing them is efficient and makes counterfactual comparisons transparent, but single samples do not measure generation variability.
- Provider contention, retry backoff, connection setup and serving implementation affect latency. No clean speed claim is justified from this run.
- The preview data and earlier Jev outputs have already been examined. The reserved students are held out from the earlier prompt-selection round, not a pristine external test set.

All 11 statistical fallacy categories were checked in designing the analysis. The numerical audit is performed by `verify.py` after the full run; this document alone is not evidence that the experiment completed.
