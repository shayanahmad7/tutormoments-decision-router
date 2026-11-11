# Execution notes

Generation began on 11 November 2026 with six workers. After1,012 successful saved replies, transient disk exhaustion and several transport failures interrupted the process. Disk writes were verified working again before resumption. Six failed traces and one interrupted pending trace were retained in failed-attempts/ with conservative cost reservations. Only missing or failed requests were resumed with their unchanged payloads; all completed replies were retained. Concurrency was reduced to four as an infrastructure precaution. No prompt, label, model, output cap or scoring criterion changed. Timings therefore describe mixed-concurrency execution and are not a production benchmark.

The accounting cap includes the saved failed/interrupted reservations. Those reservations conservatively cover calls whose actual billing is unknown; the reported experimental total is not a billing invoice. The interruption ledger retains hashes and status for each such request.
