"""Evidence-aware formative diagnosis and transparent adaptive item targeting.

This is NOT an empirically calibrated IRT / BKT / FSRS implementation.
"""
from collections import defaultdict
from datetime import datetime, timezone

HIGHER = {"apply", "analyze", "transfer"}
LEVEL_WEIGHT = {"recall": 0.8, "understand": 0.95, "apply": 1.1,
                "analyze": 1.15, "transfer": 1.2}
TYPE_WEIGHT = {"single": 0.72, "short": 1.0, "manual": 1.08}


def event_day(event, now=None):
    try:
        dt = datetime.fromisoformat(event["at"].replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).date().isoformat()
    except (ValueError, TypeError, KeyError, AttributeError):
        return (now or datetime.now(timezone.utc)).date().isoformat()


def estimate(events, now=None):
    """Conservative observed-performance signal, NOT probability of mastery."""
    if not events:
        return {"label": "untested", "rate": None, "count": 0, "unique_items": 0,
                "families": 0, "days": 0, "levels": [], "effective_evidence": 0.0,
                "flags": [], "gaps": []}
    latest_per_family_day = {}
    for event in events:
        family = event.get("family", event["id"])
        latest_per_family_day[(family, event_day(event, now))] = event
    reps = list(latest_per_family_day.values())
    families = defaultdict(list)
    for event in reps:
        families[event.get("family", event["id"])].append(event)
    total, hits = 0.0, 0.0
    for group in families.values():
        for repeat, item in enumerate(sorted(group, key=lambda e: event_day(e, now))):
            weight = TYPE_WEIGHT.get(item.get("type", "short"), 1.0)
            weight *= LEVEL_WEIGHT.get(item.get("level", "understand"), 1.0)
            weight *= {1: 0.9, 2: 1.0, 3: 1.1}.get(item.get("difficulty", 2), 1.0)
            weight *= 1.0 if repeat == 0 else (0.35 if repeat == 1 else 0.12)
            if item.get("hint_used"):
                weight *= 0.5
            if item.get("score", 0) > 0 and item.get("confidence") == "guess":
                weight *= 0.35
            elif item.get("score", 0) > 0 and item.get("confidence") == "unsure":
                weight *= 0.7
            hits += weight * item["score"]
            total += weight
    rate = (1 + hits) / (2 + total)
    days = {event_day(e, now) for e in reps}
    levels = {e.get("level", "unknown") for e in reps}
    higher_success = any(e.get("level") in HIGHER and e["score"] >= 1
                         and not e.get("hint_used")
                         and e.get("confidence") != "guess" for e in reps)
    recent_miss = events[-1]["score"] < 0.5
    flags = []
    if any(e.get("confidence") == "guess" and e["score"] > 0 for e in reps):
        flags.append("correct_but_guessed")
    if any(e.get("confidence") == "sure" and e["score"] < 1 for e in reps):
        flags.append("confident_error")
    if any(e.get("hint_used") for e in reps):
        flags.append("used_hint")
    if recent_miss:
        flags.append("recent_miss")
    gaps = []
    if len(families) < 3:
        gaps.append("few_independent_item_families")
    if len(days) < 2:
        gaps.append("no_delayed_retrieval")
    if len(levels) < 2:
        gaps.append("single_cognitive_level")
    if not higher_success:
        gaps.append("no_verified_higher_order_success")
    sufficient = (len(reps) >= 4 and len(families) >= 3 and len(days) >= 2
                  and len(levels) >= 2 and higher_success and total >= 2.2)
    if sufficient and rate >= 0.72 and not recent_miss:
        label = "tentatively_strong"
    elif len(families) >= 2 and len(reps) >= 3 and rate <= 0.43:
        label = "needs_review"
    elif len(families) < 2 or len(reps) < 3:
        label = "insufficient_evidence"
    else:
        label = "developing"
    return {"label": label, "rate": round(rate, 3), "count": len(events),
            "unique_items": len({e["id"] for e in events}), "families": len(families),
            "days": len(days), "levels": sorted(levels),
            "effective_evidence": round(total, 2), "flags": flags, "gaps": gaps}


def select_item(items, history, mode="quick", now=None, session_history=None, focus=None):
    """Low-cost coverage + error-repair item utility; not a formal CAT algorithm."""
    now = now or datetime.now(timezone.utc)
    session_history = session_history or []
    used = {e["id"] for e in session_history}
    candidates = [q for q in items if q["id"] not in used
                  and (not focus or q["concept"] == focus)]
    if not candidates:
        return None
    by_concept = defaultdict(list)
    for e in history:
        by_concept[e["concept"]].append(e)
    seen_families = {e.get("family", e["id"]) for e in history}
    recent_ids = {e["id"] for e in history[-5:]}
    last = session_history[-1] if session_history else None
    last_q = next((q for q in items if last and q["id"] == last["id"]), None)
    branch = None
    if last:
        if last["score"] < 0.5:
            branch = "repair"
        elif last.get("confidence") in ("guess", "unsure") or last.get("hint_used"):
            branch = "verify"
        elif last["score"] == 1:
            branch = "transfer"

    def priority(q):
        events = by_concept[q["concept"]]
        state = estimate(events, now)
        family = q.get("family", q["id"])
        value = 0.0
        if not events:
            value += 8
        if not any(e["concept"] == q["concept"] for e in session_history):
            value += 2
        if q["level"] not in {e["level"] for e in events}:
            value += 2
        if "no_verified_higher_order_success" in state["gaps"] and q["level"] in HIGHER:
            value += 3
        if state["label"] == "needs_review":
            value += 4
        if state["label"] == "insufficient_evidence" and events:
            value += 2
        if family in seen_families:
            value -= 5
        if q["id"] in recent_ids:
            value -= 4
        if mode == "quick" and q["level"] in {"recall", "understand", "apply"}:
            value += 1
        if mode == "deep" and q["level"] in HIGHER:
            value += 3
        avg = sum(e["score"] for e in events) / len(events) if events else 0.6
        target = 1 if avg < 0.4 else (3 if avg > 0.8 else 2)
        value -= 0.85 * abs(q["difficulty"] - target)
        if last and last_q:
            same = q["concept"] == last_q["concept"]
            if branch == "repair":
                if not focus and q["concept"] in last_q.get("prerequisites", []):
                    value += 20
                elif same:
                    value += 13
                if q["difficulty"] <= last_q["difficulty"]:
                    value += 2
            elif branch == "verify":
                if same:
                    value += 13
                if q["type"] != "single":
                    value += 3
            elif branch == "transfer":
                if same and q["level"] in HIGHER:
                    value += 7
                elif not same:
                    value += 2
        return value
    return max(candidates, key=lambda q: (priority(q), -items.index(q)))


def session_summary(history, session):
    if session is None:
        return None
    count = sum(1 for e in history if e.get("session") == session["id"])
    return {"id": session["id"], "mode": session["mode"], "limit": session["limit"],
            "answered": count, "remaining": max(0, session["limit"] - count),
            "focus": session.get("focus")}
