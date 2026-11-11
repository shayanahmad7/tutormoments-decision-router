# Full-preview first-reply routing results
Status: complete. New experiment cost: $3.0029.
All outcomes below are automated first-reply ratings. They are not the published TutorMoments multi-turn score and do not measure student learning.

## all_520
| Condition | Passing replies | Rate | Scaffolding | Rigor |
|---|---:|---:|---:|---:|
| Detailed self-choice | 357/520 | 68.7% | 208/260 | 149/260 |
| Jev-directed policy | 379/520 | 72.9% | 199/260 | 180/260 |
| Decisions-directed policy | 382/520 | 73.5% | 210/260 | 172/260 |
| Always scaffold | 294/520 | 56.5% | 224/260 | 70/260 |
| Always rigor | 385/520 | 74.0% | 171/260 | 214/260 |
| Teacher-directed diagnostic | 438/520 | 84.2% | 224/260 | 214/260 |
| Opposite-teacher diagnostic | 241/520 | 46.3% | 171/260 | 70/260 |
jev_directed_minus_self_detailed: +4.2 pp; student-cluster95% interval -1.0 to +9.2; wins 88, losses 66.
decisions_directed_minus_self_detailed: +4.8 pp; student-cluster95% interval +0.2 to +9.5; wins 85, losses 60.
jev_directed_minus_always_rigor: -1.2 pp; student-cluster95% interval -5.7 to +3.2; wins 47, losses 53.
jev_directed_minus_always_scaffolding: +16.3 pp; student-cluster95% interval +10.9 to +21.4; wins 118, losses 33.

## strict_math_346
| Condition | Passing replies | Rate | Scaffolding | Rigor |
|---|---:|---:|---:|---:|
| Detailed self-choice | 249/346 | 72.0% | 160/197 | 89/149 |
| Jev-directed policy | 252/346 | 72.8% | 148/197 | 104/149 |
| Decisions-directed policy | 260/346 | 75.1% | 161/197 | 99/149 |
| Always scaffold | 207/346 | 59.8% | 170/197 | 37/149 |
| Always rigor | 263/346 | 76.0% | 134/197 | 129/149 |
| Teacher-directed diagnostic | 299/346 | 86.4% | 170/197 | 129/149 |
| Opposite-teacher diagnostic | 171/346 | 49.4% | 134/197 | 37/149 |
jev_directed_minus_self_detailed: +0.9 pp; student-cluster95% interval -5.3 to +6.5; wins 51, losses 48.
decisions_directed_minus_self_detailed: +3.2 pp; student-cluster95% interval -2.2 to +8.3; wins 51, losses 40.
jev_directed_minus_always_rigor: -3.2 pp; student-cluster95% interval -8.5 to +1.8; wins 29, losses 40.
jev_directed_minus_always_scaffolding: +13.0 pp; student-cluster95% interval +7.0 to +19.0; wins 71, losses 26.

## known_nonmath_excluded
| Condition | Passing replies | Rate | Scaffolding | Rigor |
|---|---:|---:|---:|---:|
| Detailed self-choice | 343/498 | 68.9% | 201/251 | 142/247 |
| Jev-directed policy | 363/498 | 72.9% | 192/251 | 171/247 |
| Decisions-directed policy | 363/498 | 72.9% | 203/251 | 160/247 |
| Always scaffold | 279/498 | 56.0% | 217/251 | 62/247 |
| Always rigor | 366/498 | 73.5% | 164/251 | 202/247 |
| Teacher-directed diagnostic | 419/498 | 84.1% | 217/251 | 202/247 |
| Opposite-teacher diagnostic | 226/498 | 45.4% | 164/251 | 62/247 |
jev_directed_minus_self_detailed: +4.0 pp; student-cluster95% interval -1.2 to +8.8; wins 82, losses 62.
decisions_directed_minus_self_detailed: +4.0 pp; student-cluster95% interval -0.7 to +8.5; wins 77, losses 57.
jev_directed_minus_always_rigor: -0.6 pp; student-cluster95% interval -5.3 to +4.0; wins 47, losses 50.
jev_directed_minus_always_scaffolding: +16.9 pp; student-cluster95% interval +11.4 to +21.9; wins 116, losses 32.

## prior_math_positive
| Condition | Passing replies | Rate | Scaffolding | Rigor |
|---|---:|---:|---:|---:|
| Detailed self-choice | 246/357 | 68.9% | 149/181 | 97/176 |
| Jev-directed policy | 255/357 | 71.4% | 135/181 | 120/176 |
| Decisions-directed policy | 260/357 | 72.8% | 145/181 | 115/176 |
| Always scaffold | 196/357 | 54.9% | 156/181 | 40/176 |
| Always rigor | 266/357 | 74.5% | 120/181 | 146/176 |
| Teacher-directed diagnostic | 302/357 | 84.6% | 156/181 | 146/176 |
| Opposite-teacher diagnostic | 160/357 | 44.8% | 120/181 | 40/176 |
jev_directed_minus_self_detailed: +2.5 pp; student-cluster95% interval -4.1 to +9.0; wins 61, losses 52.
decisions_directed_minus_self_detailed: +3.9 pp; student-cluster95% interval -2.0 to +9.9; wins 55, losses 41.
jev_directed_minus_always_rigor: -3.1 pp; student-cluster95% interval -9.1 to +2.6; wins 31, losses 42.
jev_directed_minus_always_scaffolding: +16.5 pp; student-cluster95% interval +9.9 to +22.8; wins 83, losses 24.

## Evaluation audit
{"n_replies": 96, "same_pass": 75, "primary_pass": 60, "audit_pass": 53}
{"primary": 30, "audit": 9}

## Limits
Routes were archived, and policy selection was applied to paired generated alternatives. Tutor prompts and routing prompts were developed on this same source preview. These findings are exploratory internal evaluation. The known-nonmath-excluded subset is not a fully adjudicated math-only corpus. Generation calls ran concurrently; serial latency sums add historical route timing and cannot establish deployment speed. All outcomes and fixed-policy controls are retained.
