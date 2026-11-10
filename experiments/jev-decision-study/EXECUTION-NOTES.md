# Execution notes

The primary design and all five prompts were committed before live calls. The source audit found 491 unique contexts, including three two-record groups with opposing labels. The full input-only deterministic agreement ceiling is 517/520. This does not explain away other classification errors.

The structured full-history prompt C won on development balanced accuracy. Selection was committed before any new evaluation calls.

## Secondary threshold check

After freezing C and starting the evaluation requests, but before reading evaluation scores, add a development-only probability threshold check. Search the fixed grid .10 through .90 in .05 increments. Choose by balanced accuracy on the original development set, breaking ties toward .50, then lower threshold. Also estimate development threshold behavior by leaving one entire student out at a time. Freeze this choice before calculating any evaluation results.

This is a secondary amendment, not a preregistered primary analysis. It makes no additional model calls. Jev's raw returned choice remains the primary outcome. Thresholded classifications are separately named and are never substituted for raw choices in the headline table. The leave-one-student-out calculation addresses threshold fitting only, not the fact that prompt C was selected on the same development set.
