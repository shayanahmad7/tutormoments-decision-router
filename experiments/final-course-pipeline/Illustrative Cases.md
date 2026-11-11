# Illustrative contrasts

Selection rule: for each stated contrast, choose the lowest zero-based source index within the pre-existing strict matched mathematics frame that meets the observed contrast. These are transparent post-outcome illustrations, not a representative sample or a new scored analysis. Pass/fail descriptions refer to the primary Gemini evaluator. Source categories were not changed.

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

### self_detailed (primary pass: True)

Okay, so you're trying to figure out 1,000 minus 10. Let's write it out like this:  
1,000  
- 10  
________  

Now, subtract the ones place first. What do you get when you subtract 0 minus 0?

Evaluator rationale: The student is struggling with 1000 - 10. The tutor provides a scaffold by setting up the subtraction problem vertically and then guiding the student to start with the ones place.

### force_scaffolding (primary pass: False)

Let's go back to the problem on the screen: 338 + 586 = 924. So, 924 - 586 = ?

You mentioned that 338 + 586 = 924. If I take away 586 from 924, what number am I left with? Can you look at the original addition to help you figure it out?

Evaluator rationale: The tutor is trying to go back to a previous problem that the student already solved correctly. The student is currently working on 1000 - 10, which is a different problem related to the volume of cubes.

### force_rigor (primary pass: True)

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

### self_detailed (primary pass: True)

So, if we write 3 as a fraction with denominator 1, it's $ \frac{3}{1} $. Now, how can we multiply $ \frac{3}{4} $ by 3 (or $ \frac{3}{1} $) to find the result? What happens when you multiply the numerators and denominators?

Evaluator rationale: The tutor explicitly states how to write 3 as a fraction and then prompts the student on the next steps for multiplying fractions, which is a clear scaffold.

### force_scaffolding (primary pass: True)

So you're saying three is the same as 3/1. That's right! Now, if we want to multiply 3/1 by 3/4, how can we start? What do we need to do with the numerators and denominators?

Evaluator rationale: The tutor affirms the student's implicit understanding of writing 3 as a fraction and then guides them to the next step of multiplying fractions by asking about numerators and denominators.

### force_rigor (primary pass: True)

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

### self_detailed (primary pass: False)

So if you're subtracting 8 and ending up at 3 on the number line, how many steps back did you take? What number do you get when you subtract that from 8 to reach 3?

Evaluator rationale: The tutor is guiding the student to think about the subtraction in terms of steps on a number line, which is a helpful visual and conceptual scaffold for this type of problem.

### force_scaffolding (primary pass: False)

So you have 8, and you want to get to 3. If you take away 5 from 8, what do you get? Try that step.

Evaluator rationale: The student has already said 'The A' which is likely the answer 5. The tutor is asking the student to verify their answer by performing the subtraction, which is a good scaffolding step.

### force_rigor (primary pass: True)

So you said five. Let me see — if you start at eight on the number line and subtract five, does that get you to three? Why or why not?

Evaluator rationale: The tutor asks the student to verify their answer and then justify it, which promotes deeper thinking and rigor. The 'why or why not' part is particularly good for rigor.

Interpretation: The student had supplied five for eight minus an unknown number equaling three. Jev selected rigor. The selected reply asked the student to check and justify that answer; the evaluator rated both rigor and scaffolding. The self-choice reply was rated as scaffolding only. This is one positive contrast, not a claim that adding a why-question is sufficient in general.
