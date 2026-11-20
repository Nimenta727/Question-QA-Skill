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
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

LEVELS = {"recall", "understand", "apply", "analyze", "transfer"}
TYPES = {"single", "short", "manual"}
CONFIDENCES = {"sure", "unsure", "guess", "none"}
SPACING_DAYS = (1, 3, 7, 14, 30)
SCHEMA = 1


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
        elif not isinstance(q.get("rubric"), list) or not q["rubric"] or not all(
                isinstance(x, str) and x.strip() for x in q["rubric"]):
            fail("%s manual response requires rubric criteria" % q["id"])
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
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".qa-", suffix=".json", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(state, out, ensure_ascii=False, indent=2)
            out.write("\n")
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def evidence(history):
    out = defaultdict(list)
    for h in history:
        out[(h["concept"], h["level"])].append(h)
    return out


def estimate(events):
    if not events:
        return {"label": "untested", "rate": None, "count": 0, "unique_items": 0}
    # Beta(1,1) smoothed descriptive signal, not IRT / BKT.
    score = sum(x["score"] for x in events)
    rate = (1.0 + score) / (2.0 + len(events))
    unique = len({x["id"] for x in events})
    if len(events) < 3 or unique < 2:
        label = "insufficient_evidence"
    elif rate >= 0.72:
        label = "tentatively_strong"
    elif rate <= 0.45:
        label = "needs_review"
    else:
        label = "developing"
    return {"label": label, "rate": round(rate, 3),
            "count": len(events), "unique_items": unique}


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


def select_item(items, history, mode="quick", now=None):
    now = now or utc_now()
    grouped = evidence(history)
    seen = {h["id"] for h in history}
    recent = {h["id"] for h in history[-4:]}
    fresh = [q for q in items if q["id"] not in seen]
    candidates = fresh or [q for q in items if q["id"] not in recent] or list(items)

    def priority(q):
        key = (q["concept"], q["level"])
        events = grouped[key]
        avg = sum(x["score"] for x in events) / len(events) if events else None
        target = 2 if avg is None else (3 if avg >= 0.75 else 1 if avg < 0.45 else 2)
        all_concept = [x for x in history if x["concept"] == q["concept"]]
        empty_bonus = 7 if not all_concept else (3 if not events else 0)
        need_bonus = 5 if events and avg < 0.6 else 0
        review_date = due_date(events)
        due_bonus = 4 if review_date and review_date <= now.date().isoformat() else 0
        depth = 2 if mode == "deep" and q["level"] in {"analyze", "transfer", "apply"} else 0
        quick = 1 if mode == "quick" and q["level"] in {"recall", "understand", "apply"} else 0
        return (empty_bonus + need_bonus + due_bonus + depth + quick
                - abs(q["difficulty"] - target) * 1.25
                - (2 if q["id"] in recent else 0))
    return sorted(candidates, key=lambda q: (-priority(q), q["id"]))[0]


def safe_prompt(q):
    data = {"id": q["id"], "question": q["stem"], "type": q["type"]}
    if q["type"] == "single":
        data["options"] = dict(zip("ABCD", q["options"]))
    return data


def grade(q, response, manual_score=None, reason=None):
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
    return float(normalize(response) in valid), "exact_key"


def answer_key(q):
    if q["type"] == "single":
        return q["answer"] + ": " + q["options"]["ABCD".index(q["answer"])]
    if q["type"] == "short":
        return q["answer"]
    return "See rubric; no automatic model grade"


def handle_next(args):
    bank, digest = read_bank(args.bank)
    state = read_state(args.state)
    if state.get("pending"):
        p = state["pending"]
        if p.get("bank_digest") != digest:
            fail("bank changed while a question was pending; restore bank or use --reset-pending")
        q = next((item for item in bank["items"] if item["id"] == p["id"]), None)
        if q is None:
            fail("pending item not found")
    else:
        q = select_item(bank["items"], state["history"], args.mode)
        state["pending"] = {"id": q["id"], "bank_digest": digest}
        write_state(args.state, state)
    print(json.dumps(safe_prompt(q), ensure_ascii=False))


def handle_answer(args):
    bank, digest = read_bank(args.bank)
    state = read_state(args.state)
    pending = state.get("pending")
    if not pending:
        fail("no pending item; run next first")
    if pending.get("bank_digest") != digest:
        fail("bank changed while a question was pending")
    q = next((i for i in bank["items"] if i["id"] == pending["id"]), None)
    if q is None:
        fail("pending item not found")
    score, method = grade(q, args.response, args.score, args.reason)
    event = {
        "id": q["id"], "concept": q["concept"], "level": q["level"],
        "score": score, "method": method,
        "confidence": args.confidence,
        "at": utc_now().isoformat()
    }
    state["history"].append(event)
    state["pending"] = None
    write_state(args.state, state)
    result = {
        "score": score, "method": method, "expected": answer_key(q),
        "explanation": q["explanation"],
        "concept": q["concept"], "level": q["level"],
        "status": estimate(evidence(state["history"])[(q["concept"], q["level"])]),
        "next_review": due_date(evidence(state["history"])[(q["concept"], q["level"])])
    }
    if q["type"] == "manual":
        result["rubric"] = q["rubric"]
        result["review_reason"] = args.reason
    elif score == 0 and q["type"] == "short":
        result["note"] = "Exact match only. If the response is equivalent, review and add an alias; do not infer a conceptual error."
    print(json.dumps(result, ensure_ascii=False))


def handle_report(args):
    state = read_state(args.state)
    groups = evidence(state["history"])
    rows = []
    for (concept, level), events in sorted(groups.items()):
        rows.append({
            "concept": concept, "level": level,
            **estimate(events), "next_review": due_date(events)
        })
    print(json.dumps({
        "total_answers": len(state["history"]), "pending": bool(state.get("pending")),
        "areas": rows, "caution": "Formative estimates, not calibrated proficiency; untested areas omitted."
    }, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline adaptive QA state / 低成本学习诊断")
    subs = parser.add_subparsers(dest="cmd", required=True)
    p = subs.add_parser("validate")
    p.add_argument("bank")
    p = subs.add_parser("next")
    p.add_argument("bank")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--mode", choices=("quick", "deep"), default="quick")
    p = subs.add_parser("answer")
    p.add_argument("bank")
    p.add_argument("--state", default=".qa-state.json")
    p.add_argument("--response", required=True)
    p.add_argument("--confidence", choices=sorted(CONFIDENCES), default="none")
    p.add_argument("--score", type=float)
    p.add_argument("--reason")
    p = subs.add_parser("report")
    p.add_argument("--state", default=".qa-state.json")
    p = subs.add_parser("reset-pending")
    p.add_argument("--state", default=".qa-state.json")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "validate":
            bank, _ = read_bank(args.bank)
            print(json.dumps({"valid": True, "items": len(bank["items"])}, ensure_ascii=False))
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
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
