# Execution notes

The source, prompt, runner, review files and request hashes were frozen before the first paid request. The six preflight responses are included in the final 520 per method.

The first full-pass process stopped after an HTTP 503 connection termination on the ordinary LLM request for source index 213. No model response or usage was returned. The failed request is preserved as `traces/failed-llm-213-attempt1.json`, including its original request hash. After inspection, the identical request is eligible for a transport retry; all 38 completed decisions are reused. The prompt, frozen runner and payload hashes remain unchanged. This is a transport recovery, not another completed prediction or prompt trial.

The failed attempt retains a conservative $0.00453325 cost reservation in the runner budget. Its actual billed cost is unknown; it will be reported separately from costs calculated from completed-response usage. The retry record and original failure together document both attempts. Timing for the recovered prediction will describe the successful request, with the failed-attempt overhead separately reported.
