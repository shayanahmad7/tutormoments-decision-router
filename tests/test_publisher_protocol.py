import copy
import unittest
from tm_router import publisher_protocol as p


def toy():
    return {"id": "toy", "dimension": "rigor", "rubric": {"hint": "SCORER_ONLY"},
            "provenance": {"cut_turn": 4},
            "context": [{"turn_number": 1, "role": "tutor", "text": "What is two plus three?"},
                        {"turn_number": 4, "role": "student", "text": "Five."}],
            "student": {"context": "K-12 math.", "reference": "ORACLE_FUTURE",
                        "trait": {"persona": "ORACLE_PERSONA"}}}


class PublisherProtocolTests(unittest.TestCase):
    def test_routing_preserves_baseline_and_is_not_student_history(self):
        m = toy()
        original = p.tutor_messages(m, "scaffolding_rigor")
        routed = p.tutor_messages(m, "scaffolding_rigor", route_instruction=p.route_instruction("rigor"))
        self.assertEqual(routed[:-1], original)
        self.assertEqual(routed[-1]["role"], "developer")
        self.assertEqual(len(original), 1)
        self.assertNotIn("ORACLE_FUTURE", original[0]["content"])
        self.assertNotIn("ORACLE_PERSONA", original[0]["content"])
        self.assertNotIn("SCORER_ONLY", original[0]["content"])
        self.assertIn("ORACLE_FUTURE", p.student_messages(m)[0]["content"])
        self.assertIn("ORACLE_PERSONA", p.student_messages(m)[0]["content"])

    def test_router_allowlist_ignores_all_hidden_fields(self):
        m = toy()
        altered = copy.deepcopy(m)
        altered.update(dimension="scaffolding", rubric={"hint": "SECRET", "gold": "SECRET"})
        altered["student"] = {"reference": "SECRET", "trait": {"persona": "SECRET"}, "context": "SECRET"}
        self.assertEqual(p.router_messages(m), p.router_messages(altered))

    def test_split_messages_do_not_change_call_limit_and_end_wins(self):
        cleaned, ended, changed = p.parse_tutor_output("A[NEW_MESSAGE]B[PROBLEM_CHANGE][END]")
        self.assertTrue(ended)
        self.assertFalse(changed)
        g = p.append_generated_turns(toy(), [], "TUTOR", p.split_messages(cleaned))
        self.assertEqual([x["turn_number"] for x in g], [5, 6])
        self.assertEqual(p.MAX_SPEAKING_TURNS, 5)
        self.assertEqual(p.split_messages("A[NEXT]B"), ["A", "B"])

    def test_active_scorer_has_generated_only_excerpt(self):
        m = toy()
        g = p.append_generated_turns(m, [], "TUTOR", ["Explain why."])
        prompt = p.scorer_annotate_prompt(m, g)
        self.assertIn("Turn 5. TUTOR: Explain why. <<<", prompt)
        self.assertNotIn("Turn 4. STUDENT: Five.", prompt)
        self.assertIn("A team of teachers believe that this moment is appropriate for pushing for rigor.", prompt)
        self.assertIsNone(p.scorer_structure_prompt([]))
        self.assertEqual(p.parse_action_label('{"scaffolding":"no","rigor":"yes"}'), "rigor")
        self.assertEqual(p.parse_action_label('{"scaffolding":"yes","rigor":"yes"}'), "both")
        self.assertEqual(p.parse_action_label("invalid"), "unclear")
        self.assertEqual(p.parse_facets('{"spans": []}'), [])
        self.assertEqual(p.parse_facets("invalid"), [])

    def test_route_instruction_never_enters_student_or_scorer(self):
        m = toy()
        marker = "ROUTE_DIRECTIVE_ONLY_98765"
        routed = p.tutor_messages(m, "scaffolding_rigor", route_instruction=marker)
        self.assertEqual(routed[-1]["content"], marker)
        g = p.append_generated_turns(m, [], "TUTOR", ["Explain why."])
        self.assertNotIn(marker, p.student_messages(m, g)[0]["content"])
        self.assertNotIn(marker, p.scorer_annotate_prompt(m, g))
        self.assertNotIn(marker, p.router_messages(m, g)[0]["content"])
        self.assertNotIn(marker, p.tutor_messages(m, "scaffolding_rigor", g)[0]["content"])

    def test_original_problem_change_tokens_are_terminal(self):
        self.assertEqual(p.parse_tutor_output("Next task.[PROBLEM_CHANGE]"), ("Next task.", False, True))
        self.assertEqual(p.parse_tutor_output("Next task.[NEXT_PROBLEM]"), ("Next task.", False, True))
        self.assertEqual(p.parse_tutor_output("[END]"), ("", True, False))

    def test_over_scaffolding_excludes_otherwise_correct_direction(self):
        m = toy()
        result = p.publisher_metrics([(m, {"action_label": "both", "overscaffold_decomposed": ["Too much help."]})])
        self.assertEqual(result["rigor_calibrated"]["score"], 0)
        self.assertEqual(result["avoids_overscaffold"], 0)
        self.assertIsNone(result["scaffold_calibrated"]["score"])


if __name__ == "__main__":
    unittest.main()
