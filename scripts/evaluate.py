#!/usr/bin/env python3
"""Leakage-aware, zero-dependency offline evaluation of formative diagnosis.

Historical logged data can test next-response prediction and overconfident flags,
NOT counterfactual effectiveness of adaptive item choice or latent mastery truth.
Never upload individual learners' records; output only aggregate summaries.
"""
import argparse
import csv
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from .diagnosis import estimate
except ImportError:
    from diagnosis import estimate

LEVELS = {"recall", "understand", "apply", "analyze", "transfer"}
KINDS = {"single", "short", "manual"}


def _error(message):
    raise ValueError(message)


def _flag(value):
    return str(value).strip().lower() in ("1", "yes", "y", "true", "t")


def _timestamp(raw):
    raw = str(raw or "").strip()
    if not raw:
        return None
    try:
        if raw.replace(".", "", 1).isdigit():
            number = float(raw)
            if number > 1e11:
                number /= 1000
            return datetime.fromtimestamp(number, timezone.utc).isoformat()
        date = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return date.astimezone(timezone.utc).isoformat()
    except (ValueError, OverflowError, OSError):
        _error("invalid answered_at value")


def _normalize(raw, schema, index):
    if schema == "assistments09":
        learner = raw.get("user_id", "")
        concept = raw.get("skill_id", "") or raw.get("skill_name", "")
        item = raw.get("problem_id", "") or raw.get("assistment_id", "")
        order = raw.get("order_id", "")
        # Historical ASSISTments 'correct' can include help use, and the
        # original dataset includes duplicate records for multiple skills.
        if raw.get("answer_type", "") == "open_response":
            return None
        if raw.get("original", "1") == "0":
            return None
        family = raw.get("template_id", "") or item
        kind = ("single" if raw.get("answer_type") == "choose_1"
                else "short")
        level = "understand"  # UNKNOWN actual cognitive level, not validated.
        hint = _flag(raw.get("hint_count", "0")) if raw.get("hint_count", "") in ("0","1") else False
        if raw.get("hint_count", "").strip().isdigit():
            hint = int(raw["hint_count"]) > 0
        stamp = None  # order_id is a sequence, not an actual calendar date.
    else:
        learner = raw.get("learner_id", "")
        concept = raw.get("concept_id", "")
        item = raw.get("item_id", "")
        order = raw.get("order", "") or str(index + 1)
        family = raw.get("family", "") or item
        kind = raw.get("type", "") or "short"
        level = raw.get("level", "") or "understand"
        hint = _flag(raw.get("hint_used", ""))
        stamp = _timestamp(raw.get("answered_at", ""))
    learner, concept, item = (str(x).strip() for x in (learner, concept, item))
    if not learner or not concept or not item:
        _error("row %d requires learner/concept/item identifiers" % (index + 2))
    correct = str(raw.get("correct", "")).strip()
    if correct not in ("0", "1"):
        _error("row %d correct must be 0/1" % (index + 2))
    if level not in LEVELS or kind not in KINDS:
        _error("row %d invalid level/type" % (index + 2))
    if not order:
        _error("row %d missing chronological order" % (index + 2))
    try:
        sequence = float(order)
        if not math.isfinite(sequence):
            raise ValueError("nonfinite")
    except ValueError:
        _error("row %d invalid chronological order" % (index + 2))
    difficulty = str(raw.get("difficulty", "2")).strip() or "2"
    if difficulty not in ("1", "2", "3"):
        _error("row %d difficulty must be 1/2/3" % (index + 2))
    confidence = str(raw.get("confidence", "none")).strip() or "none"
    if confidence not in ("none", "sure", "unsure", "guess"):
        _error("row %d invalid confidence" % (index + 2))
    return {"learner": learner, "concept": concept, "id": item,
            "family": family, "correct": int(correct),
            "order": sequence, "stamp": stamp, "row": index,
            "level": level, "type": kind, "difficulty": int(difficulty),
            "confidence": confidence, "hint_used": hint}


def load_csv(path, schema="generic", max_rows=1000000):
    if schema not in ("generic", "assistments09"):
        _error("unknown input format")
    rows, skipped, deduped = [], 0, 0
    seen = {}
    with open(path, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        expected = ({"learner_id", "concept_id", "item_id", "correct"}
                    if schema == "generic" else
                    {"user_id", "skill_id", "problem_id", "order_id", "correct"})
        if not reader.fieldnames or not expected.issubset(reader.fieldnames):
            _error("CSV missing required columns: " + ",".join(sorted(expected)))
        for i, source in enumerate(reader):
            if i >= max_rows:
                _error("max-rows exceeded; use an explicitly bounded extract")
            item = _normalize(source, schema, i)
            if item is None:
                skipped += 1
                continue
            # Same learner+event+concept+order is duplicated in some public
            # exports; any contradictory target is a hard error.
            key = (item["learner"], item["concept"], item["id"], item["order"])
            if key in seen:
                if seen[key] != item["correct"]:
                    _error("conflicting duplicate response in input")
                deduped += 1
                continue
            seen[key] = item["correct"]
            rows.append(item)
    if not rows:
        _error("no eligible response rows")
    # Input chronological order within a learner is the single source of truth;
    # timestamp is used only for *day* grouping, not sequencing.
    rows.sort(key=lambda e: (e["learner"], e["order"], e["row"]))
    for e in rows:
        e["at"] = e["stamp"] or "2020-01-01T00:00:00+00:00"
        e["score"] = float(e["correct"])
    return rows, {"rows": len(rows), "skipped": skipped, "duplicates": deduped,
                  "has_calendar_dates": any(e["stamp"] for e in rows),
                  "learners": len({e["learner"] for e in rows}),
                  "concepts": len({e["concept"] for e in rows})}


def bucket(learner, seed):
    raw = ("%d:%s" % (seed, learner)).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:12], 16) % 10000


def split_rows(rows, seed=2026):
    partitions = {"train": [], "validation": [], "test": []}
    for event in rows:
        n = bucket(event["learner"], seed)
        split = "train" if n < 6000 else "validation" if n < 8000 else "test"
        partitions[split].append(event)
    seen = {part: {e["learner"] for e in events}
            for part, events in partitions.items()}
    if not all(seen.values()):
        _error("need learners represented in train, validation and test; add more records")
    if seen["train"] & seen["test"] or seen["train"] & seen["validation"] or seen["test"] & seen["validation"]:
        _error("learner leakage across splits")
    return partitions


def priors(train):
    counts = defaultdict(lambda: [0, 0])
    global_count = [0, 0]
    for e in train:
        counts[e["concept"]][0] += e["correct"]
        counts[e["concept"]][1] += 1
        global_count[0] += e["correct"]
        global_count[1] += 1
    global_rate = (global_count[0] + 1) / (global_count[1] + 2)
    by_concept = {c: (success + global_rate * 10) / (count + 10)
                  for c, (success, count) in counts.items()}
    return global_rate, by_concept


def replay(rows, global_rate, concept_priors, min_history=2):
    """Test time: every prediction sees only THIS learner's earlier responses."""
    by_learner = defaultdict(list)
    for e in rows:
        by_learner[e["learner"]].append(e)
    predicted = []
    for learner, events in by_learner.items():
        seen = defaultdict(list)
        for current in sorted(events, key=lambda e: (e["order"], e["row"])):
            concept = current["concept"]
            history = seen[concept]
            if len(history) >= min_history:
                prior = concept_priors.get(concept, global_rate)
                local = (sum(e["correct"] for e in history) + 4 * prior) / (len(history) + 4)
                descriptor = estimate(history)
                predicted.append({
                    "learner": learner, "target": current["correct"],
                    "global": global_rate, "concept_prior": prior,
                    "local_history": local, "diagnostic_index": descriptor["rate"],
                    "diagnostic_label": descriptor["label"],
                    "n_history": len(history),
                    "concept": concept,
                })
            # Absolutely append AFTER generating the prediction: causal replay.
            seen[concept].append(current)
    return predicted


def auc(observations):
    """Mann-Whitney rank AUC with tie-aware midranks, no sklearn dependency."""
    values = sorted(observations, key=lambda pair: pair[0])
    pos = sum(int(y) for _, y in values)
    neg = len(values) - pos
    if not pos or not neg:
        return None
    wins = 0.0
    for i, (score, label) in enumerate(values):
        pass
    count_neg = 0
    i = 0
    while i < len(values):
        j = i
        while j < len(values) and values[j][0] == values[i][0]:
            j += 1
        group = values[i:j]
        positive = sum(int(y) for _, y in group)
        negative = len(group) - positive
        wins += positive * (count_neg + 0.5 * negative)
        count_neg += negative
        i = j
    return wins / (pos * neg)


def metric(rows, key, probability=True):
    if not rows:
        return None
    pairs = [(r[key], r["target"]) for r in rows]
    result = {"n": len(rows), "auc": auc(pairs)}
    if probability:
        result["brier"] = sum((p-y)**2 for p, y in pairs) / len(pairs)
        result["log_loss"] = -sum(y*math.log(max(1e-12, p)) +
                                  (1-y)*math.log(max(1e-12, 1-p))
                                  for p, y in pairs) / len(pairs)
        result["accuracy_at_0_5"] = sum(int((p >= 0.5) == bool(y))
                                           for p, y in pairs) / len(pairs)
        bins = defaultdict(list)
        for p, y in pairs:
            bins[min(9, int(p * 10))].append((p, y))
        result["ece_10bin"] = sum(
            len(bin_rows) / len(rows) *
            abs(sum(p for p,_ in bin_rows) / len(bin_rows) -
                sum(y for _,y in bin_rows) / len(bin_rows))
            for bin_rows in bins.values())
    return result


def wilson(errors, n, z=1.96):
    if not n:
        return None
    p = errors/n
    denom = 1 + z*z/n
    center = (p+z*z/(2*n))/denom
    radius = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [max(0, center-radius), min(1, center+radius)]


def diagnostics(rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["diagnostic_label"]].append(r)
    out = {}
    for label in ("untested", "insufficient_evidence", "developing",
                  "needs_review", "tentatively_strong"):
        subset = grouped[label]
        n = len(subset)
        errors = sum(1-r["target"] for r in subset)
        out[label] = {
            "n": n, "learners": len({e["learner"] for e in subset}),
            "next_response_error_rate": errors/n if n else None,
            "error_rate_wilson_95": wilson(errors, n)}
    return out


def bootstrap_auc(rows, key, n_boot=200, seed=2026):
    groups = defaultdict(list)
    for row in rows:
        groups[row["learner"]].append(row)
    learner_ids = sorted(groups)
    if len(learner_ids) < 3 or not rows or n_boot < 2:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(n_boot):
        batch = [row for learner in rng.choices(learner_ids, k=len(learner_ids))
                 for row in groups[learner]]
        value = auc([(r[key], r["target"]) for r in batch])
        if value is not None:
            values.append(value)
    if len(values) < 5:
        return None
    values.sort()
    return [values[int(0.025*(len(values)-1))],
            values[int(0.975*(len(values)-1))]]


def evaluate(rows, seed=2026, min_history=2, bootstraps=200):
    if min_history < 1 or bootstraps < 0 or bootstraps > 2000:
        _error("min-history >=1 and bootstraps 0..2000 required")
    parts = split_rows(rows, seed)
    global_rate, concepts = priors(parts["train"])
    result = {"protocol": "heldout-learners+causal-next-response",
              "seed": seed, "min_history": min_history,
              "learner_counts": {k: len({e["learner"] for e in v})
                                 for k,v in parts.items()},
              "row_counts": {k: len(v) for k,v in parts.items()},
              "methodology": "No training labels from validation/test; streaming per-learner history only; no item selection causal claim"}
    for name in ("validation", "test"):
        predictions = replay(parts[name], global_rate, concepts, min_history)
        metrics = {key: metric(predictions, key, probability=key!="diagnostic_index")
                   for key in ("global", "concept_prior", "local_history", "diagnostic_index")}
        labels = diagnostics(predictions)
        result[name] = {"eligible_predictions": len(predictions),
                        "eligible_learners": len({r["learner"] for r in predictions}),
                        "metrics": metrics, "diagnostic_labels": labels,
                        "index_auc_95ci_learner_bootstrap":
                            bootstrap_auc(predictions, "diagnostic_index",
                                          bootstraps, seed)}
    test = result["test"]
    strong = test["diagnostic_labels"]["tentatively_strong"]
    result["readiness"] = {
        "can_assess_strong_label": strong["n"] >= 50 and strong["learners"] >= 20,
        "sufficient_test_predictions": test["eligible_predictions"] >= 1000
                                       and test["eligible_learners"] >= 100,
        "bkt_irt_decision": "do_not_add_yet",
        "reason": ("Exploratory observation only; latent mastery labels and "
                   "item selection counterfactuals are not available. "
                   "Require independent validation and item calibration before BKT/IRT.")
    }
    result["limitations"] = [
        "Next-response error is NOT a ground-truth mastery classification.",
        "Historical exposures cannot estimate adaptive question selection effectiveness.",
        "Diagnostic index is NOT calibrated probability; report only AUC for it.",
        "Student-disjoint partitions use SHA256, but per-student history is legitimately updated after each prediction.",
        "A single cognitive level or absent dates can prevent all strong decisions.",
        "This result is specific to the input sample, not a population guarantee."
    ]
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline formative diagnosis benchmark")
    p.add_argument("input", help="local CSV (never uploads data)")
    p.add_argument("--format", choices=("generic", "assistments09"), default="generic")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--min-history", type=int, default=2)
    p.add_argument("--max-rows", type=int, default=1000000)
    p.add_argument("--bootstraps", type=int, default=200)
    p.add_argument("--output", help="optional aggregate JSON path")
    args = p.parse_args(argv)
    try:
        rows, audit = load_csv(args.input, args.format, args.max_rows)
        report = evaluate(rows, args.seed, args.min_history, args.bootstraps)
        report["input_audit"] = audit
        text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        else:
            print(text)
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
