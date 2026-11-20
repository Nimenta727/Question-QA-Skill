#!/usr/bin/env python3
"""Offline evidence tracker for Question-QA-Skill. Stdlib only; formative, not calibrated."""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

LEVELS = {"recall", "understand", "apply", "analyze", "transfer"}
TYPES = {"single", "short", "manual"}
CONFIDENCES = {"sure", "unsure", "guess", "none"}
SPACING_DAYS = (1, 3, 7, 14, 30)
SCHEMA = 1
try:
    from . import diagnosis, feedback, assessment_engine, evidence_engine, prediction_engine, adaptive_engine, math_equivalence, state_store, appeals, audit_ledger, reviewer_credentials
except ImportError:
    import diagnosis
    import feedback
    import assessment_engine
    import evidence_engine
    import prediction_engine
    import adaptive_engine
    import math_equivalence
    import state_store
    import appeals
    import audit_ledger
    import reviewer_credentials


def utc_now():
    return datetime.now(timezone.utc)


def fail(message):
    raise ValueError(message)


def normalize(value):
    return unicodedata.normalize("NFKC", str(value)).strip().casefold()


def validate_bank(data):
    if not isinstance(data, dict) or data.get("version") != SCHEMA:
        fail("bank.version must equal 1")
    if not isinstance(data.get("subject"), str) or not data["subject"].strip():
        fail("bank.subject is required")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("bank.items must be nonempty")
    ids = set()
    for index, q in enumerate(items):
        if not isinstance(q, dict):
            fail("items[%d] must be an object" % index)
        for key in ("id", "concept", "stem", "claim", "evidence", "explanation", "source"):
            if not isinstance(q.get(key), str) or not q[key].strip():
                fail("%s missing nonempty %s" % (q.get("id", index), key))
        if q["id"] in ids:
            fail("duplicate item id: " + q["id"])
        ids.add(q["id"])
        if q.get("level") not in LEVELS or q.get("type") not in TYPES:
            fail("%s has invalid level/type" % q["id"])
        if type(q.get("difficulty")) is not int or not 1 <= q["difficulty"] <= 3:
            fail("%s difficulty must be 1..3" % q["id"])
        if q["type"] == "single":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                fail("%s single needs four options" % q["id"])
            if not all(isinstance(x, str) and x.strip() for x in opts):
                fail("%s options must be nonempty" % q["id"])
            if len(set(map(normalize, opts))) != 4:
                fail("%s has duplicate options" % q["id"])
            if q.get("answer") not in list("ABCD"):
                fail("%s answer must be A/B/C/D" % q["id"])
        elif q["type"] == "short":
            answers = [q.get("answer")] + q.get("aliases", [])
            if not isinstance(q.get("answer"), str) or not q["answer"].strip():
                fail("%s requires a short-answer key" % q["id"])
            if not isinstance(q.get("aliases", []), list) or not all(
                isinstance(a, str) and a.strip() for a in answers):
                fail("%s has invalid aliases" % q["id"])
            if len(set(map(normalize, answers))) != len(answers):
                fail("%s has duplicate short-answer aliases" % q["id"])
            if "answer_equivalence" in q:
                vars_ = math_equivalence.validate_spec(q["answer_equivalence"])
                math_equivalence.polynomial(q["answer"], vars_)
        elif not isinstance(q.get("rubric"), list) or not q["rubric"] or not all(
                isinstance(x, str) and x.strip() for x in q["rubric"]):
            fail("%s manual response requires rubric criteria" % q["id"])
    for q in items:
        if "answer_equivalence" in q and q["type"] != "short":
            fail(q["id"] + " answer_equivalence is only supported on short answers")
    concepts = {q["concept"] for q in items}
    for q in items:
        if "family" in q and (not isinstance(q["family"], str) or not q["family"].strip()):
            fail(q["id"] + " invalid family")
        if "prerequisites" in q:
            p = q["prerequisites"]
            if (not isinstance(p, list) or
                not all(isinstance(x, str) and x in concepts and x != q["concept"]
                        for x in p) or len(set(p)) != len(p)):
                fail(q["id"] + " invalid prerequisites")
        if "misconceptions" in q:
            m = q["misconceptions"]
            if (q["type"] != "single" or not isinstance(m, dict) or
                not all(k in "ABCD" and k != q["answer"] and
                        isinstance(v, str) and v.strip() for k, v in m.items())):
                fail(q["id"] + " invalid misconceptions")
    return items


def read_bank(path):
    raw = Path(path).read_bytes()
    data = json.loads(raw)
    validate_bank(data)
    return data, hashlib.sha256(raw).hexdigest()


def read_state(path):
    if not Path(path).exists():
        return {"version": SCHEMA, "history": [], "pending": None}
    state = json.loads(Path(path).read_text(encoding="utf-8"))
    if state.get("version") != SCHEMA or not isinstance(state.get("history"), list):
        fail("unsupported or invalid state")
    return state


def write_state(path, state):
    """Atomic write with validated prior-state backup.

    All CLI state operations are guarded by state_store.locked_state.
    """
    state_store.save(path, state)


def evidence(history):
    out = defaultdict(list)
    for h in history:
        out[(h["concept"], h["level"])].append(h)
    return out


def estimate(events):
    return diagnosis.estimate(events)


def due_date(events):
    if not events:
        return None
    last = events[-1]
    streak = 0
    for event in reversed(events):
        if event["score"] < 1:
            break
        streak += 1
    days = SPACING_DAYS[min(streak - 1, len(SPACING_DAYS) - 1)] if streak else 1
    return (datetime.fromisoformat(last["at"]) + timedelta(days=days)).date().isoformat()


def select_item(items, history, mode="quick", now=None, session_history=None, focus=None):
    return diagnosis.select_item(items, history, mode, now, session_history, focus)


def safe_prompt(q):
    data = {"id": q["id"], "question": q["stem"], "type": q["type"]}
    if q["type"] == "single":
        data["options"] = dict(zip("ABCD", q["options"]))
    return data


def grade(q, response, manual_score=None, reason=None, allow_unverified=False):
    if q["type"] == "manual":
        if manual_score is None or manual_score not in (0.0, 0.5, 1.0):
            fail("manual item requires --score 0, 0.5, or 1")
        if not reason or not reason.strip():
            fail("manual item requires --reason describing rubric evidence")
        return float(manual_score), "rubric_review"
    if manual_score is not None:
        fail("objective items must be graded by their answer key, not --score")
    if q["type"] == "single":
        guess = normalize(response)
        by_letter = guess.upper() if len(guess) == 1 else None
        if by_letter in "ABCD" if by_letter is not None else False:
            picked = by_letter
        else:
            matches = [k for k, option in zip("ABCD", q["options"]) if normalize(option) == guess]
            picked = matches[0] if len(matches) == 1 else None
        return float(picked == q["answer"]), "exact_key"
    valid = {normalize(q["answer"])} | {normalize(x) for x in q.get("aliases", [])}
    if normalize(response) in valid:
        return 1.0, "exact_key"
    if "answer_equivalence" in q:
        try:
            equivalent = math_equivalence.matches(q["answer"], response, q["answer_equivalence"])
        except ValueError:
            # Preserve grade()'s legacy numeric return contract; the CLI
            # explicitly refuses to commit this unresolved judgment.
            return 0.0, "math_equivalence_unverified"
        return (1.0 if equivalent else 0.0), ("verified_math_equivalence" if equivalent
                                               else "verified_math_inequivalent")
    return 0.0, "exact_key"


def answer_key(q):
    if q["type"] == "single":
        return q["answer"] + ": " + q["options"]["ABCD".index(q["answer"])]
    if q["type"] == "short":
        return q["answer"]
    return "See rubric; no automatic model grade"


def new_session(mode, limit=None, focus=None):
    limit = limit or (6 if mode == "quick" else 5)
    if not 1 <= limit <= 20:
        fail("session limit must be between 1 and 20")
    return {"id": uuid.uuid4().hex[:12], "mode": mode, "limit": limit, "focus": focus}


def ensure_focus(bank, focus):
    if focus and focus not in {q["concept"] for q in bank["items"]}:
        fail("unknown focus concept: " + focus)


def handle_start(args):
    bank, _ = read_bank(args.bank)
    ensure_focus(bank, args.focus)
    state = read_state(args.state)
    if state.get("pending") and not args.discard_pending:
        fail("unanswered question pending; submit first or pass --discard-pending")
    state["session"] = new_session(args.mode, args.limit, args.focus)
    state["pending"] = None
    write_state(args.state, state)
    print(json.dumps({"session": diagnosis.session_summary(state["history"], state["session"])},
                     ensure_ascii=True))


def handle_next(args):
    bank, digest = read_bank(args.bank)
    state = read_state(args.state)
    if not state.get("session"):
        mode = args.mode or "quick"
        ensure_focus(bank, args.focus)
        state["session"] = new_session(mode, args.limit, args.focus)
    session = state["session"]
    if args.mode and args.mode != session["mode"]:
        fail("active mode differs; use start")
    if args.focus and args.focus != session.get("focus"):
        fail("active focus differs; use start")
    if args.limit and args.limit != session["limit"]:
        fail("active limit differs; use start")
    if state.get("pending"):
        p = state["pending"]
        if p.get("bank_digest") != digest:
            fail("bank changed while pending; restore the bank or reset-pending")
        q = next((x for x in bank["items"] if x["id"] == p["id"]), None)
        if q is None:
            fail("pending item not found")
    else:
        part = [e for e in state["history"] if e.get("session") == session["id"]]
        if len(part) >= session["limit"]:
            write_state(args.state, state)
            print(json.dumps({"complete": True, "reason": "question_budget_reached",
                              "session": diagnosis.session_summary(state["history"], session)},
                             ensure_ascii=True))
            return
        q, selection = adaptive_engine.choose(bank["items"], state["history"], session["mode"],
                                              session_history=part, focus=session.get("focus"))
        if q is None:
            write_state(args.state, state)
            print(json.dumps({"complete": True, "reason": "item_bank_exhausted",
                              "session": diagnosis.session_summary(state["history"], session)},
                             ensure_ascii=True))
            return
        state["pending"] = {"id": q["id"], "bank_digest": digest,
                            "selection": selection}
        write_state(args.state, state)
    result = safe_prompt(q)
    if state.get("pending", {}).get("selection"):
        result["selection"] = state["pending"]["selection"]
    result["session"] = diagnosis.session_summary(state["history"], session)
    print(json.dumps(result, ensure_ascii=True))


def selected_choice(q, response):
    if q["type"] != "single":
        return None
    ans = normalize(response)
    if len(ans) == 1 and ans.upper() in "ABCD":
        return ans.upper()
    found = [code for code, text in zip("ABCD", q["options"]) if normalize(text) == ans]
    return found[0] if len(found) == 1 else None


def handle_answer(args):
    bank, digest = read_bank(args.bank)
    state = read_state(args.state)
    pending = state.get("pending")
    if not pending:
        fail("no pending item; run next first")
    if pending.get("bank_digest") != digest:
        fail("bank changed while a question was pending")
    q = next((x for x in bank["items"] if x["id"] == pending["id"]), None)
    if q is None:
        fail("pending item not found")
    if args.response_file is not None:
        if args.response is not None:
            fail("--response and --response-file cannot be combined")
        # Avoid raw answer in the CLI process list or shell history.
        args.response = Path(args.response_file).read_text(encoding="utf-8")
    if args.response is None:
        fail("provide --response or --response-file")
    rubric_review = None
    if args.independent_reviews is not None:
        if q["type"] != "manual" or args.score is not None or args.rubric_judgments is not None:
            fail("--independent-reviews applies only to manual items and cannot combine with other scores")
        rubric_review = assessment_engine.resolve(
            q["rubric"], args.response, args.independent_reviews, args.adjudication)
        score, method = rubric_review["score"], rubric_review["method"]
    elif args.rubric_judgments is not None:
        if q["type"] != "manual" or args.score is not None:
            fail("--rubric-judgments is only for manual items and cannot combine with --score")
        if not args.reason or not args.reason.strip():
            fail("structured rubric review needs --reason")
        rubric_review = feedback.assess_rubric(q["rubric"], args.rubric_judgments)
        score, method = rubric_review["score"], rubric_review["method"]
    else:
        score, method = grade(q, args.response, args.score, args.reason,
                              allow_unverified=args.review_equivalent)
    if method == "math_equivalence_unverified" and not args.review_equivalent:
        fail("math_equivalence_unverified: unsupported input; request independent review")
    if args.adjudication and args.independent_reviews is None:
        fail("--adjudication requires --independent-reviews")
    if args.review_equivalent:
        if q["type"] != "short" or args.score is not None or args.rubric_judgments is not None:
            fail("--review-equivalent only available for short answer with independent reviewer")
        if score == 1:
            fail("answer already matches key; no equivalence review required")
        if not args.reason or not args.reason.strip():
            fail("equivalence review requires --reason with independently checked equivalence")
        score, method = 1.0, "reviewed_equivalent_answer"
    if not state.get("session"):
        state["session"] = new_session("quick")
    session = state["session"]
    chosen = selected_choice(q, args.response)
    misconception = (q.get("misconceptions", {}).get(chosen)
                     if chosen is not None and score < 1 else None)
    if score < 1 and args.misconception:
        misconception = args.misconception.strip()[:100]
    event = {
        "id": q["id"], "family": q.get("family", q["id"]),
        "concept": q["concept"], "level": q["level"],
        "difficulty": q["difficulty"], "type": q["type"],
        "score": score, "method": method,
        "confidence": args.confidence, "hint_used": args.hint_used,
        "session": session["id"], "at": utc_now().isoformat(),
        "event_id": uuid.uuid4().hex
    }
    if misconception:
        event["misconception"] = misconception
    if rubric_review is not None:
        event["criterion_scores"] = [r["score"] for r in rubric_review["criteria"]]
        if "agreement" in rubric_review:
            # Persist only small numeric agreement metadata, not reviewer IDs,
            # quotations, free-form evidence or the raw student's answer.
            event["review_agreement"] = rubric_review["agreement"]["rate"]
            event["review_disputes"] = len(rubric_review["agreement"]["disputed_indices"])
    state["history"].append(event)
    state["pending"] = None
    write_state(args.state, state)
    c_events = [e for e in state["history"] if e["concept"] == q["concept"]]
    result = {
        "event_id": event["event_id"], "score": score, "method": method, "expected": answer_key(q),
        "explanation": q["explanation"], "concept": q["concept"],
        "level": q["level"], "status": estimate(c_events),
        "evidence_profile": evidence_engine.profile(c_events),
        "prediction_baseline": prediction_engine.history_baseline(c_events),
        "level_status": estimate(evidence(state["history"])[(q["concept"], q["level"])]),
        "next_review": due_date(evidence(state["history"])[(q["concept"], q["level"])]),
        "session": diagnosis.session_summary(state["history"], session)
    }
    if misconception:
        result["misconception"] = misconception
    result["feedback"] = feedback.concise_feedback(q, score, misconception, args.confidence)
    if rubric_review is not None:
        result["assessment"] = rubric_review
    if method == "verified_math_equivalence":
        result["math_note"] = ("Equivalent under the item's explicitly enabled, bounded "
                               "rational/polynomial rules, not a general semantic proof.")
    if args.review_equivalent:
        result["review_note"] = ("Accepted as equivalent by reviewer; "
                                 "not verified automatically by local code.")
    if q["type"] == "manual":
        result["rubric"] = q["rubric"]
        result["review_reason"] = args.reason
    elif score == 0 and q["type"] == "short":
        result["note"] = "Exact match only; review equivalent answers before inferring misconceptions."
    print(json.dumps(result, ensure_ascii=True))


def handle_report(args):
    state = read_state(args.state)
    groups = evidence(state["history"])
    rows = [{"concept": c, "level": l, **estimate(events),
             "evidence_profile": evidence_engine.profile(events),
             "prediction_baseline": prediction_engine.history_baseline(events),
             "next_review": due_date(events)}
            for (c, l), events in sorted(groups.items())]
    by_concept = defaultdict(list)
    for event in state["history"]:
        by_concept[event["concept"]].append(event)
    if args.bank:
        bank, _ = read_bank(args.bank)
        for q in bank["items"]:
            by_concept[q["concept"]]
    concepts = [{"concept": concept, **estimate(events),
                 "evidence_profile": evidence_engine.profile(events),
                 "prediction_baseline": prediction_engine.history_baseline(events),
                 "misconceptions": sorted({e["misconception"] for e in events
                                         if e.get("misconception")})}
                for concept, events in sorted(by_concept.items())]
    print(json.dumps({
        "total_answers": len(state["history"]), "pending": bool(state.get("pending")),
        "appeal_summary": {"open":sum(a.get("status")=="open" for a in state.get("appeals",[])),
                           "resolved":sum(a.get("status")=="resolved" for a in state.get("appeals",[]))},
        "session": diagnosis.session_summary(state["history"], state.get("session")),
        "concepts": concepts, "areas": rows,
        "caution": ("Rate is a descriptive evidence index, NOT a probability of mastery. "
                    "Strong status requires varied independent items, cognitive breadth "
                    "and delayed retrieval. Review timing is not a fitted FSRS model.")
    }, ensure_ascii=True, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline diagnostic assessment / 本地诊断测评")
    subs = parser.add_subparsers(dest="cmd", required=True)
    p = subs.add_parser("validate")
    p.add_argument("bank")
    p = subs.add_parser("start")
    p.add_argument("bank")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--mode", choices=("quick", "deep"), default="quick")
    p.add_argument("--limit", type=int)
    p.add_argument("--focus")
    p.add_argument("--discard-pending", action="store_true")
    p = subs.add_parser("next")
    p.add_argument("bank")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--mode", choices=("quick", "deep"))
    p.add_argument("--limit", type=int)
    p.add_argument("--focus")
    p = subs.add_parser("answer")
    p.add_argument("bank")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--response")
    p.add_argument("--response-file", help="read student response from a private UTF-8 file")
    p.add_argument("--confidence", choices=sorted(CONFIDENCES), default="none")
    p.add_argument("--hint-used", action="store_true")
    p.add_argument("--misconception")
    p.add_argument("--score", type=float)
    p.add_argument("--reason")
    p.add_argument("--rubric-judgments", help="JSON array or @path of reviewed rubric scores")
    p.add_argument("--independent-reviews", help="@file containing two distinct reviewer assessments")
    p.add_argument("--adjudication", help="@file with required third-party decisions on disagreements")
    p.add_argument("--review-equivalent", action="store_true", help="reviewer-confirmed equivalent short answer; requires --reason")
    p = subs.add_parser("report")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--bank")
    p = subs.add_parser("reset-pending")
    p.add_argument("--state", default=".qa-state.json")
    p = subs.add_parser("state-check")
    p.add_argument("--state", default=".qa-state.json")
    p = subs.add_parser("state-recover")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--confirm", action="store_true", help="explicit rollback")
    p.add_argument("--snapshot", help="optional exact snapshot ID; otherwise uses .bak")
    p.add_argument("--acknowledge-audit-rollback", action="store_true",
                   help="explicitly allow restoring an older signed audit chain")
    p.add_argument("--audit-key-file", help="required to validate a protected rollback snapshot")
    p = subs.add_parser("state-snapshots")
    p.add_argument("--state", default=".qa-state.json")
    p = subs.add_parser("state-export")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--output", required=True)
    p.add_argument("--include-private", action="store_true",
                   help="export private event history, not only aggregates")
    p.add_argument("--confirm-private", action="store_true",
                   help="acknowledge that output contains private learner information")
    p = subs.add_parser("state-delete")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--confirm-delete", choices=("DELETE-LOCAL",),
                   help="explicitly delete managed state, backup and snapshots")
    p.add_argument("--acknowledge-audit-deletion", action="store_true",
                   help="explicitly permit deletion of HMAC-protected appeal audit state")
    p = subs.add_parser("appeal-open")
    p.add_argument("--state", default=".qa-state.json")
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--event-id")
    target.add_argument("--event-index", type=int)
    p.add_argument("--reason", choices=sorted(appeals.OPEN_REASONS), required=True)
    p.add_argument("--audit-key-file", help="required when this state has HMAC appeal audit enabled")
    p = subs.add_parser("appeal-list")
    p.add_argument("--state", default=".qa-state.json")
    p = subs.add_parser("appeal-resolve")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--appeal-id", required=True)
    p.add_argument("--decision", choices=("uphold","correct"), required=True)
    p.add_argument("--reason", choices=sorted(appeals.RESOLVE_REASONS), required=True)
    p.add_argument("--reviewer-confirmed", action="store_true",
                   help="explicit self-declared independent review")
    p.add_argument("--new-score", type=float)
    p.add_argument("--criterion-scores", help="JSON array of revised criterion scores")
    p.add_argument("--audit-key-file", help="mandatory in protected appeal mode")
    p.add_argument("--registry", help="local reviewer credential registry for protected appeals")
    p.add_argument("--reviewer-id", help="locally enrolled credential ID")
    p.add_argument("--reviewer-token-file", help="private, 0600 reviewer token file")
    p = subs.add_parser("audit-init")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--registry", required=True)
    p.add_argument("--admin-token-file", required=True)
    p.add_argument("--audit-key-output", required=True)
    p = subs.add_parser("audit-verify")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--audit-key-file", required=True)
    p.add_argument("--checkpoint", help="independently stored checkpoint receipt JSON")
    p = subs.add_parser("audit-checkpoint")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--audit-key-file", required=True)
    p.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "validate":
            bank, _ = read_bank(args.bank)
            print(json.dumps({"valid": True, "items": len(bank["items"])}, ensure_ascii=True))
        else:
            # This lock covers the entire read/modify/backup/atomic-write
            # transaction, preventing lost updates across independent CLIs.
            with state_store.locked_state(args.state):
                if args.cmd == "start":
                    handle_start(args)
                elif args.cmd == "next":
                    handle_next(args)
                elif args.cmd == "answer":
                    handle_answer(args)
                elif args.cmd == "report":
                    handle_report(args)
                elif args.cmd == "reset-pending":
                    state = read_state(args.state)
                    state["pending"] = None
                    write_state(args.state, state)
                    print(json.dumps({"pending": False}))
                elif args.cmd == "state-check":
                    result = state_store.inspect(args.state)
                    marker = audit_ledger.policy_path(args.state).exists()
                    enabled = "audit" in read_state(args.state) if result["current"]["valid"] else False
                    result["audit_policy_present"] = marker
                    result["audit_metadata_consistent"] = (enabled == marker)
                    result["audit_cryptographic_verified"] = False
                    print(json.dumps(result, ensure_ascii=True))
                    if (result["current"]["exists"] and not result["current"]["valid"]
                            or not result["audit_metadata_consistent"]):
                        return 2
                elif args.cmd == "state-recover":
                    if not args.confirm:
                        fail("state-recover requires --confirm (rolls back latest action)")
                    secure = ("audit" in read_state(args.state)
                              or audit_ledger.policy_path(args.state).exists())
                    if secure:
                        if not args.acknowledge_audit_rollback or not args.audit_key_file:
                            fail("audited state rollback requires --acknowledge-audit-rollback "
                                 "and --audit-key-file; retain external receipts")
                        secret = audit_ledger.key_from_file(args.audit_key_file)
                        # Verify the signed destination BEFORE writing any rollback.
                        source = (state_store.backup_path(args.state) if args.snapshot is None
                                  else state_store.snapshots_path(args.state)/(args.snapshot+".json"))
                        if args.snapshot is not None and args.snapshot not in {
                                x["snapshot_id"] for x in state_store.list_snapshots(args.state)
                                if x["valid"]}:
                            fail("invalid signed rollback snapshot")
                        incoming = json.loads(source.read_text(encoding="utf-8"))
                        audit_ledger.verify(incoming,secret)
                        current = read_state(args.state)
                        if (current.get("audit") is not None and
                                incoming["audit"]["registry_id"]!=current["audit"]["registry_id"]):
                            fail("cannot restore a state from a different audit registry")
                        audit_ledger.verify_policy(args.state,incoming,secret)
                    restored = state_store.recover(args.state, args.snapshot)
                    print(json.dumps({"restored": True,
                                      "answers": len(restored["history"]),
                                      "caution": "One or more recent actions may be lost."}, ensure_ascii=True))
                elif args.cmd == "state-snapshots":
                    result = state_store.inspect(args.state)
                    result["audit_policy_present"] = audit_ledger.policy_path(args.state).exists()
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "state-export":
                    if args.include_private != args.confirm_private:
                        fail("--include-private requires --confirm-private; neither may be used alone")
                    result = state_store.export(args.state, args.output, args.include_private)
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "state-delete":
                    if args.confirm_delete != "DELETE-LOCAL":
                        fail("state-delete requires --confirm-delete DELETE-LOCAL")
                    if (read_state(args.state).get("audit") or
                            audit_ledger.policy_path(args.state).exists()) and not args.acknowledge_audit_deletion:
                        fail("audited state deletion requires --acknowledge-audit-deletion; "
                             "external checkpoints and secret keys are not removed")
                    result = state_store.delete_local(args.state)
                    if audit_ledger.policy_path(args.state).exists():
                        audit_ledger.policy_path(args.state).unlink()
                        result["deleted_audit_policy"] = True
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "appeal-open":
                    state = read_state(args.state)
                    audited = ("audit" in state or audit_ledger.policy_path(args.state).exists())
                    if audited != bool(args.audit_key_file):
                        fail("audited appeals require --audit-key-file; "
                             "legacy state must not claim authenticated audit")
                    key = None
                    if audited:
                        key = audit_ledger.key_from_file(args.audit_key_file)
                        audit_ledger.verify(state, key, state_path=args.state)
                    result = appeals.open_appeal(state, args.reason, args.event_id, args.event_index)
                    if audited:
                        result.update(audit_ledger.append(state,key,"open",result))
                    write_state(args.state, state)
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "appeal-list":
                    current = read_state(args.state)
                    result = appeals.view(current)
                    result["audit_enabled"] = "audit" in current
                    result["audit_verified"] = False
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "appeal-resolve":
                    state = read_state(args.state)
                    audited = ("audit" in state or audit_ledger.policy_path(args.state).exists())
                    credential_args = (args.registry,args.reviewer_id,args.reviewer_token_file)
                    if audited:
                        if not args.audit_key_file or not all(credential_args):
                            fail("protected review requires audit key, registry, reviewer-id "
                                 "and reviewer-token-file; self-declaration cannot bypass")
                        key = audit_ledger.key_from_file(args.audit_key_file)
                        audit_ledger.verify(state, key, state_path=args.state)
                        verified = reviewer_credentials.authenticate(
                            args.registry,args.reviewer_id,args.reviewer_token_file,
                            state["audit"]["registry_id"])
                    else:
                        if args.audit_key_file or any(credential_args):
                            fail("legacy state has no protected audit; initialize protection first")
                        verified = None
                    values = json.loads(args.criterion_scores) if args.criterion_scores else None
                    result = appeals.resolve_appeal(
                        state,args.appeal_id,args.decision,args.reason,
                        True if verified else args.reviewer_confirmed,args.new_score,values)
                    if audited:
                        stored = next(a for a in state["appeals"] if a["appeal_id"]==args.appeal_id)
                        stored["credential_reviewer_id"] = verified["reviewer_id"]
                        stored["reviewer_auth_mode"] = "local_credential"
                        result = dict(stored)
                        result.update(audit_ledger.append(state,key,"resolve",stored))
                    else:
                        result["reviewer_auth_mode"] = "self_declared_not_authenticated"
                    write_state(args.state, state)
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "audit-init":
                    if not Path(args.state).is_file():
                        fail("initialize a learner state before enabling audit protection")
                    registry = reviewer_credentials.read_registry(args.registry)
                    reviewer_credentials._require_admin(registry,args.admin_token_file)
                    if Path(args.audit_key_output).resolve() in {
                            Path(args.state).resolve(),Path(args.registry).resolve()}:
                        fail("audit secret must not overwrite state or reviewer registry")
                    state = read_state(args.state)
                    if state.get("appeals") or "audit" in state or audit_ledger.policy_path(args.state).exists():
                        fail("cannot retroactively authenticate earlier appeal records or replace an audit policy")
                    key = audit_ledger.generate_key_file(args.audit_key_output)
                    result = audit_ledger.initialize(state,key,registry["registry_id"])
                    write_state(args.state,state)
                    audit_ledger.create_policy(args.state,state,key)
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "audit-verify":
                    key = audit_ledger.key_from_file(args.audit_key_file)
                    receipt = (json.loads(Path(args.checkpoint).read_text(encoding="utf-8"))
                               if args.checkpoint else None)
                    result = audit_ledger.verify(read_state(args.state),key,receipt,
                                                 state_path=args.state)
                    print(json.dumps(result, ensure_ascii=True))
                elif args.cmd == "audit-checkpoint":
                    state = read_state(args.state)
                    key = audit_ledger.key_from_file(args.audit_key_file)
                    if Path(args.output).resolve() in {
                            Path(args.state).resolve(),Path(args.audit_key_file).resolve()}:
                        fail("checkpoint must not replace state or audit secret")
                    audit_ledger.verify(state,key,state_path=args.state)
                    receipt = audit_ledger.receipt_for(state,key)
                    reviewer_credentials._new_file(
                        args.output,(json.dumps(receipt,sort_keys=True,indent=2)+"\n").encode())
                    print(json.dumps({"checkpoint_created":str(args.output),
                                      "entries":receipt["entries"],
                                      "head":receipt["head"]},ensure_ascii=True))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
