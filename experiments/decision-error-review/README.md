# Decision errors for review

This review preserves the released labels. It is designed for inspecting disagreements, not proving that the teachers were wrong.

## Open the review

- [Google Doc](https://docs.google.com/document/d/1HXVbQNR_8GgFogpoedYhRXvw04WB3XH5WcLK6K5ZOZY/edit): explanation and all 343 case entries, each with a short conversation preview and a full-context link.
- [Browser viewer](TutorMoments%20Decision%20Error%20Review.html): download and open locally. Search the full text, filter by reference category or cases missed by all three revised models, read the complete conversation, then reveal answers.
- [All 520 decisions](All%20520%20decisions%20for%20review.csv): one row per released moment; all archived raw columns, separate derived results, and the twenty-case Astra checks. Empty Astra entries mean not run.
- [Full cases](cases/): verbatim released conversation prefixes, reference category, every archived prediction and the selected original teacher annotation when an exact source match was found.

## Coverage

There are 342 distinct full-run disagreements across 18 archived raw-result columns (15 distinct prediction vectors; aliases are documented in summary.json). Moment 440 is an additional fresh-Astra disagreement outside that union, giving 343 case entries. The latest revised Jev, OpenAI Decisions and Luna models disagree with at least one reference on 254 moments and all disagree on 57. A complete source-ID and label alignment check was performed for all 520 rows.

The first six-prompt C vector is also archived as Jev earlier and Jev selected C. Prompt A is also archived as previous fresh. Copies are not independent replications. Threshold and voting columns are derived summaries, not new API calls. Source CSV hashes are in summary.json. The review includes the raw full-520 result archives rather than selectively showing only the latest prompt's failures.

Three identical-context pairs have opposite reference labels: 70/71, 367/368 and 411/412. Each pair also has the same student metadata, conversation and cut turn. This is a concrete ambiguity for a deterministic context-only classifier. It does not establish which label should be changed. No cases were removed or labels changed. Some source material is non-math; prior subject-screen labels are preserved rather than describing all 520 as a verified math-only sample.

Exact original teacher annotations were matched on transcript ID, annotator ID, turn start and turn end in 315/343 case entries. For the remaining 28, the released rubric hint remains visible, but no alternative source annotation was substituted. These comments may describe the larger episode, including events after the decision point. They were not sent to the decision models.

## Website protocol

The live leaderboard snapshot is saved in website-leaderboard.json, with its source page/script and the released default configuration. GPT-6 Astra's evaluation-aware scores are .938 for scaffolding and .915 for rigor; their average is .9265 (about 92.7%). The default replay has up to three tutor replies alternating with two simulated student replies. Claude Opus 4.6 is the oracle student and judge. Astra is configured at high reasoning.

The score requires the appropriate behavior with no over-scaffolding. An action classified as both can pass either reference category. Our forced binary decision is made before those additional student replies, so it is a different outcome. This protocol difference makes a direct comparison invalid; it does not quantify the contribution of each difference to the numerical gap. See [publisher scoring](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/report.py), [configuration](https://github.com/allenai/tutormoments/blob/main/src/tutormoments/default_config.yaml) and [website](https://tutormoments.allen.ai/).

## New diagnostic

The [twenty fresh Astra agents](../astra-blind-subagents/README.md) scored 14/20, with 6/10 scaffolding and 8/10 rigor. The same-input official API also scored 14/20. One prediction improved and one regressed. Agents had no inherited chat and received only their assigned neutral input file. This was procedural blinding in a shared filesystem, not OS-enforced isolation. No paid API calls were made. The sample was reused and is too small to establish a general ranking.

## Rebuild

From the repository root, run `python3 experiments/decision-error-review/build_review.py`. It requires the already-downloaded original dataset under the adjacent Original Data workspace and the ignored `data/jev/moments.jsonl`, as well as the tracked result archives. It does not call model APIs or modify the source labels. The standalone full-context viewer and Markdown case files are already built.
