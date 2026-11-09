# Where this study fits

Checked against primary sources on 9 November 2026. This is a focused novelty check, not a claim to have found every relevant publication. Searches for TutorMoments with Jev or pedagogical routing did not identify a directly matching published Jev experiment. Absence from these searches is not proof of novelty.

| Work | What overlaps | What our study should test differently |
|---|---|---|
| [Puech et al., 2025: Pedagogical Steering / StratL](https://aclanthology.org/2025.findings-acl.1348/) | Represents a teaching strategy as a transition graph and steers a tutor through it; includes a small high-school field study. | Do not claim to invent separating teaching strategy from language generation. Test a specific fast binary router against matched policy prompts, with error propagation and cost. |
| [Chang et al., 2026: Learning to Prompt](https://arxiv.org/html/2606.20138v2) | Learns adaptive prompt selection, evaluates simulated conversations and a high-school deployment. | Our proposal is a frozen, off-the-shelf decision model, without router training, at teacher-annotated moments. Its classroom outcomes cannot be compared directly with our first-reply ratings. |
| [Macina, Kapur and Sachan, 2026: The Assistance Dilemma / Eduardo](https://arxiv.org/html/2610.06446v1) | Trains tutors at several model sizes and evaluates on TutorMoments. Its learning-based reward includes constraints against solution handover and factual errors. | Our intervention changes inference-time control rather than weights. This is a particularly important comparator for the eventual small-model claim. Merely obtaining a strong small-model TutorMoments score would not itself be new. |
| [Li and Zhao, 2026: SocraGate](https://doi.org/10.3390/app162110561) | Screens candidate tutoring responses for answer leakage. | It acts after generation; our router chooses an instructional policy before generation. A future combined system would need an ablation showing what each component contributes. |
| [humans&, 2026: Introducing &Tutor](https://tutor.humansand.ai/blog/) | Reports TutorMoments improvements from training with a learner simulator, plus analysis of learner modeling. | This is a vendor report, not equivalent to independent validation. It reinforces that comparison should be against current strong tutoring systems as well as general assistants, without treating simulator performance as measured human learning. |

The strongest modest contribution is an empirical answer to: **When does a fast, explicit scaffold-or-rigor decision help a smaller tutor beyond equally detailed prompting, and what is lost when that decision is wrong?**

Useful supporting results are a decomposition of routing versus execution failures, the value of declining to force a low-confidence decision, and a measured quality/cost/delay trade-off. The current pilot can establish feasibility and expose failure modes. It cannot establish broad model-size effects, learner gains, or a dependable latency advantage.

For the larger study, prioritize a cheap LLM classifier with the same policies, a tutor trained for pedagogy if accessible, and an independent blinded human review. Do not add more model names merely to make the table larger.

## A practical next-stage target

For the course, this pilot can support a clear preliminary technical report if the actual replies and limitations are shown. For a conference paper, prioritize the main causal comparison over a long leaderboard: Jev-directed detailed policy versus detailed self-choice, with the cheap LLM router and teacher-route diagnostic explaining the mechanism.

As a rough planning calculation, a paired binary comparison with 30% discordant pairs needs about 285 independent cases to detect a 10-percentage-point difference with 80% power at two-sided alpha .025 (normal approximation). A 5-point difference needs roughly four times as many. This is not a power guarantee: moments from the same student are clustered, and only 89 students are present in this preview. Use the pilot’s discordance and a student-cluster simulation to plan the actual follow-up. Do not treat multiple generations or ten derived policies as independent new students.

Before a larger paid run, have two people independently review a balanced, blinded set of replies, including route disagreements and over-help cases, then reconcile disagreements. Report the reviewer procedure and agreement honestly. For the class draft, that can be a concrete next step rather than a claim that validation already happened.
