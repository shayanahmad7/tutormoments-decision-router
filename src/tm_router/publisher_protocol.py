"""Publisher prompt/protocol adapter, modified from AllenAI TutorMoments (Apache-2.0).

Copyright 2026 The Allen Institute for Artificial Intelligence.
Unchanged extracted functions below are followed by new dictionary/API wrappers.
The model substitution in a caller is a deviation: these builders do not make a
GPT student or judge equivalent to the publisher's Claude auxiliary models.
See docs/publisher_protocol_manifest.json and third_party/tutormoments/NOTICE.
"""
from __future__ import annotations
import json
import re as _re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

TUTOR_MODEL = "gpt-5.5-2026-04-23"
TUTOR_KWARGS = {"reasoning_effort": "high", "max_completion_tokens": 128000}
STUDENT_MODEL = "claude-opus-4-6"
SCORER_MODEL = "claude-opus-4-6"
STUDENT_THINKING = {"type": "disabled"}
SCORER_THINKING = {"type": "adaptive"}
MAX_SPEAKING_TURNS = 5  # LLM calls: tutor, student, tutor, student, tutor
_PROMPTS_DIR = "prompts/student"

def resource_text(path: str) -> str:
    if not path.startswith("prompts/"):
        raise ValueError("Only publisher prompt resources are bundled")
    return (Path(__file__).parent / "publisher_prompts" / path[8:]).read_text()


# Extracted unchanged: src/tutormoments/tutor.py:23
def _load_template(filename: str) -> str:
    """Load a prompt template from the tutor prompts directory."""
    return resource_text(f"prompts/tutor/{filename}").strip()


# Extracted unchanged: src/tutormoments/tutor.py:28
def build_tutor_system_prompt(
    mode: str | None,
    *,
    student_context: str,
    reference_transcript: str = "",
) -> str:
    """Assemble the TUTOR system prompt.

    Args:
        mode: None (or "" or "default") for the plain tutor; "plain" for
            the basic tutor; "scaffolding_rigor" for the expert tutor;
            "oracle" for the reference-aware tutor that mimics the real
            human tutor's post-cut continuation.
        student_context: substituted for `{student_context}`.
        reference_transcript: required when mode == "oracle"; used for
            `{reference_transcript}` substitution.

    Returns:
        The fully-substituted system prompt string.

    Raises:
        ValueError: if mode == "oracle" but reference_transcript is not provided.
    """
    # Default mode: load plain.txt
    if mode in (None, "", "default"):
        template = _load_template("plain.txt")
    else:
        template = _load_template(f"{mode}.txt")

    # Substitute student_context
    out = template.replace("{student_context}", student_context or "")

    # Oracle-specific: substitute reference_transcript
    if mode == "oracle":
        if not reference_transcript:
            raise ValueError("mode='oracle' requires a non-empty reference_transcript")
        out = out.replace("{reference_transcript}", reference_transcript)

    return out


# Extracted unchanged: src/tutormoments/student.py:25
_STUDENT_PROMPTS_DIR = _PROMPTS_DIR


# Extracted unchanged: src/tutormoments/student.py:27
_EMPTY_REFERENCE_FALLBACK = (
    "(The real conversation ends at the cut point — the student made no "
    "further turns. Acknowledge any final tutor message briefly, then end "
    "the session.)"
)


# Extracted unchanged: src/tutormoments/student.py:34
def _get_shared_generation_instructions() -> str:
    """Return the shared generation instructions text."""
    return (
        "You may generate multiple student turns in a row as needed. "
        "Do *not* generate any turns as the tutor. "
        "You should only generate turns that involve student utterances or actions. "
        "Remember to wait for the tutor to respond before generating your next turns."
    )


# Extracted unchanged: src/tutormoments/student.py:44
def _render_oracle_template() -> str:
    """Load prompts/student/oracle.txt and substitute {shared_generation_instructions}."""
    template = resource_text(f"{_STUDENT_PROMPTS_DIR}/oracle.txt").rstrip("\n")
    shared = _get_shared_generation_instructions()
    return template.replace("{shared_generation_instructions}", shared)


# Extracted unchanged: src/tutormoments/student.py:51
def build_student_system_prompt(
    *,
    student_context: str,
    reference_transcript: str | None,
    persona: str,
) -> str:
    """Assemble the STUDENT system prompt for oracle mode.

    Loads prompts/student/oracle.txt, substitutes {shared_generation_instructions},
    then fills the three bracket placeholders:
      [[REFERENCE_TRANSCRIPT_HERE]]           <- reference_transcript (fallback if empty)
      [[PERSONA_DESCRIPTION_HERE]]            <- persona
      [[NEXT_CONVERSATION_INFORMATION_HERE]]  <- student_context

    Args:
        student_context: Text for the student's current context / conversation info.
        reference_transcript: Full post-cut real transcript the oracle student imitates.
            If empty or None, the empty-reference fallback message is used instead.
        persona: The moment's frozen student.trait.persona text.

    Returns:
        Fully-substituted system prompt string (ASCII-safe, no unreplaced placeholders).
    """
    out = _render_oracle_template()

    # Substitute shared + bracket placeholders.
    out = out.replace("[[NEXT_CONVERSATION_INFORMATION_HERE]]", student_context or "")
    out = out.replace("[[PERSONA_DESCRIPTION_HERE]]", persona or "")

    # Empty reference fallback: same logic as students.py lines 155-160.
    ref = reference_transcript or _EMPTY_REFERENCE_FALLBACK
    out = out.replace("[[REFERENCE_TRANSCRIPT_HERE]]", ref)

    return out


# Extracted unchanged: src/tutormoments/conversation.py:22
NEXT_DELIMITER = "[NEXT]"


# Extracted unchanged: src/tutormoments/conversation.py:23
NEW_MESSAGE_DELIMITER = "[NEW_MESSAGE]"


# Extracted unchanged: src/tutormoments/conversation.py:24
END_TOKEN = "[END]"


# Extracted unchanged: src/tutormoments/conversation.py:25
PROBLEM_CHANGE_TOKEN = "[PROBLEM_CHANGE]"


# Extracted unchanged: src/tutormoments/conversation.py:26
NEXT_PROBLEM_TOKEN = "[NEXT_PROBLEM]"  # legacy alias (v5 and earlier prompts)


# Extracted unchanged: src/tutormoments/conversation.py:76
def _parse_tutor_tokens(text: str) -> tuple[str, bool, bool]:
    """Strip tutor control tokens and report which were present.

    Returns (cleaned_text, ended, problem_change).
    END takes precedence: if both tokens appear, ended=True, problem_change=False.
    [NEXT_PROBLEM] is the legacy alias for [PROBLEM_CHANGE].
    """
    has_end = END_TOKEN in text
    has_change = (PROBLEM_CHANGE_TOKEN in text) or (NEXT_PROBLEM_TOKEN in text)
    cleaned = (
        text.replace(END_TOKEN, "")
        .replace(PROBLEM_CHANGE_TOKEN, "")
        .replace(NEXT_PROBLEM_TOKEN, "")
        .rstrip()
    )
    if has_end:
        return cleaned, True, False
    return cleaned, False, has_change


# Extracted unchanged: src/tutormoments/conversation.py:96
def _split_messages(text: str) -> list[str]:
    """Split LLM output into multiple messages on either delimiter.

    Recognizes [NEXT] (v1-v4) and [NEW_MESSAGE] (v5+). Either token splits
    the text into separate chat messages.
    """
    normalized = text.replace(NEW_MESSAGE_DELIMITER, NEXT_DELIMITER)
    parts = normalized.split(NEXT_DELIMITER)
    messages = [p.strip() for p in parts]
    return [m for m in messages if m]


# Extracted unchanged: src/tutormoments/conversation.py:166
def _format_transcript_prefix(context: list[dict]) -> str:
    """Format scenario.context turns into 'Turn N. ROLE: text' string.

    Roles are uppercased (tutor -> TUTOR, student -> STUDENT).
    Turn numbers come from the real turn_number stored in each context entry,
    preserving the original (non-sequential) numbering from the source transcript.
    """
    lines = []
    for turn in context:
        n = turn["turn_number"]
        role = turn["role"].upper()
        text = turn["text"]
        lines.append(f"Turn {n}. {role}: {text}")
    return "\n".join(lines)


# Extracted unchanged: src/tutormoments/conversation.py:187
def _build_role_prompt(
    role: str,
    transcript_prefix: str,
    extra: str,
    student_context: str,
    *,
    tutor_mode: str | None = None,
    reference_transcript: str | None = None,
    persona: str = "",
) -> tuple[str, str]:
    """Build (cacheable_head, tail) for either tutor or student.

    head = system_prompt + "Here is the conversation so far:\\n\\n" + transcript_prefix
    tail = extra + "\\n\\n" + role_instruction

    The head is byte-stable across rounds (system + static cut prefix), so the
    prompt cache hits on round 2+. Generated turns flow through `extra` (tail).

    Prompts are built through the tutormoments adapter signatures
    (build_tutor_system_prompt / build_student_system_prompt).
    """
    if role == "TUTOR":
        system_prompt = build_tutor_system_prompt(
            tutor_mode,
            student_context=student_context,
            reference_transcript=reference_transcript or "",
        )
        role_instruction = (
            "Respond as the TUTOR. Give only your response, no labels or prefixes."
        )
    else:
        system_prompt = build_student_system_prompt(
            student_context=student_context,
            reference_transcript=reference_transcript,
            persona=persona,
        )
        role_instruction = (
            "Respond as the STUDENT. Give only your response, no labels or prefixes."
        )

    head = f"{system_prompt}\n\nHere is the conversation so far:\n\n{transcript_prefix}"
    tail = f"{extra}\n\n{role_instruction}"
    return head, tail


# Extracted unchanged: src/tutormoments/scoring.py:26
_SCORER_PROMPTS_DIR = "prompts/scorer"


# Extracted unchanged: src/tutormoments/scoring.py:107
_SITUATION_LABEL_AGG_TO_SUGGESTION = {
    "scaffolding": "A team of teachers believe that this moment is appropriate for scaffolding.",
    "rigor": "A team of teachers believe that this moment is appropriate for pushing for rigor.",
    "mixed": "A team of teachers believe that this moment is appropriate for either rigor or scaffolding.",
    "both": "A team of teachers believe that this moment is appropriate for either rigor or scaffolding.",
    "neither": "A team of teachers believe that this moment is not appropriate for either rigor or scaffolding.",
}


# Extracted unchanged: src/tutormoments/scoring.py:114
_SUGGESTION_UNKNOWN = "It's unclear to a team of teachers whether this moment is appropriate for rigor or scaffolding."


# Extracted unchanged: src/tutormoments/scoring.py:38
def _format_excerpt(
    conversation: dict,
    turn_start: int,
    turn_end: int,
    context_before: int = 0,
    context_after: int = 0,
) -> str:
    """Extract a transcript excerpt around a detected moment, with context.

    Outputs the detected range with >>> markers, surrounded by context turns.
    The benchmark always calls with context_before=0, context_after=0.
    """
    turns = conversation.get("turns", [])
    if not turns:
        return ""

    # Find actual min/max turn numbers
    all_turn_nums = [t["turn_number"] for t in turns]
    min_turn = min(all_turn_nums)
    max_turn = max(all_turn_nums)

    # Calculate excerpt boundaries
    excerpt_start = max(min_turn, turn_start - context_before)
    excerpt_end = min(max_turn, turn_end + context_after)

    lines = []

    # Header if not starting from the beginning
    if excerpt_start > min_turn:
        lines.append(f"[... turns 1-{excerpt_start - 1} omitted ...]")
        lines.append("")

    marker_start_emitted = False
    for turn in turns:
        n = turn["turn_number"]
        if n < excerpt_start or n > excerpt_end:
            continue

        is_enrichment = turn.get("is_enrichment", False)

        # Emit start marker before the first dialogue turn at turn_start
        if n == turn_start and not is_enrichment and not marker_start_emitted:
            lines.append(f">>> DETECTED MOMENT START (Turn {turn_start}) <<<")
            marker_start_emitted = True

        role = turn["role"]
        text = turn["text"]
        if is_enrichment:
            lines.append(text)
        else:
            marker = " <<<" if turn_start <= n <= turn_end else ""
            lines.append(f"Turn {n}. {role}: {text}{marker}")

        # Emit end marker after the last dialogue turn at turn_end
        if n == turn_end and not is_enrichment:
            lines.append(f">>> DETECTED MOMENT END (Turn {turn_end}) <<<")

    # Footer if not ending at last turn
    if excerpt_end < max_turn:
        lines.append("")
        lines.append(f"[... turns {excerpt_end + 1}-{max_turn} omitted ...]")

    return "\n".join(lines)


# Extracted unchanged: src/tutormoments/scoring.py:117
def _suggestion_text(situation_label_agg: str | None) -> str:
    """Map situation_label_agg to the suggestion sentence injected into the prompt."""
    return _SITUATION_LABEL_AGG_TO_SUGGESTION.get(
        situation_label_agg or "", _SUGGESTION_UNKNOWN
    )


# Extracted unchanged: src/tutormoments/scoring.py:349
def _build_synthetic_conversation(
    scenario: Any,
    transcript: Any,
) -> tuple[dict, dict]:
    """Build a full conversation dict and detections from a scenario + transcript.

    Ports annotator_bridge.build_synthetic_conversation (~lines 23-56) and
    annotator_bridge.build_synthetic_detections (~lines 59-112), plus the
    conv_id -> scenario_id remap from prepare_bulk_entries (~lines 159-166).

    Args:
        scenario: tutormoments.moments.Moment object.
        transcript: tutormoments.conversation.Transcript object.

    Returns:
        (conversation_dict, detections_by_id) where both are keyed by
        scenario.id (the remapped scenario_id, not the raw conv_id).
    """
    # ---- Build turns: context prefix + generated turns ----
    turns = []

    # Prefix turns from scenario.context: [{turn_number, role, text}]
    # Role stored lowercase in new schema; annotator pipeline expects uppercase.
    for ctx_turn in scenario.context:
        turns.append(
            {
                "turn_number": ctx_turn["turn_number"],
                "role": ctx_turn["role"].upper(),
                "text": ctx_turn["text"],
                "type": "DIALOGUE",
                "timestamp": "",
            }
        )

    # Generated turns from transcript.generated_turns: already {turn_number, role, text}
    for gen_turn in transcript.generated_turns:
        turns.append(
            {
                "turn_number": gen_turn["turn_number"],
                "role": gen_turn["role"],
                "text": gen_turn["text"],
                "type": "DIALOGUE",
                "timestamp": "",
            }
        )

    # ---- Build conversation dict (remapped: conversation_id = scenario.id) ----
    # Original annotator_bridge used scenario.conv_id as conversation_id, then
    # prepare_bulk_entries remapped it to scenario.scenario_id. In the new schema
    # scenario.id is the scenario_id and scenario.provenance["conv_id"] is the
    # raw conv_id. We produce the post-remap form directly.
    conv = {
        "conversation_id": scenario.id,
        "turns": turns,
        "context": scenario.student.get("context", ""),
        "num_turns": len(turns),
    }
    conversation_dict = {scenario.id: conv}

    # ---- Build detections ----
    if not transcript.generated_turns:
        return conversation_dict, {}

    first_gen = transcript.generated_turns[0]["turn_number"]
    last_gen = transcript.generated_turns[-1]["turn_number"]

    # Benchmark always annotates the scaffolding lens for detected moments.
    ann_type = "scaffolding"

    cut_turn = scenario.provenance.get("cut_turn", "?")
    hint = scenario.rubric.get("hint", "")
    description = f"AI tutor continuation from cut at turn {cut_turn}: {hint}"

    # situation_label_agg from scenario.dimension (= rubric["gold"])
    situation_label_agg = scenario.dimension

    detections = [
        {
            "turn_start": first_gen,
            "turn_end": last_gen,
            "annotation_type": ann_type,
            "situation": description,
            "situation_label_agg": situation_label_agg,
        }
    ]

    detections_by_id = {
        scenario.id: {
            "detections": detections,
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        }
    }

    return conversation_dict, detections_by_id


# Extracted unchanged: src/tutormoments/scoring.py:458
JUNK_TEXTS = {"", "n/a", "test", "sdf", "this is a test annotation"}


# Extracted unchanged: src/tutormoments/scoring.py:639
_YES_NO_TO_ACTION_LABEL = {
    ("yes", "yes"): "both",
    ("yes", "no"): "scaffolding",
    ("no", "yes"): "rigor",
    ("no", "no"): "neither",
}


# Extracted unchanged: src/tutormoments/scoring.py:663
def _format_facet_list(facets: list) -> str:
    """Format facets as a bullet list, one per line, for {action_list}/{student_list}."""
    return "\n".join(f"- {facet}" for facet in facets)


# Extracted unchanged: src/tutormoments/scoring.py:468
def _coerce_facets(parsed: object) -> list[str] | None:
    """Coerce a parsed JSON value into a list of facet strings.

    Returns the facet list, or None if the value is not a recognizable facet
    container (signals a parse failure to the caller).

    Handles two shapes:
      - a bare array (Gemini/Anthropic honor the prompt's requested format), and
      - an object, because OpenAI's response_format={"type": "json_object"}
        cannot emit a top-level array. The model wraps the facets either under a
        key whose value is the list (e.g. {"facets": [...]}) or, when it has no
        list to hand, crams them across the object's keys and values
        (e.g. {"facet a": "facet b", ...}).
    """
    if isinstance(parsed, list):
        return [str(s) for s in parsed]

    if isinstance(parsed, dict):
        # Prefer the wrapper shape: a list-valued key holds the facets (e.g.
        # {"facets": [...]} or {"spans": [...]}). An empty list value
        # ({"spans": []}) is a real empty result -- return [], do NOT fall through
        # to the cram path, or the key and "[]" come back as two bogus facets.
        list_values = [v for v in parsed.values() if isinstance(v, list)]
        if list_values:
            return [str(s) for v in list_values for s in v]
        # No list value anywhere: facets were crammed across keys and values.
        # Interleave to preserve each pair's order.
        facets: list[str] = []
        for k, v in parsed.items():
            facets.append(str(k))
            facets.append(str(v))
        return facets

    return None


# Extracted unchanged: src/tutormoments/scoring.py:668
def _parse_action_label(text: str) -> tuple:
    """Parse the action label from model output text.

    classify_action.md asks for JSON {"scaffolding": "yes"|"no", "rigor":
    "yes"|"no"} -- two independent per-dimension judgments. Tries json.loads
    first (a list-wrapped response like [{...}] is unwrapped), then falls back
    to regex field extraction for responses with extra surrounding text.
    The resulting (scaffolding, rigor) tuple is mapped to a single action_label
    via _YES_NO_TO_ACTION_LABEL.

    Returns (label, had_error). Falls back to "unclear" if either dimension
    is missing or isn't "yes"/"no".
    """

    def _coerce(val) -> str | None:
        v = str(val).strip().lower()
        return v if v in ("yes", "no") else None

    scaffolding = rigor = None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            parsed = parsed[0] if parsed else {}
        if isinstance(parsed, dict):
            scaffolding = _coerce(parsed.get("scaffolding"))
            rigor = _coerce(parsed.get("rigor"))
    except (json.JSONDecodeError, AttributeError, TypeError, IndexError):
        pass

    if scaffolding is None or rigor is None:
        m_scaf = _re.search(
            r'["\']?scaffolding["\']?\s*:\s*["\']?(yes|no)["\']?', text, _re.IGNORECASE
        )
        m_rigor = _re.search(
            r'["\']?rigor["\']?\s*:\s*["\']?(yes|no)["\']?', text, _re.IGNORECASE
        )
        if scaffolding is None and m_scaf:
            scaffolding = m_scaf.group(1).lower()
        if rigor is None and m_rigor:
            rigor = m_rigor.group(1).lower()

    if scaffolding is not None and rigor is not None:
        return _YES_NO_TO_ACTION_LABEL[(scaffolding, rigor)], False

    return "unclear", True


# Extracted unchanged: src/tutormoments/report.py:30
_ACTION_LABEL_TO_DIMENSIONS = {
    "both": ("yes", "yes"),
    "scaffolding": ("yes", "no"),
    "rigor": ("no", "yes"),
    "neither": ("no", "no"),
}


# Extracted unchanged: src/tutormoments/report.py:38
def _to_dims(label):
    return _ACTION_LABEL_TO_DIMENSIONS.get(label)


# Extracted unchanged: src/tutormoments/report.py:47
def aggregate(scenarios: list, annotations: list) -> dict:
    """Compute the paper's three metrics from scored annotations.

    outcome_pos_rate and the did-rates are not computed (both dropped
    from the paper).

    Args:
        scenarios: list of tutormoments.moments.Moment objects (canonical order).
        annotations: list of tutormoments.scoring.Annotation objects, parallel to scenarios.

    Returns:
        {
          "n_scenarios": int,
          "overscaffold":    {"n_yes": int, "n_total": int, "rate": float|None, "available": bool},
          "scaffold_calibrated": {"n_clean_yes": int, "n_overscaffold": int, "n_total": int, "score": float|None},
          "rigor_calibrated":    {"n_clean_yes": int, "n_total": int, "score": float|None},
        }

    scaffold_calibrated.score = scaffolding-gold scenarios where the LM took the
                            right action (action_label in {scaffolding, both})
                            AND emitted no over-scaffold facets, divided by all
                            scaffolding-gold scenarios. (Appropriate Scaffolding)
    rigor_calibrated.score  = analogous for rigor-gold scenarios. (Appropriate Rigor)
    overscaffold.rate       = scenarios with non-empty overscaffold_decomposed
                            divided by total scenarios. Reported to readers as
                            Avoids Over-Scaffolding = 1 - rate (see leaderboard).
                            available=False if the overscaffold_decomposed field
                            was never present (not applicable for the new
                            Annotation dataclass -- field always exists, so
                            available is always True when any scenario is
                            processed).

    Scenarios where gold is mixed/unknown/neither/unclear are excluded from
    BOTH calibrated denominators -- they don't carry a clean direction.
    """
    scaf_total = 0
    rig_total = 0
    over_yes = 0
    any_overscaffold_field = False
    n_total = 0

    # Calibrated scoring:
    #   scaffold_calibrated = n_scaffolded_cleanly / n_scaffold_moments
    #   rigor_calibrated    = n_rigor_pushed_cleanly / n_rigor_moments
    # "cleanly" = right action direction AND no over-scaffold facets.
    # Both axes are symmetric: count clean moments / total moments. Range [0, 1].
    #
    # NOTE: an earlier version subtracted n_over_scaffolded from the scaffold
    # numerator. That double-penalized -- a moment that over-scaffolds is
    # already excluded from n_clean_yes (clean requires no over-scaffold), so
    # subtracting it again counted it twice. The subtraction was removed;
    # scaf_over_yes is kept as a reported component only (not in the score).
    scaf_clean_yes = 0  # scaffold-gold + action right + no over-scaffold
    scaf_over_yes = 0  # scaffold-gold + over-scaffold emitted (reported, not scored)
    rig_clean_yes = 0  # rigor-gold + action right + no over-scaffold

    for scenario, annotation in zip(scenarios, annotations):
        n_total += 1

        # scenario.dimension is set from situation_label_agg at build time.
        gt_label = scenario.dimension

        pred_label = annotation.action_label
        # Treat empty/None as absent.
        if not isinstance(pred_label, str) or not pred_label:
            pred_label = None
        pred_dims = _to_dims(pred_label)

        # annotation.overscaffold_decomposed is always present as a list field;
        # non-empty means over-scaffold detected.
        has_over = bool(annotation.overscaffold_decomposed)

        if gt_label == "scaffolding":
            scaf_total += 1
            action_right = pred_dims is not None and pred_dims[0] == "yes"
            if action_right and not has_over:
                scaf_clean_yes += 1
            if has_over:
                scaf_over_yes += 1
        elif gt_label == "rigor":
            rig_total += 1
            action_right = pred_dims is not None and pred_dims[1] == "yes"
            if action_right and not has_over:
                rig_clean_yes += 1
        # mixed / both / neither / unknown / unclear -> excluded from both
        # calibrated denominators. Still counts toward overscaffold.

        # The Annotation dataclass always has the overscaffold_decomposed field,
        # so any_overscaffold_field becomes True as soon as we process any
        # scenario (available=True whenever n_total > 0).
        any_overscaffold_field = True  # field always present on Annotation dataclass
        if has_over:
            over_yes += 1

    def _rate(yes, total):
        return (yes / total) if total else None

    return {
        "n_scenarios": n_total,
        "overscaffold": {
            "n_yes": over_yes,
            "n_total": n_total,
            "rate": _rate(over_yes, n_total),
            "available": any_overscaffold_field,
        },
        # Calibrated scores -- subsume did-rate + over-scaffold into one
        # number per axis. Components exposed so other formulas can be
        # recomputed from the same data without re-running annotation.
        "scaffold_calibrated": {
            "n_clean_yes": scaf_clean_yes,
            "n_overscaffold": scaf_over_yes,
            "n_total": scaf_total,
            "score": _rate(scaf_clean_yes, scaf_total),
        },
        "rigor_calibrated": {
            "n_clean_yes": rig_clean_yes,
            "n_total": rig_total,
            "score": _rate(rig_clean_yes, rig_total),
        },
    }



# New adapter wrappers (2026-10-29); publisher functions above remain unchanged.
def _moment(moment: dict) -> SimpleNamespace:
    return SimpleNamespace(**moment)


def _extra(generated_turns) -> str:
    return "".join(
        f"\nTurn {t['turn_number']}. {t['role'].upper()}: {t['text']}"
        for t in generated_turns
    )


def _messages(moment, role, generated_turns=(), mode="plain"):
    student = moment["student"]
    persona = (student.get("trait") or {}).get("persona", "")
    if role == "STUDENT" and not persona:
        raise RuntimeError("Frozen student.trait.persona is required; never regenerate it")
    head, tail = _build_role_prompt(
        role, _format_transcript_prefix(moment["context"]), _extra(generated_turns),
        student.get("context", ""), tutor_mode=mode,
        reference_transcript=student.get("reference", ""), persona=persona,
    )
    # GPT-5.5 publisher wire: ONE user message, head concatenated with tail.
    return [{"role": "user", "content": head + tail}]


def tutor_messages(moment, mode="plain", generated_turns=(), route_instruction=None):
    aliases = {"original_plain": "plain", "original_evaluation_aware": "scaffolding_rigor",
               "aware": "scaffolding_rigor", "evaluation_aware_plus_decisions": "scaffolding_rigor"}
    mode = aliases.get(mode, mode)
    if mode not in (None, "", "default", "plain", "scaffolding_rigor"):
        raise ValueError("Only the original plain/evaluation-aware tutor is allowed")
    messages = _messages(moment, "TUTOR", generated_turns, mode)
    if route_instruction is not None:
        if not isinstance(route_instruction, str) or not route_instruction.strip():
            raise ValueError("route_instruction must be a nonempty string")
        # Sole experimental addition. Never append this message to dialogue.
        messages.append({"role": "developer", "content": route_instruction})
    return messages


def student_messages(moment, generated_turns=()):
    return _messages(moment, "STUDENT", generated_turns)


def router_messages(moment, generated_turns=()):
    # Deliberate allowlist: no dimension/rubric/rationale/reference/persona/ID.
    dialogue = _format_transcript_prefix(moment["context"]) + _extra(generated_turns)
    return [{"role": "user", "content": dialogue}]


def route_instruction(route):
    if route == "scaffolding":
        return ("For your next reply only, provide targeted scaffolding for the learner's "
                "current mathematical difficulty. Preserve the learner's meaningful "
                "participation and use only the available dialogue evidence.")
    if route == "rigor":
        return ("For your next reply only, push for appropriate rigor by inviting the "
                "learner's reasoning, justification, connections, or independent work. "
                "Use only the available dialogue evidence and avoid unnecessary takeover.")
    raise ValueError("Route must be scaffolding or rigor")


parse_tutor_output = _parse_tutor_tokens
split_messages = _split_messages


def append_generated_turns(moment, generated_turns, role, messages):
    """Append already-split messages; one LLM call may produce several turns."""
    if isinstance(messages, str):
        raise TypeError("Pass split_messages(text), not a string")
    if role.upper() not in ("TUTOR", "STUDENT"):
        raise ValueError(role)
    result = [dict(t) for t in generated_turns]
    next_number = result[-1]["turn_number"] + 1 if result else moment["provenance"]["cut_turn"] + 1
    for msg in messages:
        result.append({"turn_number": next_number, "role": role.upper(), "text": msg})
        next_number += 1
    return result


def scorer_annotate_prompt(moment, generated_turns):
    """Official scorer sees generated range ONLY, context_window=0, plus gold hint."""
    convs, dets = _build_synthetic_conversation(
        _moment(moment), SimpleNamespace(generated_turns=list(generated_turns)))
    if not dets:
        return None
    det = dets[moment["id"]]["detections"][0]
    excerpt = _format_excerpt(convs[moment["id"]], det["turn_start"], det["turn_end"], 0, 0)
    prompt = resource_text("prompts/scorer/annotate/scaffolding.md")
    return (prompt.replace("{annotator_style}", "")
            .replace("{suggestion}", _suggestion_text(det.get("situation_label_agg")))
            .replace("{excerpt}", excerpt)
            .replace("{turn_start}", str(det["turn_start"]))
            .replace("{turn_end}", str(det["turn_end"])))


def parse_annotation(text):
    """Publisher JSON parse/list-unwrapping; raise on malformed response."""
    value = json.loads(text)
    if isinstance(value, list):
        value = value[0] if value else {}
    if not isinstance(value, dict):
        raise ValueError("Annotation must be an object or a list containing one")
    return {k: value.get(k, "") for k in ("situation", "action", "result")}


def scorer_decompose_prompt(annotation, kind="action"):
    action, result = annotation.get("action", ""), annotation.get("result", "")
    if kind == "action":
        if action.strip().lower() in JUNK_TEXTS:
            return None
        return resource_text("prompts/scorer/decompose/decompose_action.md").replace("{action}", action)
    if kind == "overscaffold":
        if action.strip().lower() in JUNK_TEXTS and result.strip().lower() in JUNK_TEXTS:
            return None
        return (resource_text("prompts/scorer/decompose/decompose_overscaffold.md")
                .replace("{situation}", annotation.get("situation", ""))
                .replace("{action}", action).replace("{result}", result))
    raise ValueError(kind)


def parse_facets(text):
    """Active scorer strict JSON behavior; no ground-truth regex fallback."""
    try:
        return _coerce_facets(json.loads(text)) or []
    except json.JSONDecodeError:
        return []  # original score_batch._assign_decomposed fallback


def scorer_structure_prompt(action_facets):
    if not action_facets:
        return None  # publisher defaults to action_label=neither
    return resource_text("prompts/scorer/structure/classify_action.md").replace(
        "{action_list}", _format_facet_list(action_facets))


def parse_action_label(text):
    return _parse_action_label(text)[0]


def publisher_metrics(moment_annotation_pairs):
    """Publisher formulas; model provenance must be reported by the caller."""
    pairs = list(moment_annotation_pairs)
    scenarios = [_moment(m) for m, a in pairs]
    annotations = [SimpleNamespace(**a) for m, a in pairs]
    result = aggregate(scenarios, annotations)
    over = result["overscaffold"]["rate"]
    result["avoids_overscaffold"] = None if over is None else 1 - over
    return result
