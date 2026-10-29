"""Offline end-to-end runner regressions; no API calls or active-state writes."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tm_router import publisher_protocol as protocol
from tm_router.reliability import (
    first_decision_agreement, metric_coverage, paired_scored_comparison,
    publisher_no_generated_annotation, recover_terminal_checkpoint,
)

STAGE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reliability_test_runner", STAGE / "run_pilot.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def toy(index=0):
    return {
        "id": f"toy-{index}", "dimension": "rigor", "rubric": {"hint": "SCORER_ONLY"},
        "provenance": {"cut_turn": 4},
        "context": [{"turn_number": 4, "role": "student", "text": "Five."}],
        "student": {"context": "Math.", "reference": "ORACLE_FUTURE",
                    "trait": {"persona": "ORACLE_PERSONA"}},
    }


def state(index, condition, status="scored", generated=None):
    return {
        "moment_index": index, "moment_id": f"toy-{index}", "condition": condition,
        "status": status, "generated_turns": generated if generated is not None else [
            {"turn_number": 5, "role": "TUTOR", "text": "Explain why."}],
        "next_speaking_step": 5, "calls": [], "routes": [],
        "stop_reason": "max_five_speaking_calls",
        "annotation": {"situation": "Ready.", "action": "Asks why.", "result": "Explains.",
                       "action_label": "rigor", "action_decomposed": ["Asks why."],
                       "overscaffold_decomposed": []},
    }


class FakeClient:
    calls = []
    tutor_outputs = {}

    def __init__(self, *args, **kwargs):
        pass

    def record(self, tag):
        self.calls.append(tag)
        return {"request_id": f"fake-{len(self.calls)}", "elapsed_ms": 1,
                "attempts": [{"http_status": 200}], "payload_sha256": "fake",
                "response": {"model": "offline", "usage": {}}}

    def decide(self, messages, tag, model):
        assert "SCORER_ONLY" not in str(messages)
        assert "ORACLE_FUTURE" not in str(messages)
        return {"type": "choice", "name": "next_teaching_mode", "choice": "scaffolding"}, self.record(tag)

    def chat(self, model, messages, tag, **kwargs):
        assert kwargs["max_completion_tokens"] == 128000
        record = self.record(tag)
        if tag.endswith(":tutor"):
            assert kwargs["reasoning_effort"] == "high"
            assert "SCORER_ONLY" not in str(messages)
            assert "ORACLE_FUTURE" not in str(messages)
            step = int(tag.split(":")[2])
            return self.tutor_outputs[step], record
        if tag.endswith(":student_proxy"):
            assert kwargs["reasoning_effort"] == "low"
            assert "ORACLE_FUTURE" in str(messages)
            return "I think so.", record
        if tag.endswith(":judge_annotate"):
            return json.dumps({"situation": "Ready.", "action": "Asks a question.", "result": "Responds."}), record
        if ":judge_decompose_" in tag:
            assert kwargs["response_format"]["type"] == "json_schema"
            return '{"facets":[]}', record
        raise AssertionError("Unexpected call: " + tag)


class RunnerReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.moments = [toy(0), toy(1)]
        self.conditions = ["original_evaluation_aware", "evaluation_aware_plus_decisions"]
        self.source = self.root / "moments.jsonl"
        self.source.write_text("".join(json.dumps(m) + "\n" for m in self.moments))
        self.config = self.root / "configs/test.json"
        self.config.parent.mkdir()
        self.run_dir = self.root / "data/test"
        self.run_dir.mkdir(parents=True)
        FakeClient.calls = []
        FakeClient.tutor_outputs = {0: "[END]"}
        self.write_config(case_count=1)

    def write_config(self, case_count=1, conditions=None):
        self.config.write_text(json.dumps({
            "source_moments_sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
            "conditions": conditions or self.conditions,
            "tutor_model": "gpt-5.5-2026-04-23", "decision_model": "gpt-6-luna",
            "cases": [{"moment_index": i, "moment_id": self.moments[i]["id"]}
                      for i in range(case_count)],
        }))

    def write_state(self, s):
        (self.run_dir / f"{s['moment_index']}-{s['condition']}.json").write_text(json.dumps(s))

    def read_state(self, condition=None):
        return json.loads((self.run_dir / f"0-{condition or self.conditions[0]}.json").read_text())

    def run_main(self, stage="all", save_override=None):
        argv = ["run_pilot.py", "--source", str(self.source), "--config", str(self.config),
                "--workers", "1", "--stage", stage, "--retry-failed"]
        with patch.object(runner, "ROOT", self.root), patch.object(runner, "OpenAIClient", FakeClient), \
             patch.object(sys, "argv", argv), patch("urllib.request.urlopen", side_effect=AssertionError("No network")), \
             contextlib.redirect_stdout(io.StringIO()):
            if save_override:
                with patch.object(runner, "save", save_override):
                    runner.main()
            else:
                runner.main()
        return json.loads((self.root / "results/test_summary.json").read_text())

    def test_legacy_terminal_checkpoint_never_resumes_student_or_tutor(self):
        for control, reason in [({"ended": True, "problem_change": False}, "end"),
                                ({"ended": False, "problem_change": True}, "problem_change")]:
            with self.subTest(reason=reason):
                self.write_config(conditions=[self.conditions[0]])
                s = state(0, self.conditions[0], status="running")
                s.update(next_speaking_step=1, last_tutor_control=control)
                s.pop("stop_reason")
                s.pop("annotation")
                self.write_state(s)
                self.run_main(stage="rollouts")
                saved = self.read_state()
                self.assertEqual(saved["status"], "rollout_complete")
                self.assertEqual(saved["stop_reason"], reason)
                self.assertEqual(saved["next_speaking_step"], 1)
                self.assertEqual(FakeClient.calls, [])

    def test_immediate_end_is_publisher_default_without_judge_and_stays_in_metrics(self):
        summary = self.run_main()
        for condition in self.conditions:
            s = self.read_state(condition)
            self.assertEqual(s["generated_turns"], [])
            self.assertEqual(s["status"], "scored")
            self.assertEqual(s["next_speaking_step"], 1)
            self.assertEqual(s["annotation"], publisher_no_generated_annotation("toy-0"))
            self.assertEqual(s["annotation_source"], "publisher_minimal_no_generated_turns")
            c = summary["conditions"][condition]
            self.assertEqual(c["proxy_publisher_metrics"]["n_scenarios"], 1)
            self.assertEqual(c["proxy_publisher_metrics"]["rigor_calibrated"]["n_total"], 1)
            self.assertEqual(c["proxy_publisher_metrics"]["rigor_calibrated"]["score"], 0)
            self.assertEqual(c["metric_coverage"]["scored_publisher_no_generated_defaults"], 1)
            self.assertEqual(c["metric_coverage"]["completed_without_tutor_text"], 1)
        self.assertFalse(any(":judge_" in x or x.endswith(":student_proxy") for x in FakeClient.calls))
        self.assertEqual(summary["paired_scored_comparison"]["paired_scored_cases"], 1)
        before = list(FakeClient.calls)
        self.run_main()  # Resume must not pay to re-create or judge the empty termination.
        self.assertEqual(FakeClient.calls, before)

    def test_empty_problem_change_is_also_completed_not_invented_speech(self):
        FakeClient.tutor_outputs = {0: "[NEW_MESSAGE][PROBLEM_CHANGE]"}
        self.run_main()
        self.assertEqual(self.read_state()["generated_turns"], [])
        self.assertEqual(self.read_state()["stop_reason"], "problem_change")
        self.assertEqual(self.read_state()["annotation"]["action_label"], "neither")

    def test_legacy_empty_end_scoring_error_is_repaired_without_generation_or_judge(self):
        self.write_config(conditions=[self.conditions[0]])
        s = state(0, self.conditions[0], status="rollout_complete", generated=[])
        s.update(next_speaking_step=1, stop_reason="end",
                 last_tutor_control={"ended": True, "problem_change": False},
                 scoring_error={"type": "RuntimeError", "message": "No generated excerpt to score"})
        s.pop("annotation")
        self.write_state(s)
        self.run_main()
        saved = self.read_state()
        self.assertEqual(saved["status"], "scored")
        self.assertNotIn("scoring_error", saved)
        self.assertEqual(FakeClient.calls, [])

    def test_later_empty_end_scores_existing_dialogue_normally(self):
        self.write_config(conditions=[self.conditions[0]])
        FakeClient.tutor_outputs = {0: "Explain why.", 2: "[END]"}
        self.run_main()
        s = self.read_state()
        self.assertEqual([t["role"] for t in s["generated_turns"]], ["TUTOR", "STUDENT"])
        self.assertEqual(s["next_speaking_step"], 3)
        self.assertEqual(s["annotation_source"], "proxy_judge")
        self.assertTrue(any(x.endswith(":judge_annotate") for x in FakeClient.calls))
        self.assertFalse(any(":3:" in x or ":4:" in x for x in FakeClient.calls))

    def test_terminal_save_is_atomic_under_interruption(self):
        self.write_config(conditions=[self.conditions[0]])
        original_save = runner.save
        class Crash(BaseException):
            pass
        def crashing_save(path, value):
            original_save(path, value)
            if value.get("last_tutor_control", {}).get("ended"):
                raise Crash()
        with self.assertRaises(Crash):
            self.run_main(save_override=crashing_save)
        saved = self.read_state()
        self.assertEqual(saved["status"], "rollout_complete")
        self.assertEqual(saved["stop_reason"], "end")
        self.assertEqual(saved["next_speaking_step"], 1)
        self.run_main()
        self.assertEqual(self.read_state()["status"], "scored")
        self.assertEqual(sum(x.endswith(":tutor") for x in FakeClient.calls), 1)

    def test_five_call_alternation_and_split_message_numbering_unchanged(self):
        self.write_config(conditions=[self.conditions[1]])
        FakeClient.tutor_outputs = {0: "First.[NEW_MESSAGE]Second.", 2: "Continue.", 4: "Explain."}
        self.run_main(stage="rollouts")
        s = self.read_state(self.conditions[1])
        self.assertEqual(s["next_speaking_step"], 5)
        self.assertEqual([t["role"] for t in s["generated_turns"]],
                         ["TUTOR", "TUTOR", "STUDENT", "TUTOR", "STUDENT", "TUTOR"])
        self.assertEqual([t["turn_number"] for t in s["generated_turns"]], list(range(5, 11)))
        self.assertEqual([r["step"] for r in s["routes"]], [0, 2, 4])
        self.assertEqual(sum(x.endswith(":student_proxy") for x in FakeClient.calls), 2)

    def test_summary_exposes_unpaired_cases_instead_of_calling_them_matched(self):
        self.write_config(case_count=2)
        self.write_state(state(0, self.conditions[0]))
        self.write_state(state(1, self.conditions[1]))
        summary = self.run_main(stage="score")
        for condition in self.conditions:
            coverage = summary["conditions"][condition]["metric_coverage"]
            self.assertEqual(coverage["planned_cases"], 2)
            self.assertEqual(coverage["persisted_cases"], 1)
            self.assertEqual(coverage["missing_case_states"], 1)
        paired = summary["paired_scored_comparison"]
        self.assertEqual(paired["paired_scored_cases"], 0)
        self.assertEqual(paired["planned_cases_not_yet_paired"], 2)
        self.assertTrue(all(x is None for x in paired["condition_metrics"].values()))
        self.assertEqual(FakeClient.calls, [])


class ReportingBoundaryTests(unittest.TestCase):
    def test_only_initial_decision_is_compared_with_initial_category(self):
        ms = [toy()]
        ms[0]["dimension"] = "scaffolding"
        s = state(0, "evaluation_aware_plus_decisions")
        s["routes"] = [
            {"step": 0, "answer": {"type": "choice", "choice": "scaffolding"}},
            {"step": 2, "answer": {"type": "choice", "choice": "rigor"}},
            {"step": 4, "answer": {"type": "choice", "choice": "rigor"}},
        ]
        result = first_decision_agreement([s], ms)
        self.assertEqual(result["eligible_first_decisions"], 1)
        self.assertEqual(result["agreements"], 1)
        self.assertEqual(result["agreement_rate"], 1)
        self.assertEqual(result["later_decisions_not_scored_against_initial_category"], 2)

    def test_retry_records_do_not_inflate_agreement(self):
        ms = [toy()]
        initial = {"step": 0, "answer": {"type": "choice", "choice": "rigor"}}
        s = state(0, "evaluation_aware_plus_decisions")
        s["routes"] = [initial, initial, {"step": 2, "answer": {"type": "choice", "choice": "scaffolding"}}]
        result = first_decision_agreement([s], ms)
        self.assertEqual(result["eligible_first_decisions"], 1)
        self.assertEqual(result["coverage"]["duplicate_initial_records_ignored"], 1)
        s["routes"].append({"step": 0, "answer": {"type": "choice", "choice": "scaffolding"}})
        result = first_decision_agreement([s], ms)
        self.assertEqual(result["eligible_first_decisions"], 0)
        self.assertEqual(result["coverage"]["conflicting_initial_retry_records_excluded"], 1)

    def test_missing_or_fallback_first_decision_is_not_a_wrong_prediction(self):
        s = state(0, "evaluation_aware_plus_decisions")
        s["routes"] = [{"step": 0, "answer": None, "fallback_to_original_prompt": True},
                       {"step": 2, "answer": {"type": "choice", "choice": "rigor"}}]
        result = first_decision_agreement([s], [toy()])
        self.assertEqual(result["eligible_first_decisions"], 0)
        self.assertIsNone(result["agreement_rate"])
        self.assertEqual(result["coverage"]["invalid_or_fallback_initial_decisions"], 1)

    def test_paired_metrics_use_identical_indices_and_include_empty_defaults(self):
        ms = [toy(0), toy(1)]
        baseline = [state(0, "base"), state(1, "base")]
        routed = [state(0, "route", generated=[])]
        routed[0]["annotation"] = publisher_no_generated_annotation("toy-0")
        result = paired_scored_comparison({"base": baseline, "route": routed}, ms, [0, 1], protocol.publisher_metrics)
        self.assertEqual(result["paired_moment_indices"], [0])
        for c in ["base", "route"]:
            self.assertEqual(result["condition_metrics"][c]["n_scenarios"], 1)
            self.assertEqual(result["condition_metrics"][c]["rigor_calibrated"]["n_total"], 1)
        self.assertEqual(result["condition_metrics"]["base"]["rigor_calibrated"]["score"], 1)
        self.assertEqual(result["condition_metrics"]["route"]["rigor_calibrated"]["score"], 0)

    def test_coverage_distinguishes_empty_success_scoring_error_and_failed_rollout(self):
        empty = state(0, "base", generated=[])
        error = state(1, "base", status="rollout_complete")
        error["scoring_error"] = {"type": "APIError"}
        failure = state(2, "base", status="failed", generated=[])
        result = metric_coverage([empty, error, failure], 4)
        self.assertEqual(result["missing_case_states"], 1)
        self.assertEqual(result["completed_without_tutor_text"], 1)
        self.assertEqual(result["scored_publisher_no_generated_defaults"], 1)
        self.assertEqual(result["cases_with_scoring_errors"], 1)
        self.assertEqual(result["failed_rollouts"], 1)
        self.assertEqual(result["scored_cases_in_metric_denominator"], 1)

    def test_publisher_no_generated_default_matches_executed_original_source(self):
        archive = STAGE.parent / "02 - Original Data/002 - TutorMoments-Preview/Publisher Repository.zip"
        data = archive.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "231b617b9589e07c6af0225ce3491fb4eed4720019333d2fb6d400958c577835")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            source = ast.parse(z.read("tutormoments-main/src/tutormoments/scoring.py").decode())
            usage_source = ast.parse(z.read("tutormoments-main/src/tutormoments/usage.py").decode())
        function = next(x for x in source.body if isinstance(x, ast.FunctionDef) and x.name == "score_batch")
        module = ast.Module(body=[
            ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), function
        ], type_ignores=[])
        fake_client = types.ModuleType("audit_publisher.client")
        fake_client.ModelClient = lambda model: object()
        fake_client.run_batch = lambda *a, **k: (_ for _ in ()).throw(AssertionError("No batch calls for empty transcript"))
        fake_config = types.ModuleType("audit_publisher.config")
        fake_config.scorer_spec = lambda: SimpleNamespace(model="offline")
        usage = ast.literal_eval(next(x.value for x in usage_source.body if isinstance(x, ast.Assign)
                                     and any(isinstance(t, ast.Name) and t.id == "EMPTY_USAGE" for t in x.targets)))
        ns = {"__package__": "audit_publisher", "_build_synthetic_conversation": protocol._build_synthetic_conversation,
              "Annotation": lambda **kw: SimpleNamespace(**kw), "EMPTY_USAGE": usage,
              "DEFAULT_ACTION_LABEL": "neither"}
        exec(compile(ast.fix_missing_locations(module), "publisher_scoring.py", "exec"), ns)
        with patch.dict(sys.modules, {"audit_publisher.client": fake_client, "audit_publisher.config": fake_config}):
            result = ns["score_batch"]([(SimpleNamespace(**toy()), SimpleNamespace(generated_turns=[]))])
        self.assertEqual(vars(result["toy-0"]), publisher_no_generated_annotation("toy-0"))


if __name__ == "__main__":
    unittest.main()
