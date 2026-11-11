# Frozen full-preview first-reply routing experiment

Frozen 11 November 2026, before new tutor responses and judgments. This expands the earlier exploratory pilot; it is not a new held-out benchmark. The user authorized up to $10 additional spending; this runner has a separate hard $8 cap, including failures and audit judgments, leaving $2 outside this runner.

## Question and scope
Does choosing a scaffold/rigor policy with a separate decision component improve the next reply of a small tutor beyond giving the same tutor the same policy menu and letting it choose?

Use all 520 released moments with their full pre-cut conversation; preserve conflicting labels and non-math cases. The primary outcome concerns the next reply, not the publisher's five-speaking-call replay or student learning. Do not compare its percentage directly with the leaderboard. The full source was used in earlier prompt exploration. No new claim of held-out generalization.

## Frozen generation
One tutor: Qwen3-32B through DeepInfra/OpenRouter, non-thinking `/no_think`, temperature 0, seed 20261111, output cap 384, no provider fallback. Three generated replies per moment: detailed self-choice (both policies), forced scaffolding, forced rigor. Policies and scoring definitions are unchanged from the earlier pilot. Generate both forced replies once, then select them for paired analyses; the additional selected conditions are not independent generated observations.

Frozen route choices are archived Jev prompt C (376/520 label matches) and OpenAI Decisions/GPT-6 Luna (386/520). These were the strongest previously observed raw configurations, chosen before this generation round, but selected using this same preview. They are not fresh router calls. Derive Jev-directed, Decisions-directed, always-scaffold, always-rigor, teacher-directed, and opposite-teacher policies. The teacher label is used only for diagnostics and final scoring, never as input to deployable conditions or the judge.

Primary comparison: Jev-directed versus detailed self-choice. Required controls: both fixed policies, Decisions-directed, teacher-directed and opposite-teacher. Report all of them irrespective of direction. A fixed-policy benefit is evidence about instruction effects, not proof that routing helps.

## Evaluation and analysis
Gemini 2.5 Flash rates all three replies per case in seeded shuffled order with anonymous IDs, without labels, model/condition names, route choices or teacher notes. It scores observed scaffolding and rigor separately (both may occur), over-helping, mathematical error, context fit and uncertainty; it quotes literal response evidence. Primary pass requires the reference-direction behavior, no over-helping, no detected math error, context fit 2, and valid generation. Also report direction-plus-no-overhelp and each component. Empty/truncated/unexpected-reasoning replies count as failures; missing judge coverage stays explicitly missing. Never silently drop cases or replace unfavorable ratings.

A fixed 32-case Claude Sonnet 4.6 audit, balanced by reference and one case per student, is selected without using outcomes. It rates the same three replies with independently shuffled order. Report both judgments, not whichever is more favorable.

Report n, counts, paired percentage-point differences and student-cluster bootstrap 95% intervals (89 student IDs in the released source, verify actual count). Repeated moments are not independent students. Main scope is all 520. Sensitivity excludes only pre-existing clearly non-math flags and opposite-label identical-context cases; it is a known-nonmath-excluded sensitivity, not a newly verified all-math sample. Math-positive annotations provide a second descriptive subset. Preserve mixed/unknown cases explicitly.

Generation timings come from concurrent calls and are descriptive. Report generator-only first-answer latency separately from archived router latency; adding these is a reconstructed serial estimate. Cached route lookup time is not router inference time. This study does not establish deployment latency improvements. Deployment costs count the selected reply plus historical route cost, not the other potential reply or judges. Experiment expenditure includes all new calls.

## Stopping and reproducibility
Do not alter prompts, select a different model, optimize thresholds or choose cases after observing the final results. Finish the frozen calls if budget/time permits; otherwise report exact incomplete coverage. Resume only identical payload hashes. The $8 guard reserves conservative byte-based input/output charges before requests and retains conservative costs for failed attempts. Stop at the cap, with no top-up. Endpoint prices and source hashes are stored before calls. No credentials enter outputs.
