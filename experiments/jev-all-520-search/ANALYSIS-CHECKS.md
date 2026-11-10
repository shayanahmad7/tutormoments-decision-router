# Scope and analysis checks

This is the user's requested all-520 optimization round. No new split or held-out claim is introduced. Raw choices, fitted thresholds and six-prompt averaging are named separately. All candidates and all threshold results are reported, including worse candidates.

| Check | Treatment |
|---|---|
| Aggregate/subgroup differences | Report scaffold and rigor matches separately, 260 each. |
| Ecological inference | No inference about student learning or individual learner outcomes. |
| Selection bias | Teacher-selected benchmark, prior exposure disclosed; optimized on the full benchmark. |
| Collider adjustment | Main score retains all rows, errors and conflicting labels. |
| Base rates | Balanced 260/260; a one-category rule achieves 50%. |
| Regression to the mean | Reuse exact first-run records, not the best prior repeats; no successful call resampled. |
| Multiple comparisons | Six prompts and 91 thresholds per method; best full-set score is explicitly selected and optimistic. |
| Significance interpretation | Descriptive counts only; no p-values or claims that a small gain generalizes. |
| Causal interpretation | No tutoring quality or classroom effect inferred from label agreement. |
| Pseudoreplication | 3,120 candidate-record decisions are not 3,120 independent learners; source has 520 rows and 491 unique contexts. |
| Researcher degrees of freedom | Frozen prompt F and requests; full threshold grid retained; no label edits, per-row fitting, arbitrary trained stacker or hidden-source metadata. |

API model probabilities are used as returned. Individual raw choices at .50 preserve the API's tie choice. The ensemble mean is calculated from the decimal probabilities with stable arithmetic; an independent rational-arithmetic verifier checks threshold counts. No tutor-generation code was run.
