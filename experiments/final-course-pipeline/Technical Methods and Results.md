# Decision-Guided Tutoring: Methods and Complete Results

Companion to the EDUC 6181 conference paper. This document explains the technical study and points to the complete records. The study uses the public TutorMoments-Preview dataset, released by the Allen Institute for AI and collaborators under CC BY 4.0: https://huggingface.co/datasets/allenai/tutormoments-preview .

## 1. What we tried to improve

A tutor needs to decide whether a student needs more support or is ready to explain, justify, or work more independently. We tested whether a separate model could make this decision before a smaller language model writes the tutor's reply. The intended sequence is: conversation history, then a scaffold-or-rigor decision, then detailed instructions for that direction, then the tutor's response.

Jev 1.14.0 and OpenAI Decisions with GPT-6 Luna made the choices. Qwen3-32B wrote the replies. This is an inference-time method: we did not train or fine-tune any model.

## 2. What data went into the test

We used all 520 balanced evaluation moments, 260 labeled scaffolding and 260 rigor, from 89 students. Each input contains the complete conversation before the stopping point. The decision models do not receive the assigned label, teacher explanation, later conversation, or simulated learner persona. Qwen receives the same preceding dialogue plus the publisher's student metadata.

We also report a previously defined 346-moment mathematics comparison set. This set requires suitable turn boundaries, removal of duplicate cuts, and usable original responses as well as mathematical content. It must not be interpreted as a subject-only filter.

## 3. First test: does the decision match the assigned category?

Earlier prompt development asked each system to return scaffolding or rigor. We retained the strongest completed configurations for the response test. Later revisions and unsuccessful alternatives remain in the complete package. Prompt development used this same preview dataset, so these are exploratory results rather than performance on unseen data.

| Decision system | Selected prompt | Later revision |
|---|---:|---:|
| Jev 1.14.0 | 376/520 (72.3%) | 367/520 (70.6%) |
| OpenAI Decisions, GPT-6 Luna | 386/520 (74.2%) | 372/520 (71.5%) |
| GPT-6 Luna, ordinary one-word response | 373/520 (71.7%) | 377/520 (72.5%) |

These percentages measure agreement with the assigned category. They do not measure the quality of a generated tutoring response. Three pairs of records share identical visible input but opposite assigned labels, which also cautions against treating every label as the only defensible next action.

## 4. Second test: does the selected instruction improve the reply?

For every moment, Qwen produced three replies. In self-choice, it received both instruction sets and selected an approach itself. The scaffold-guided reply received the scaffolding instruction. The rigor-guided reply received the rigor instruction. All three retained the publisher's evaluation-aware tutoring prompt. There were 1,560 actual generations, not seven separate generations per moment.

The saved Jev and Decisions outputs selected the corresponding scaffold or rigor reply. Using the same two candidate replies makes the comparison depend on the decision rather than on different random generations. We also selected the scaffold reply for every case, the rigor reply for every case, the reply named by the dataset label, and the opposite reply. The last two are diagnostic controls with access to the label; they cannot be deployed as autonomous tutors.

We fixed the prompts and analysis before the new replies and judgments. Generation used Qwen3-32B in non-thinking mode, temperature zero, a fixed provider and a 384-token output cap. Every moment completed, and no reply was truncated. Full requests, responses, provider names, usage, and timing are retained in the package.

## 5. How we evaluated replies

Gemini 2.5 Flash saw the context and three anonymous replies in randomized order, without the assigned label. It judged scaffolding, rigor, over-helping, mathematical correctness, and context fit. We then compared those judgments with the assigned category. A pass required the appropriate direction, no over-helping or math error, full context fit, and a valid reply. A reply expressing both directions could satisfy either label.

Claude Sonnet 4.6 repeated the evaluation for a fixed 32-case subset, one moment per student and balanced by category. Uncertainty estimates resample students, keeping moments from the same student together. The task evaluates the first tutor reply, whereas the original TutorMoments leaderboard evaluates multi-turn replays with a simulated student. Their percentages are not directly comparable.

## 6. All response results

| Instruction selection | All 520 | Scaffold /260 | Rigor /260 | Math set /346 |
|---|---:|---:|---:|---:|
| Qwen chooses | 357 (68.7%) | 208 | 149 | 249 (72.0%) |
| Jev chooses | 379 (72.9%) | 199 | 180 | 252 (72.8%) |
| OpenAI Decisions chooses | 382 (73.5%) | 210 | 172 | 260 (75.1%) |
| Always scaffold | 294 (56.5%) | 224 | 70 | 207 (59.8%) |
| Always rigor | 385 (74.0%) | 171 | 214 | 263 (76.0%) |
| Use dataset label | 438 (84.2%) | 224 | 214 | 299 (86.4%) |
| Use opposite label | 241 (46.3%) | 171 | 70 | 171 (49.4%) |

Jev improved over self-choice by 4.2 percentage points (95% student-cluster interval -1.0 to 9.2). Decisions improved by 4.8 points (0.2 to 9.5). Neither exceeded fixed rigor. In the mathematics comparison set, Jev's advantage was 0.9 points (-5.3 to 6.5); Decisions' was 3.2 points (-2.2 to 8.3).

On the same 32 audit cases, Gemini passed 20 self-choice replies and 19 Jev-selected replies. Claude passed 16 and 22. The two evaluators agreed on 75/96 reply judgments, or 78.1% (kappa .551). The direction of Jev's apparent advantage therefore depends on the evaluator in this small subset. These ratings have not been independently validated by human raters.

## 7. What the results mean

The separate decision step improved the overall point estimate relative to Qwen choosing for itself, but the best simple instruction did slightly better. This experiment does not establish that the router is necessary. It also does not establish that rigor is always appropriate: the evaluator recognized both scaffold and rigor behavior in 202/520 replies generated with rigor instructions.

Matching the label and producing a good response were different problems. Of Jev's 376 category matches, 320 selected replies passed. Of its 144 category mismatches, 59 still passed. Across the two guided replies, both passed at 214 moments, only rigor passed at 171, only scaffold passed at 80, and neither passed at 55. Even a correct assigned-category decision left 82 failed replies. A better choice alone cannot fix all response-generation errors.

## 8. Timing and cost

Qwen began answering after a median 1.20 seconds in self-choice. Adding separately measured routing durations gives estimated medians of 1.43 seconds for Jev and 1.60 seconds for Decisions. These sums are estimates from component measurements, not measurements of a running end-to-end pipeline. They do not demonstrate a speed improvement.

Estimated model cost per 1,000 selected replies was $0.59 for self-choice, $0.90 for Jev, and $1.25 for Decisions, excluding evaluation. New spending on the complete response experiment, both evaluators, and conservative failed-call reservations was $3.0029. No new API calls were made for the writing revision.

## 9. Inspecting and reproducing the study

All 520 Cases - Replies and Results.csv provides a case-by-case table. Technical Experiment - Complete Review Package.zip contains every source context, prior decision, actual reply, evaluation, protocol, and analysis script. Unzip it and run python3 reproduce_summary.py inside the extracted Technical Experiment folder to regenerate the main results without network access, credentials, or paid calls. The package also retains earlier pilots, all prompt variants, evaluator disagreements, and interrupted attempts.

The implementation is maintained at https://github.com/shayanahmad7/tutormoments-decision-router . The repository is private; the Drive package provides the complete review copy without requiring GitHub access. The original data and source labels are preserved. This work measures model behavior in text, not student learning.

## 10. Concrete examples

The following examples were selected by a fixed rule: for each contrast, use the lowest source index within the existing mathematics comparison set that meets it. They illustrate outcomes; they are not a representative sample. All pass/fail descriptions below refer to Gemini's primary ratings.

## Correct category, unsuccessful reply
Moment 24; zero-based index 23; source category: scaffolding; Jev: scaffolding; Decisions: scaffolding.

### Last ten context records (verbatim)

> Turn 286, tutor: Now, now you know this, there's one thousand cubes in this big cube, right?
> Turn 287, student: Yeah.
> Turn 288, tutor: So then how many cubes are in this one?
> Turn 289, student: Ten.
> Turn 290, tutor: So now it's a thousand minus ten. What do you get?
> Turn 291, student: Hundred.
> Turn 292, tutor: No. One thousand minus ten.
> Turn 293, tutor: You can work it out.
> Turn 294, student: One thousand minus ten. One comma zero zero zero minus ten.
> Turn 295, student: We got zero, zero, zero, zero.

### Qwen chooses its approach (primary pass: True)

Okay, so you're trying to figure out 1,000 minus 10. Let's write it out like this:  
1,000  
- 10  
________  

Now, subtract the ones place first. What do you get when you subtract 0 minus 0?

Evaluator rationale: The student is struggling with 1000 - 10. The tutor provides a scaffold by setting up the subtraction problem vertically and then guiding the student to start with the ones place.

### Scaffold-guided reply (primary pass: False)

Let's go back to the problem on the screen: 338 + 586 = 924. So, 924 - 586 = ?

You mentioned that 338 + 586 = 924. If I take away 586 from 924, what number am I left with? Can you look at the original addition to help you figure it out?

Evaluator rationale: The tutor is trying to go back to a previous problem that the student already solved correctly. The student is currently working on 1000 - 10, which is a different problem related to the volume of cubes.

### Rigor-guided reply (primary pass: True)

Okay, so you said one thousand minus ten. Let me see how you figure that out. Can you write it down step by step on the whiteboard?

Evaluator rationale: The student is struggling with 1000 - 10. The tutor asks the student to write it down on the whiteboard, which encourages the student to show their work and take responsibility for the next step, while also providing a visual aid for the tutor to understand the student's thought process.

Interpretation: Both routers chose scaffolding, matching the source. The selected reply nevertheless returned to an earlier addition problem instead of the current 1,000 minus 10 task. The evaluator marked context_fit=0. Self-choice stayed with the current task and passed. This separates category selection from contextual execution.

## Category mismatch, successful reply
Moment 5; zero-based index 4; source category: scaffolding; Jev: rigor; Decisions: rigor.

### Last ten context records (verbatim)

> Turn 165, student: We shouldn't ever do this.
> Turn 166, tutor: We've done this before. Just see if you can pull out of your memory like how to solve these kinds of questions.
> Turn 167, tutor: [PAUSE: 1 second]
> Turn 167, tutor: Okay. So, do you remember what a whole number like how to write a whole number in a fraction?
> Turn 168, student: You like do what you do to the top to the bottom or something.
> Turn 169, tutor: So, that's if we're trying to find an equivalent fraction.
> Turn 170, student: Oh.
> Turn 171, tutor: But if you multiply three over four times three, what is three written in fraction form?
> Turn 172, tutor: What can we put in as the denominator to make three a fraction?
> Turn 173, student: Uh, one.

### Qwen chooses its approach (primary pass: True)

So, if we write 3 as a fraction with denominator 1, it's $ \frac{3}{1} $. Now, how can we multiply $ \frac{3}{4} $ by 3 (or $ \frac{3}{1} $) to find the result? What happens when you multiply the numerators and denominators?

Evaluator rationale: The tutor explicitly states how to write 3 as a fraction and then prompts the student on the next steps for multiplying fractions, which is a clear scaffold.

### Scaffold-guided reply (primary pass: True)

So you're saying three is the same as 3/1. That's right! Now, if we want to multiply 3/1 by 3/4, how can we start? What do we need to do with the numerators and denominators?

Evaluator rationale: The tutor affirms the student's implicit understanding of writing 3 as a fraction and then guides them to the next step of multiplying fractions by asking about numerators and denominators.

### Rigor-guided reply (primary pass: True)

So if three is three over one, how can we multiply that by three over four? What does that look like?

Evaluator rationale: The tutor provides the correct fraction form for 3 and then asks the student to apply that knowledge to the multiplication problem, which is a helpful next step.

Interpretation: Both routers chose rigor despite the source scaffolding category. The selected reply restated three as three over one and asked how to multiply it by three over four. The evaluator counted this as scaffolding and passed it. A forced-policy label does not guarantee an exclusive behavioral category.

## Routed reply passes while self-choice fails
Moment 26; zero-based index 25; source category: rigor; Jev: rigor; Decisions: rigor.

### Last ten context records (verbatim)

> Turn 357, tutor: Uh-oh.
> Turn 358, tutor: [PAUSE: 13 seconds]
> Turn 358, tutor: Let's do this one. We're just gonna go in order.
> Turn 359, student: No, number line.
> Turn 360, tutor: [PAUSE: 22 seconds]
> Turn 360, student: The A.
> Turn 361, tutor: [PAUSE: 7 seconds]
> Turn 361, tutor: Did you look at what numbers are you using? So you have eight and you're going back to three. So what do you have to subtract eight by to get three?
> Turn 362, tutor: [PAUSE: 12 seconds]
> Turn 362, student: Five.

### Qwen chooses its approach (primary pass: False)

So if you're subtracting 8 and ending up at 3 on the number line, how many steps back did you take? What number do you get when you subtract that from 8 to reach 3?

Evaluator rationale: The tutor is guiding the student to think about the subtraction in terms of steps on a number line, which is a helpful visual and conceptual scaffold for this type of problem.

### Scaffold-guided reply (primary pass: False)

So you have 8, and you want to get to 3. If you take away 5 from 8, what do you get? Try that step.

Evaluator rationale: The student has already said 'The A' which is likely the answer 5. The tutor is asking the student to verify their answer by performing the subtraction, which is a good scaffolding step.

### Rigor-guided reply (primary pass: True)

So you said five. Let me see — if you start at eight on the number line and subtract five, does that get you to three? Why or why not?

Evaluator rationale: The tutor asks the student to verify their answer and then justify it, which promotes deeper thinking and rigor. The 'why or why not' part is particularly good for rigor.

Interpretation: The student had supplied five for eight minus an unknown number equaling three. Jev selected rigor. The selected reply asked the student to check and justify that answer; the evaluator rated both rigor and scaffolding. The self-choice reply was rated as scaffolding only. This is one positive contrast, not a claim that adding a why-question is sufficient in general.
