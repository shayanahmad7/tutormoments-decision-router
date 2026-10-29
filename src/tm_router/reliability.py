"""Reliability and reporting boundaries; no generation prompts or API calls."""
from collections import Counter

_COMPLETE = {"rollout_complete", "scored"}


def recover_terminal_checkpoint(state):
    """Recover the old running checkpoint written after a terminal tutor call."""
    if state.get("status") == "scored":
        return False
    control = state.get("last_tutor_control") or {}
    reason = ("end" if control.get("ended") else
              "problem_change" if control.get("problem_change") else None)
    if reason is None or not state.get("next_speaking_step"):
        return False
    changed = state.get("status") != "rollout_complete" or state.get("stop_reason") != reason
    state.update(status="rollout_complete", stop_reason=reason)
    return changed


def publisher_no_generated_annotation(moment_id):
    """Match publisher scoring.score_batch's no-detections Annotation exactly."""
    return {
        "scenario_id": moment_id,
        "annotation_type": "scaffolding",
        "turn_start": 0,
        "turn_end": 0,
        "situation": "",
        "action": "[No generated turns in transcript]",
        "result": "",
        "action_decomposed": [],
        "overscaffold_decomposed": [],
        "action_label": "neither",
        "usage": {k: 0 for k in (
            "input_tokens", "output_tokens", "total_tokens", "input_uncached",
            "cache_read", "cache_write", "output", "reasoning", "total")},
    }


def has_tutor_text(state):
    return any(str(t.get("role", "")).upper() == "TUTOR"
               and isinstance(t.get("text"), str) and t["text"].strip()
               for t in state.get("generated_turns", []))


def metric_coverage(states, planned_cases):
    """Expose missing/error/default cases; never silently equate these groups."""
    counts = Counter(s.get("status", "pending") for s in states)
    completed = [s for s in states if s.get("status") in _COMPLETE]
    scored = [s for s in states if s.get("status") == "scored"]
    return {
        "planned_cases": planned_cases,
        "persisted_cases": len(states),
        "missing_case_states": max(0, planned_cases - len(states)),
        "status_counts": dict(counts),
        "rollouts_completed": len(completed),
        "completed_without_generated_turns": sum(not s.get("generated_turns") for s in completed),
        "completed_without_tutor_text": sum(not has_tutor_text(s) for s in completed),
        "scored_cases_in_metric_denominator": len(scored),
        "scored_publisher_no_generated_defaults": sum(not s.get("generated_turns") for s in scored),
        "scored_with_tutor_text": sum(has_tutor_text(s) for s in scored),
        "unscored_completed_cases": sum(s.get("status") == "rollout_complete" for s in states),
        "cases_with_scoring_errors": sum(bool(s.get("scoring_error")) for s in states),
        "failed_rollouts": counts.get("failed", 0),
    }


def paired_scored_comparison(states_by_condition, moments, planned_indices, metric_fn):
    """Identical available scored cases across all compared conditions."""
    conditions = list(states_by_condition)
    indexed = {
        c: {s["moment_index"]: s for s in states
            if s.get("status") == "scored" and s.get("annotation") is not None}
        for c, states in states_by_condition.items()
    }
    common = set(planned_indices)
    for c in conditions:
        common.intersection_update(indexed[c])
    indices = [i for i in planned_indices if i in common]
    return {
        "scope": "Common scored cases only; includes publisher no-generated defaults.",
        "conditions": conditions,
        "planned_cases": len(planned_indices),
        "paired_scored_cases": len(indices),
        "paired_moment_indices": indices,
        "planned_cases_not_yet_paired": len(planned_indices) - len(indices),
        "condition_metrics": {
            c: metric_fn([(moments[i], indexed[c][i]["annotation"]) for i in indices])
            if indices else None for c in conditions
        },
    }


def first_decision_agreement(states, moments):
    """Initial route versus initial category, once per case; never later routes."""
    counts = Counter()
    confusion = Counter()
    later_modes = Counter()
    for state in states:
        routes = state.get("routes", [])
        initial = [r for r in routes if r.get("step") == 0]
        counts["cases_with_initial_record" if initial else "cases_missing_initial_record"] += 1
        if initial:
            counts["duplicate_initial_records_ignored"] += max(0, len(initial) - 1)
            first = initial[0].get("answer") or {}
            choice = first.get("choice")
            distinct = {
                (r.get("answer") or {}).get("choice") for r in initial
                if (r.get("answer") or {}).get("choice") in ("scaffolding", "rigor")
            }
            if len(distinct) > 1:
                counts["conflicting_initial_retry_records_excluded"] += 1
            elif first.get("type") != "choice" or choice not in ("scaffolding", "rigor"):
                counts["invalid_or_fallback_initial_decisions"] += 1
            else:
                gold = moments[state["moment_index"]].get("dimension")
                if gold not in ("scaffolding", "rigor"):
                    counts["unclear_initial_categories_excluded"] += 1
                else:
                    counts["eligible_first_decisions"] += 1
                    counts["agreements"] += choice == gold
                    confusion[(gold, choice)] += 1
        # Descriptive only. A changed learner state can warrant a changed route.
        seen_steps = set()
        for route in routes:
            step = route.get("step")
            if not isinstance(step, int) or step <= 0 or step in seen_steps:
                continue
            seen_steps.add(step)
            answer = route.get("answer") or {}
            if answer.get("type") == "choice" and answer.get("choice") in ("scaffolding", "rigor"):
                later_modes[answer["choice"]] += 1
    n = counts["eligible_first_decisions"]
    return {
        "scope": "First step=0 decision versus initial publisher category; proxy agreement, not validity.",
        "eligible_first_decisions": n,
        "agreements": counts["agreements"],
        "agreement_rate": counts["agreements"] / n if n else None,
        "coverage": dict(counts),
        "confusion": [{"initial_category": gold, "first_choice": choice, "n": count}
                      for (gold, choice), count in sorted(confusion.items())],
        "later_decisions_not_scored_against_initial_category": sum(later_modes.values()),
        "later_choice_counts_descriptive_only": dict(later_modes),
    }
