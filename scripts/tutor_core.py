"""Compact pedagogical next-move plan for an AI tutor, not a mastery model.

This module only interprets observed response metadata and existing reviewed
bank items. It never creates keys, authenticates content, executes learner
answers or claims calibrated knowledge probabilities. The LLM still needs
to write/assess source-grounded reasoning probes and request clarifications.
"""
from collections import defaultdict

HIGHER = {"apply", "analyze", "transfer"}
VALID_LEVELS = {"recall", "understand", "apply", "analyze", "transfer"}

INSTRUCTIONS = {
    "baseline": "Ask one short, fair question establishing the stated learning objective.",
    "repair_prerequisite": ("Probe the nearest prerequisite or contrast with a different "
                            "representation. Do not repeat the same numbers or stem."),
    "clarify_reasoning": ("Ask what reasoning led to the answer, or identify the first "
                          "unsupported step. Do not declare a misconception from a wrong "
                          "answer alone."),
    "verify_independently": ("Verify the same concept with a different item family and "
                             "representation, without hints or the previous answer key."),
    "probe_transfer": ("Ask one bounded application, boundary case or explanation requiring "
                       "a different cognitive move, not another recall clone."),
    "close_and_review": ("Stop posing questions; summarize observed evidence, what remains "
                         "untested, and one concrete follow-up retrieval probe."),
    "draft_source_anchored_item": ("No suitable unused reviewed item remains. Draft ONE new "
                                  "source-aligned question with a distinct item family; "
                                  "independently check its answer, rubric, alternatives and "
                                  "fairness before presenting it.")
}


def _session_events(history, session):
    if not session or not session.get("id"):
        return list(history)
    return [e for e in history if e.get("session") == session["id"]]


def plan(items, history, session=None, next_item=None):
    """Return a short, answer-key-free and student-text-free teaching instruction.

    The selected next_item is a suggestion from the existing chooser, not
    evidence that the item actually fits the desired diagnostic probe.
    """
    items = items or []
    history = history or []
    recent = _session_events(history, session)
    last = recent[-1] if recent else None
    bank_by_id = {item["id"]: item for item in items}
    last_item = bank_by_id.get(last.get("id")) if last else None
    source_concept = last.get("concept") if last else None
    observed = [e for e in history if source_concept and e.get("concept") == source_concept]
    used = {e.get("id") for e in recent}
    budget = session.get("limit") if session else None
    ended = budget is not None and len(recent) >= budget
    focus = session.get("focus") if session else None
    candidates = [q for q in items if q.get("id") not in used
                  and (not focus or q.get("concept") == focus)]
    known_families = {e.get("family", e.get("id")) for e in observed}
    known_levels = {e.get("level") for e in observed}
    evidence = {
        "answers_this_session": len(recent),
        "independent_families_for_last_concept": len(known_families),
        "cognitive_levels_for_last_concept": sorted(
            x for x in known_levels if x in VALID_LEVELS),
        "delayed_retrieval_verified": False,
        "mastery_probability_available": False,
    }
    if ended:
        move = "close_and_review"
    elif last is None:
        move = "baseline"
    elif last.get("score", 0) < .5:
        move = "repair_prerequisite" if last_item and last_item.get("prerequisites") else "clarify_reasoning"
    elif last.get("score", 0) < 1:
        move = "clarify_reasoning"
    elif last.get("confidence") in ("guess", "unsure") or last.get("hint_used"):
        move = "verify_independently"
    else:
        move = "probe_transfer"
    evidence["delayed_retrieval_verified"] = False  # never infer time gaps from same-session success
    underlying_need = move
    if not ended and not candidates:
        move = "draft_source_anchored_item"
    suggestion = None
    fit = "none"
    if not ended and next_item is not None:
        family = next_item.get("family", next_item["id"])
        source_family = last.get("family", last.get("id")) if last else None
        suggestion = {
            "id": next_item["id"], "concept": next_item["concept"],
            "level": next_item["level"], "family": family,
        }
        fit = "possible"
        if move == "verify_independently":
            fit = ("matching" if next_item["concept"] == source_concept
                   and family != source_family and family not in known_families
                   else "review_or_author_better_variant")
        elif move == "probe_transfer":
            fit = ("matching" if next_item["level"] in HIGHER
                   and (next_item["concept"] != source_concept
                        or family not in known_families)
                   else "review_or_author_better_variant")
        elif move == "repair_prerequisite":
            fit = ("matching" if next_item["concept"] in last_item.get("prerequisites", [])
                   else "review_or_author_better_variant")
        elif move == "clarify_reasoning":
            fit = "possible_requires_reasoning_check"
        else:
            fit = "possible"
    diagnosis = "not_enough_evidence"
    if last:
        if last.get("score", 0) < 1:
            diagnosis = ("reviewer_tag_not_independent_diagnosis" if last.get("misconception")
                         else "error_cause_unverified")
        elif last.get("confidence") in ("guess", "unsure") or last.get("hint_used"):
            diagnosis = "correctness_needs_independent_confirmation"
        else:
            diagnosis = "correct_on_this_item_only"
    authoring_brief = None
    if move == "draft_source_anchored_item":
        # A generation brief, not a fabricated or automatically approved item.
        source = last_item.get("source") if last_item else None
        authoring_brief = {
            "objective_concept": source_concept or focus,
            "underlying_learning_need": underlying_need,
            "previous_cognitive_levels": sorted(x for x in known_levels if x in VALID_LEVELS),
            "avoid_same_item_families": sorted(str(x) for x in known_families if x)[:8],
            "source_anchor_to_verify": source,
            "source_is_actual_instructor_material_verified": False,
            "request_one_new_item_only": True,
            "review_before_presenting": [
                "match_stated_course_scope",
                "show_all_conditions_and_valid_answers",
                "check_solution_and_rubric_independently",
                "ensure_new_reasoning_not_just_new_numbers",
                "avoid_ambiguity_and_trick_wording"
            ]
        }
    # Never embed student original text, actual answer keys, explanations,
    # or unverified diagnostic labels in the learner-facing plan.
    return {
        "move": move, "instruction": INSTRUCTIONS[move],
        "target_concept": (source_concept if last else focus),
        "evidence_status": diagnosis,
        "observation": evidence,
        "suggested_reviewed_item": suggestion,
        "suggestion_fit": fit,
        "new_item_authoring_brief": authoring_brief,
        "must_ask_one_question": move != "close_and_review",
        "stop_reason": "session_budget" if ended else None,
        "safety": ("One response does not prove mastery. Do not invent source claims, "
                   "misconception causes, student identity or learning outcome gains.")
    }


def compact_session_report(items, history, session=None):
    """Formative narrative facts and next study actions, not student ranking."""
    events = _session_events(history, session)
    groups = defaultdict(list)
    for event in events:
        groups[event.get("concept", "unknown")].append(event)
    out = []
    for concept, sample in sorted(groups.items()):
        families = {e.get("family", e.get("id")) for e in sample}
        incorrect = sum(e.get("score", 0) < .5 for e in sample)
        partial = sum(.5 <= e.get("score", 0) < 1 for e in sample)
        uncertain = sum(e.get("confidence") in ("guess", "unsure") or e.get("hint_used")
                        for e in sample)
        out.append({
            "concept": concept, "observations": len(sample),
            "independent_families": len(families),
            "incorrect_or_unscored": incorrect,
            "partially_correct": partial,
            "uncertain_or_assisted": uncertain,
            "interpretation": ("further_independent_probe_needed"
                               if len(families) < 2 or incorrect or partial or uncertain
                               else "observed_success_not_long_term_mastery")
        })
    covered = {x["concept"] for x in out}
    untested = sorted({q["concept"] for q in items if q["concept"] not in covered})
    return {
        "scope": "current_session_observations_only",
        "answered": len(events),
        "concepts": out,
        "untested_concepts": untested,
        "next_action": ("close_and_schedule_review" if session and
                        session.get("limit") is not None and
                        len(events) >= session["limit"] else
                        "ask_one_new_independent_probe" if events
                        else "establish_baseline"),
        "retention_verified": False,
        "standardized_mastery_estimate": None
    }
