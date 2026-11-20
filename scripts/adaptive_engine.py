"""Explain which existing heuristic led to the next prompt.

Rationale codes are local explanations, not causal proof that adaptivity
improves student learning. Selection policy is preserved for reproducibility.
"""
try:
    from . import diagnosis
except ImportError:
    import diagnosis


def choose(items, history, mode="quick", session_history=None, focus=None, now=None):
    session_history = session_history or []
    choice = diagnosis.select_item(items, history, mode=mode, now=now,
                                   session_history=session_history, focus=focus)
    if choice is None:
        return None, None
    prior = [event for event in history if event.get("concept") == choice["concept"]]
    reasons = []
    if focus:
        reasons.append("respects_explicit_focus")
    if not prior:
        reasons.append("expand_untested_concept_coverage")
    else:
        if choice["level"] not in {e.get("level") for e in prior}:
            reasons.append("probe_untested_cognitive_level")
        if choice.get("family", choice["id"]) not in {
                e.get("family", e["id"]) for e in prior}:
            reasons.append("add_independent_item_family")
        if diagnosis.estimate(prior)["label"] == "needs_review":
            reasons.append("revisit_observed_misses")
    if session_history:
        last = session_history[-1]
        if last["score"] < .5:
            reasons.append("follow_up_after_incorrect_answer")
        elif last.get("confidence") in ("guess","unsure") or last.get("hint_used"):
            reasons.append("verify_uncertain_or_assisted_answer")
        elif last["score"] >= 1:
            reasons.append("increase_breadth_or_transfer_after_correct_answer")
    if not reasons:
        reasons.append("heuristic_difficulty_and_coverage_balance")
    return choice, {
        "policy": "rule_based_v02_unchanged",
        "reason_codes": reasons,
        "reason_scope": "explanatory_tags_not_exact_priority_breakdown",
        "caution": "Selection benefits are not established by randomized studies."
    }
