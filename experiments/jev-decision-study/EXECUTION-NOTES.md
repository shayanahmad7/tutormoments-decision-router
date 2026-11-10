# Execution notes

The primary design and all five prompts were committed before live calls. The source audit found 491 unique contexts, including three two-record groups with opposing labels. The full input-only deterministic agreement ceiling is 517/520. This does not explain away other classification errors.

The structured full-history prompt C won on development balanced accuracy. Selection was committed before any new evaluation calls.

## Secondary threshold check

After freezing C and starting the evaluation requests, but before reading evaluation scores, add a development-only probability threshold check. Search the fixed grid .10 through .90 in .05 increments. Choose by balanced accuracy on the original development set, breaking ties toward .50, then lower threshold. Also estimate development threshold behavior by leaving one entire student out at a time. Freeze this choice before calculating any evaluation results.

This is a secondary amendment, not a preregistered primary analysis. It makes no additional model calls. Jev's raw returned choice remains the primary outcome. Thresholded classifications are separately named and are never substituted for raw choices in the headline table. The leave-one-student-out calculation addresses threshold fitting only, not the fact that prompt C was selected on the same development set.

## Unchanged repeats after primary results

The fresh old prompt differed from its archived choices on 25 records. After reporting the primary new-prompt result, freeze two exact repeats on all 520 records. Save the primary result snapshot and timestamped repeat plan before calls, and report every repeat plus fixed majority/mean-probability summaries. Do not pick the best repeat. These are stability checks on the same cases, not new independent students or a new held-out test.

The three new-prompt runs returned 376, 378 and 375 matches. They agreed on 507/520 decisions. Majority voting returned 374 matches and mean-probability classification 375. Neither improved the result.

## Source-note review after scoring

Inspection of the prespecified error examples found representative notes recommending the opposite direction from the category. Screen all 520 notes with an explicit keyword rule, then read the flagged notes. Record 23 explicit opposite-recommendation flags among 37 keyword hits. Negation and descriptions of prior tutor behavior account for the other flagged cases. The source schema distinguishes aggregate labels from one representative note, so these are review flags, not adjudicated mistakes. Do not change any source label or exclude these records from scoring. No new prompt was built from this evaluation error review.
