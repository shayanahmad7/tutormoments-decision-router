# Examples of changed and persistent decisions

Selected on evaluation cases by highest new-prompt top probability, then index, separately for improvements, regressions and persistent errors. These are explanations from source inspection, not Jev-generated rationales or human adjudication. Reference notes are shown for review only and were never in Jev’s input.

## Improved: record 195

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.85).

**Last eight source turns**

> Student: Okay.

> Tutor: Okay.

> Tutor: Okay. So if if the denominator can be divided by the numerator evenly, that's the best way to do those. So, so what was the answer to the first one?

> Student: Three-fourths.

> Tutor: Three-fourths. Okay.

> Tutor: [PAUSE: 4 seconds] Tutor writes "3/4" as the answer for 12/16. Tutor then writes "1/5" as the answer for 3/15.

> Tutor: So... that's... I oops, I can't... I can't draw with my... And the answer to the second one would be one-fifth. So those are equivalent fractions. Three-fifteenths is exactly the same amount as one-fifth, but one-fifth is the simplest form of the fraction. It can't be reduced anymore.

> Tutor: So, try eight-tenths.


**Representative annotation note:** This could be an appropriate place to push for rigor because the student got the answer right away without any support. Pushing for rigor here will help internalize the skill and build fluency.

## Improved: record 418

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.73).

**Last eight source turns**

> Tutor: So two. So now we are pairing everything, but let's say like how many balls have I drawn that you have not crossed out? How many balls have I drawn that you have not crossed out?

> Student: Can you count them for me? Five.

> Tutor: [PAUSE: 8 seconds] Student draws a small curved line on the whiteboard.

> Student: Five.

> Tutor: Very good. So do you see like how one ball doesn't have a partner or a friend or a pair?

> Student: Yeah.

> Tutor: Right? So is five odd or even?

> Student: Odd.


**Representative annotation note:** This is an appropriate time to push for rigor because the tutor has explained a concept to the student, and it is important to find out what the student is taking away from that explanation.

## Improved: record 344

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.71).

**Last eight source turns**

> Tutor: [SCREEN_UPDATE] A pop-up appears with a green checkmark and the text "Nice work! You got it. Onward! See how we answered this question."

> Tutor: Okay, here is the next question. We have to construct a 90 degree angle.

> Tutor: [PROBLEM_CHANGE: p4 - 'Construct a 90° angle.' (start)] The screen changes to a new problem showing a semi-circular protractor.
> Tutor erases the "80" and the blue arrows from the whiteboard and writes "90°".

> Tutor: Okay, I'm gonna clear this out. We have to construct a 90 degree angle. I want you to draw both the rays this time, the whole angle. One at 0 degrees and one at 90 degrees.

> Tutor: Two lines, one at zero and one at 90.

> Tutor: [SCREEN_INTERACTION: student - drawing] Student draws a green arrow on the protractor, starting from the center and pointing to the 0-degree mark on the right.

> Tutor: [PAUSE: 45 seconds]

> Tutor: Yeah, that's right.


**Representative annotation note:** this moment does not call for rigor or scaffolding. it is simply the student drawing the angle from a semi-circular protractor

## Regressed: record 332

Reference: **scaffolding**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.68).

**Last eight source turns**

> Tutor: [SCREEN_INTERACTION: tutor - writing] Tutor erases the previous writing and writes "3/1" on the whiteboard.
> Writes "3/1 x 3/4 =" on the whiteboard.

> Tutor: Let's do it this way, right? So let's say three times three over one times four.

> Tutor: [PAUSE: 28 seconds]

> Tutor: You think it's one?

> Tutor: [PAUSE: 3 seconds] Circles the fraction 3/4 in the problem on the screen.

> Tutor: Did you read their note? They said, did you multiply both the top and bottom of the fraction? Remember, only multiply the top part by the number.

> Tutor: [SCREEN_INTERACTION: student - drawing] Student circles the answer choice B, which is 9/4.

> Student: Yeah.


**Representative annotation note:** IS a moment for rigor. Student got the right answer but said "okay" without really explaining why it is nine over four.

## Regressed: record 428

Reference: **scaffolding**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.65).

**Last eight source turns**

> Tutor: Sorry, it's late here, so I'm a bit, um, tired.

> Student: I I can't see you.

> Tutor: You can't?

> Student: Oh.

> Student: I can't see you.

> Tutor: Can you see the question, though?

> Student: Yeah.

> Student: I think it's, um, A.


**Representative annotation note:** Student guessed through options without understanding the pattern, good moment to scaffold.

## Regressed: record 231

Reference: **scaffolding**. Fresh control: **scaffolding**. New prompt: **rigor** (top probability 0.64).

**Last eight source turns**

> Tutor: [PAUSE: 2 seconds]

> Tutor: Okay.

> Tutor: [SCREEN_INTERACTION: tutor - clicks 'Check'] Tutor clicks the "Check" button on the screen.

> Tutor: [PAUSE: 1 second] The screen displays an explanation for the answer. The text reads: "In the second row, we write a 0 in the ones column to show we are multiplying by 30 instead of 3."
> Tutor erases her writing from the whiteboard.

> Tutor: Right. In the second row, we write a zero in the ones column to show we are multiplying by thirty instead of three.

> Tutor: So right, does that make sense? That because when you do the three times seven, because the three is in the tens place, you have to have a zero at the end to kind of shift the numbers down. When we start working with decimals, I think it'll make even more sense. Okay, let's do the next one. Oh, I didn't erase any of this. Where? Okay, there we go. Boop boop boop boop boop.

> Tutor: Go ahead and read that question to me.

> Student: Ellie is using distribute method to calculate forty eight times three. What should replace the star?


**Representative annotation note:** This is a place to scaffold because the student states that they do not remember learning this last year and they were not sure how to solve.

## Persistent Error: record 375

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **scaffolding** (top probability 0.97).

**Last eight source turns**

> Student: Ten?

> Tutor: [SCREEN_INTERACTION: student - selecting and checking answer] Student clicks on option B, "10", and then clicks the "Check" button.

> Tutor: [SCREEN_UPDATE] The screen shows "B is correct!" and provides feedback: "With 10 lots of 10 ones we would need 10 bundles of 10 sticks to make 100 sticks in total."

> Tutor: [SCREEN_INTERACTION: student - proceeding to next question] Student clicks the "Next" button.

> Tutor: [PROBLEM_CHANGE: p4 - '4 tens and 1 hundred = ___ tens' (start)] A new problem appears. The question is "4 tens and 1 hundred = ___ tens". The options are: A) 140, B) 14, C) 41, D) 410.

> Student: Forty.

> Tutor: [PAUSE: 15 seconds]

> Student: Four hundred and one?


**Representative annotation note:** This is an appropriate place to scaffold becuase the student is confused.  Providing a scaffold can help the student slow down and build on their understanding to master a new skill.

## Persistent Error: record 65

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **scaffolding** (top probability 0.96).

**Last eight source turns**

> Tutor: [PAUSE: 10 seconds]

> Tutor: [PROBLEM_CHANGE: p1 - '☆ x 11 = -165' (start)] On the whiteboard, the equation '☆ x 11 = -165' is written in black marker. An arrow is drawn from the star symbol to the number 11.
> Tutor rewrites the equation '☆ x 11 = -165' below the original one.

> Tutor: Star times eleven equals minus one sixty-five.

> Tutor: Kayla, you think one fifty... It's multiplication, Kayla, it's not addition. It's multiplication.

> Tutor: [PAUSE: 7 seconds]

> Tutor: No, Kayla, do one sixty-five divided by eleven. Write it out on a... Do you have a piece of paper? Can you write it out?

> Tutor: [PAUSE: 27 seconds]

> Student: Mm, mm, mm, mm, mm.


**Representative annotation note:** This is an appropriate time to push for rigor because the student is on the challenge question as a result of getting all the questions within the previous skill correct. Pushing for rigor here will help deep students conceptual understanding of the topic being covered.

## Persistent Error: record 179

Reference: **rigor**. Fresh control: **scaffolding**. New prompt: **scaffolding** (top probability 0.96).

**Last eight source turns**

> Tutor: But there was though, uh, could you explain why you chose C? Because it's multiplication.

> Tutor: [PROBLEM_CHANGE: p1 - 'Indie buys 5 bags of candies which each contain c bars. In total there are 40 candy bars. Which equation represents this situation?' (start)] The problem is displayed on the screen with four multiple-choice options: A) c = 5 x 40, B) 40 = c x 5, C) 5 = c x 40, D) c ÷ 40 = 5.

> Tutor: was the uh could you explain why you chose C?

> Student: Because it's multiplication.

> Tutor: [PAUSE: 5 seconds]

> Student: I ran away. I ran away.

> Tutor: You got it right. It was B, but why was it B? Do you know why it was B?

> Student: No, I just guessed, like always.


**Representative annotation note:** IS an appropriate time to push for rigor. The student got the right answer by luck and admits it clearly, so this is a perfect opening to build real understanding.
