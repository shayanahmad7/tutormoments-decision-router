# Four original-prompt tutoring replays

Generated tutor/student dialogue and automated scorer judgments. These are not new human student observations.

## Moment 310: scaffolding

### Last six original turns

**Tutor:** [SCREEN_UPDATE] A message appears: "B is correct!" along with an explanation.

**Tutor:** [SCREEN_INTERACTION: student - clicking] Student clicks the "Next" button.

**Tutor:** [PROBLEM_CHANGE: p2 - 'What should replace the star? ⭐ - 37 = 38' (start)] A new problem appears on the screen: "What should replace the star? ⭐ - 37 = 38". The multiple-choice options are A) 75, B) 1, C) -1, D) 65.

**Student:** Uh...

**Tutor:** [PAUSE: 24 seconds]

**Student:** Wait, um, B?

### Generated exchange

**Tutor:** Let’s check B, which is 1. Could you start with 1, take away 37, and have 38 left? Explain your thinking.

**Student:** Um, no.

**Tutor:** Right—1 doesn’t work. If taking away 37 leaves you with 38, how could you work backward to find how many you started with?

**Student:** Um, subtract them?

**Tutor:** Imagine ⭐ is how many blocks you started with. You move 37 blocks into a box, and 38 stay on the table. How could you use those two groups to find how many blocks you started with?

### Automated scoring

Action: **scaffolding**. Over-scaffolding: **False**. Publisher-rule success: **True**.

The tutor scaffolds in multiple ways. First, they guide the student to evaluate and eliminate an incorrect answer choice. When the student incorrectly proposes subtraction as the backward strategy, the tutor introduces a concrete real-world analogy involving blocks on a table and blocks in a box to help the student visualize combining two groups to find the original total.

The tutor's strategy is partially effective. The student achieves a small win by correctly recognizing that the wrong answer choice doesn't work, but the student's suggestion of subtraction reveals persistent confusion about the inverse operation needed. The moment ends before the student can respond to the tutor's analogy, so it is unclear whether the scaffolding resolved the underlying misconception.

Over-scaffolding spans: []

## Moment 251: scaffolding

### Last six original turns

**Tutor:** [PAUSE: 10 seconds]

**Student:** Three.

**Tutor:** Uh-huh.

**Tutor:** [PAUSE: 4 seconds]

**Tutor:** Now, what do we do next?

**Student:** Remainder three.

### Generated exchange

**Tutor:** Yes—31 with 3 left over. A full group has 6, so what fraction of another group do those 3 leftovers make?

**Student:** Um, three over six?

**Tutor:** Yes—\(\frac{3}{6}\) of another group. What simpler fraction names that same amount, and how do you know?

**Student:** Um, I don't know.

**Tutor:** Let’s picture six equal pieces, with three shaded:

■ ■ ■ □ □ □

That shows \(\frac{3}{6}\). How does the shaded amount compare with the unshaded amount?

### Automated scoring

Action: **both**. Over-scaffolding: **False**. Publisher-rule success: **True**.

The tutor initially pushes for rigor by asking the student to simplify the fraction and explain their reasoning. When the student says they don't know, the tutor pivots to scaffolding by presenting a visual diagram of the fraction and asking a guiding comparison question to lead the student toward recognizing the simplified form.

The tutor's strategy is partially effective. The pivot from rigor to scaffolding is well-calibrated to the student's expressed confusion, and the visual representation is a reasonable scaffold. The student demonstrated a small win by correctly identifying the unsimplified fraction. However, the moment ends before we can see whether the student benefits from the visual scaffold, so there is insufficient evidence of a clear learning outcome from the scaffolding move itself.

Over-scaffolding spans: []

## Moment 326: rigor

### Last six original turns

**Tutor:** [PAUSE: 4 seconds]

**Tutor:** Do you wanna read it out for me?

**Tutor:** [PAUSE: 8 seconds]

**Student:** A square traffic sign has sides of length five feet. What is the perimeter of the sign? A, twenty-five feet. B, twenty feet. C, ten feet. D, nine feet.

**Tutor:** [PAUSE: 36 seconds]

**Student:** B.

### Generated exchange

**Tutor:** Yes, 20 feet. How would you convince someone who chose 25 feet that your answer gives the distance around the sign?

**Student:** Um, since a square has four sides and each side is five feet, you have to add all four sides together. So it's five plus five plus five plus five, which is twenty feet. And if someone picked twenty-five, they probably did five times five, which is the area, not the perimeter.

**Tutor:** You clearly explained the difference between perimeter and area. Could a rectangular sign have the same 20-foot perimeter as this square but a different area? Use specific side lengths to justify your answer.

**Student:** Um, I'm not sure.

**Tutor:** Let’s try a rectangle that’s 6 feet long. What width would make the distance all the way around exactly 20 feet? You can sketch it to keep track of the sides.

### Automated scoring

Action: **both**. Over-scaffolding: **False**. Publisher-rule success: **True**.

The tutor pushes for rigor by asking the student to justify their answer and explain why an alternative (incorrect) answer is wrong. When the student responds with a strong explanation, the tutor pushes further by posing a deeper conceptual question about whether a different shape could share the same perimeter but have a different area. When the student expresses uncertainty, the tutor scaffolds by providing a specific starting value and suggesting the student sketch the shape.

The tutor's strategy is effective. The student rises to the initial rigor push by clearly articulating the difference between perimeter and area and identifying the likely error behind the wrong answer. The follow-up conceptual extension is well-calibrated, and the tutor appropriately shifts to scaffolding when the student signals uncertainty, providing a concrete entry point without giving away the answer.

Over-scaffolding spans: []

## Moment 377: rigor

### Last six original turns

**Student:** So, um, I could try. Yeah.

**Tutor:** [PAUSE: 73 seconds] The student is thinking, resting her chin on her hand.

**Student:** Wait, so Colin is um counting by fives or skip counting?

**Tutor:** [PAUSE: 4 seconds]

**Tutor:** [PROBLEM_CHANGE: p1 - 'Skip counting in 5s' (start)] The screen shows a problem: "Colin is skip counting in 5s. 456, 461, 466, ___. What number should go in the box?". The options are A) 455, B) 471, C) 451, D) 446.

**Student:** Four hundred and four hundred and fifty-one.

### Generated exchange

**Tutor:** Counting by fives and skip counting in fives mean the same thing. Let’s check your idea with the pattern:

**456, 461, 466, ___**

How do the numbers change each time—and would 451 keep that pattern going?

**Student:** Um, they go up by five each time?

**Student:** So, four hundred and seventy-one?

**Tutor:** Yes, 471 fits! Now let’s extend the same pattern backward:

**___, 456, 461, 466, 471**

What number belongs before 456, and how could you check that it fits?

**Student:** Um, so you go back five from four hundred and fifty-six?

**Student:** Four hundred and fifty-one.

**Tutor:** Yes—you went back five to get 451. How could you check that it fits by counting forward?

### Automated scoring

Action: **both**. Over-scaffolding: **True**. Publisher-rule success: **False**.

The tutor mostly scaffolds by presenting structured pattern tasks and confirming answers, but includes a push for rigor at the end by asking the student to verify their answer using a different approach (counting forward to check). The tutor also guides the student through a backward extension of the pattern, which adds mild complexity.

The tutor's strategy is partially effective. The student demonstrates understanding throughout, correctly identifying the pattern rule and applying it in both directions. The final rigor move — asking the student to explain how they could verify their answer — is a meaningful metacognitive prompt. However, given the student's consistent success, the tutor could have pushed harder for independence or increased complexity rather than continuing to set up each sub-task and confirm answers along the way.

Over-scaffolding spans: ["given the student's consistent success, the tutor could have pushed harder for independence or increased complexity rather than continuing to set up each sub-task and confirm answers along the way"]
