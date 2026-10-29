"""Compare adapter outputs directly with independently executed publisher ZIP functions.
Only hashes/counts are emitted. No transcript text is written by this verifier.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, re, sys, zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tm_router import publisher_protocol as p


def verify(archive, moments_path, config_path):
    z = zipfile.ZipFile(archive)
    base = "tutormoments-main/src/tutormoments/"
    ns = {"json": json, "_re": re, "Any": Any,
          "resource_text": lambda name: z.read(base + name).decode(),
          "_PROMPTS_DIR": "prompts/student"}
    keep = {
        "tutor.py": ["_load_template", "build_tutor_system_prompt"],
        "student.py": ["_STUDENT_PROMPTS_DIR", "_EMPTY_REFERENCE_FALLBACK",
            "_get_shared_generation_instructions", "_render_oracle_template", "build_student_system_prompt"],
        "conversation.py": ["_format_transcript_prefix", "_build_role_prompt"],
        "scoring.py": ["VALID_ANNOTATION_TYPES", "_SCORER_PROMPTS_DIR", "_SITUATION_LABEL_AGG_TO_SUGGESTION",
            "_SUGGESTION_UNKNOWN", "_format_excerpt", "_suggestion_text", "_load_annotate_prompt",
            "_build_annotate_entries", "JUNK_TEXTS", "_DECOMPOSE_PROMPTS_DIR", "_load_decompose_prompt",
            "_build_decompose_entries", "_STRUCTURE_PROMPTS_DIR", "_load_structure_prompt",
            "_format_facet_list", "_build_structure_entries"],
    }
    # Replace only provider batch-entry plumbing, leaving publisher prompt logic intact.
    ns["build_batch_entry"] = lambda key, prompt, **kw: {"key": key, "prompt": prompt, **kw}
    for filename, names in keep.items():
        original = ast.parse(z.read(base + filename).decode())
        selected = []
        for node in original.body:
            node_name = node.name if isinstance(node, ast.FunctionDef) else None
            if isinstance(node, ast.Assign):
                node_name = next((t.id for t in node.targets if isinstance(t, ast.Name)), None)
            if node_name in names:
                if isinstance(node, ast.FunctionDef):
                    node.body = [b for b in node.body if not isinstance(b, (ast.Import, ast.ImportFrom))]
                selected.append(node)
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)] + selected, type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), filename, "exec"), ns)
    manifest = json.loads((Path(p.__file__).resolve().parents[2] / "docs/publisher_protocol_manifest.json").read_text())
    for entry in manifest["prompts"]:
        bundled = (Path(p.__file__).resolve().parents[2] / entry["path"]).read_bytes()
        assert bundled == z.read(entry["archive_member"])
        assert hashlib.sha256(bundled).hexdigest() == entry["raw_sha256"]
    moments = [json.loads(s) for s in Path(moments_path).read_text().splitlines()]
    config = json.loads(Path(config_path).read_text())
    counts = {"tutor_prompt_comparisons": 0, "student_prompt_comparisons": 0,
              "annotate_prompt_comparisons": 0, "decompose_prompt_comparisons": 0,
              "structure_prompt_comparisons": 0, "router_leakage_canary_checks": 0}
    for case in config["cases"]:
        m = moments[case["moment_index"]]
        assert m["id"] == case["moment_id"]
        g = []
        for round_number in range(3):
            extra = "".join(f"\nTurn {t['turn_number']}. {t['role']}: {t['text']}" for t in g)
            prefix = ns["_format_transcript_prefix"](m["context"])
            for mode in ("plain", "scaffolding_rigor"):
                h, t = ns["_build_role_prompt"]("TUTOR", prefix, extra, m["student"]["context"], tutor_mode=mode)
                baseline = p.tutor_messages(m, mode, g)
                assert baseline == [{"role": "user", "content": h + t}]
                assert p.tutor_messages(m, mode, g, "ONE_REPLY_ONLY")[0] == baseline[0]
                counts["tutor_prompt_comparisons"] += 1
            h, t = ns["_build_role_prompt"]("STUDENT", prefix, extra, m["student"]["context"],
                reference_transcript=m["student"]["reference"], persona=m["student"]["trait"]["persona"])
            assert p.student_messages(m, g) == [{"role": "user", "content": h + t}]
            counts["student_prompt_comparisons"] += 1
            polluted = dict(m, dimension="FORBIDDEN_DIMENSION", rubric={"gold": "FORBIDDEN_GOLD"},
                            student={"reference": "FORBIDDEN_FUTURE", "trait": {"persona": "FORBIDDEN_PERSONA"}, "context": "FORBIDDEN_METADATA"})
            assert p.router_messages(m, g) == p.router_messages(polluted, g)
            assert all("FORBIDDEN_" not in msg["content"] for msg in p.router_messages(polluted, g))
            counts["router_leakage_canary_checks"] += 1
            g = p.append_generated_turns(m, g, "TUTOR", ["Explain the next step.", "Take your time."])
            if round_number < 2:
                g = p.append_generated_turns(m, g, "STUDENT", ["I think I see."])
        # Reuse publisher entry builder directly for context_window=0 scoring parity.
        turns = [{"turn_number": x["turn_number"], "role": x["role"].upper(), "text": x["text"]} for x in m["context"]] + g
        convs = {m["id"]: {"turns": turns}}
        dets = {m["id"]: {"detections": [{"annotation_type": "scaffolding", "turn_start": g[0]["turn_number"],
                 "turn_end": g[-1]["turn_number"], "situation_label_agg": m["dimension"]}]}}
        expected = ns["_build_annotate_entries"](convs, dets)[0]["prompt"]
        assert p.scorer_annotate_prompt(m, g) == expected
        counts["annotate_prompt_comparisons"] += 1
        ann = {"annotation_type": "scaffolding", "situation": "A current difficulty.", "action": "The tutor asks a guiding question.", "result": "Some progress."}
        for kind in ("action", "overscaffold"):
            entries, _ = ns["_build_decompose_entries"]({"case": {"annotations": [ann]}}, kind)
            assert p.scorer_decompose_prompt(ann, kind) == entries[0]["prompt"]
            counts["decompose_prompt_comparisons"] += 1
        facets = ["The tutor asks a guiding question."]
        entries, _ = ns["_build_structure_entries"]({"case": {"annotations": [{"action_decomposed": facets}]}})
        assert p.scorer_structure_prompt(facets) == entries[0]["prompt"]
        counts["structure_prompt_comparisons"] += 1
    return {"status": "passed", "archive_sha256": hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
            "moment_file_sha256": hashlib.sha256(Path(moments_path).read_bytes()).hexdigest(),
            "config_sha256": hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),
            "case_count": len(config["cases"]), "unchanged_prompt_byte_checks": len(manifest["prompts"]),
            **counts, "scope": "Offline parity checks only; no API generation or human validation."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--moments", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = verify(args.archive, args.moments, args.config)
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
