# Qualitative study supporting materials

This folder reproduces the 38-moment analysis in the course paper. It does not combine that sample with the later eight-episode human-method pilot or the 520-moment routing experiments.

## Start here

- **Qualitative Coding and Results.xlsx:** the main reading copy, with three tabs: Read Me and Codebook, Coded Responses, and Results. Both passes remain visible; counts and agreement are calculated from the response table.
- **Complete Coding Data - 114 Responses.csv:** 38 matched moments × observed human, GPT-5.5 plain, and GPT-5.5 evaluation-aware responses. The Work Left and Information Supplied columns contain the first archived AI-assisted coding pass used in the paper. Exact response text, evidence quote and rationale are included. The second archived pass appears in separate clearly named columns.
- **Coding Manual.md:** the frozen W0–W3/NA and R0–R3/NA definitions, unit boundaries and coding instructions. The source manual is copied unchanged.
- **All 38 Cases - Readable.md:** nearby conversation and all three source responses for each case.
- **All 38 Cases - Full Context and Coding.json:** complete preceding context, nearby reading window and all response codes. Use this for any case that requires earlier context.
- **Results - Both Preserved Coding Passes.csv:** category distributions from both archived passes. The paper reports the first; the second exposes coding sensitivity rather than a consensus label.
- **Original 40 Cases - Eligibility and Exclusions.csv:** E20 and E24 remain in the original selection ledger but are excluded from the 38-case analysis because additional learner events preceded the human reply. They were not replaced.
- **Verification.json:** source hashes and checks completed on November 11, 2026.

## Design and interpretation

The analysis contains 38 distinct students and 19 source scaffolding/19 rigor opportunities. These source categories do not determine the W or R codes. W describes the most substantive mathematical action left unsupplied in the response; R describes information supplied relative to the active demand. A higher W value is not automatically better instruction.

The original response archive contained two separate AI coding passes, not independent human coding. All 114 main-pass excerpts were checked against their actual response text and all responses were checked against the original source-masked packets. This verifies traceability, not human reliability or construct validity. Retaining the second pass prevents the first-pass figures from being mistaken for adjudicated consensus.

Counts use all 38 responses per condition unless explicitly labeled assessable. NA remains missing/unclear evidence and is never treated as W0 or R0. There is one R-NA plain response and five W-NA human responses in the reported pass.

Data source: TutorMoments-Preview, pinned revision 3bb0c104d65e29facffca7ba864ef10fa22d0e78. Publisher: Zhang and colleagues, https://huggingface.co/datasets/allenai/tutormoments-preview . The source is CC BY 4.0; retain publisher attribution and the original responsible-use guidance. These archived texts do not establish later student learning. The human continuation is a naturalistic reference, not a randomized experimental arm.


## How the comparison frame and coding sample were formed

The initial preparation produced 370 matched mathematics situations. Excluding all students in the earlier pilot left 226 situations from 60 students (127 scaffolding and 99 rigor). Seed 20261022 selected 40 situations: one per student and 20 per source label. A later speech/event audit produced the final 346-situation comparison frame. It also excluded two locked cases, E20 and E24, because learner events intervened before the human response. The remaining 38 cases were retained without replacement; all 38 are included in the final 346 frame.

The 520-row eligibility ledger preserves the original moment index and scenario ID. The scope screen excluded 41 situations: 20 literacy/vocabulary, 3 general mindset, 14 logistics/greetings/recreation/closing, and 4 confidence or comfort ratings without an active reasoning demand. Separately, 29 situations were noncanonical repeated session/cuts and 126 lacked an aligned usable initial response across all 15 source response cells. These exclusions overlap. Applying scope, then canonical-cut, then all-response alignment gives 520 → 479 → 453 → 346. The 174 exclusions should therefore not be described as 174 nonmathematics situations.

The ledger is copied from the archived version-two preparation data; it introduces no new outcome-based eligibility screen. A 1 means eligible on the named criterion and 0 means ineligible. Human-tutor responses and fourteen AI response conditions make up the 15 source cells. Full source text is preserved in the archived dataset; the ledger adds no transcript alterations.
