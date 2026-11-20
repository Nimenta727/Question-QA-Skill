#!/usr/bin/env python3
"""External-criterion test on FORGET-SE: weekly responses -> independent exam.

FORGET-SE is a separately licensed, de-identified public research dataset (CC BY 4.0).
Inputs are downloaded/kept outside the repo. This script outputs aggregates only.
No claim is made that final-exam correctness is ground-truth latent mastery.
"""
import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

try:
    from .diagnosis import estimate
    from .evaluate import auc, bucket, metric, wilson
except ImportError:
    from diagnosis import estimate
    from evaluate import auc, bucket, metric, wilson

FIELDS = ["KC%d" % i for i in range(1, 11)]


def _float(raw):
    try:
        x = float(str(raw).strip())
    except (ValueError, TypeError):
        raise ValueError("invalid score")
    if not math.isfinite(x) or not 0 <= x <= 1:
        raise ValueError("score outside [0,1]")
    return x


def load(weekly_path, exam_path):
    """Treat log_id as an ORDER KEY only: documented anonymization is not real date."""
    quiz = defaultdict(list)
    counts = {"weekly_rows": 0, "exam_rows": 0, "partial_weekly_scores": 0,
              "duplicate_weekly": 0}
    seen = {}
    with open(weekly_path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        if not rd.fieldnames or not set(["user_id", "qid", "sequence_id", "log_id", "correct"]).issubset(rd.fieldnames):
            raise ValueError("FORGET-SE weekly CSV headers are invalid")
        for n, row in enumerate(rd):
            learner = row["user_id"].strip()
            concept = row["sequence_id"].strip()
            item = row["qid"].strip()
            if not learner or not item or not concept or not concept.isdigit() or not 1 <= int(concept) <= 10:
                raise ValueError("invalid IDs at weekly record %d" % n)
            score = _float(row["correct"])
            if 0 < score < 1:
                counts["partial_weekly_scores"] += 1
            try:
                order = float(row["log_id"])
            except ValueError:
                raise ValueError("invalid log order")
            if not math.isfinite(order):
                raise ValueError("nonfinite order")
            key = (learner, concept, item, order)
            if key in seen:
                if seen[key] != score:
                    raise ValueError("conflicting duplicate weekly score")
                counts["duplicate_weekly"] += 1
                continue
            seen[key] = score
            quiz[(learner, concept)].append({
                "id": item, "family": item, "concept": concept,
                "level": "understand",  # not author-labelled; no higher-order inference
                "score": score, "difficulty": 2, "type": "short",
                "confidence": "none", "hint_used": False,
                "at": "2020-01-01T00:00:00+00:00",  # date intentionally UNKNOWN
                "order": order, "row": n})
            counts["weekly_rows"] += 1
    exam = {}
    conflicted = set()
    identical = 0
    with open(exam_path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        if not rd.fieldnames or not set(["user_id"] + FIELDS).issubset(rd.fieldnames):
            raise ValueError("FORGET-SE exam CSV headers are invalid")
        for row in rd:
            learner = row["user_id"].strip()
            if not learner:
                raise ValueError("exam record with empty learner ID")
            values = {}
            for i, col in enumerate(FIELDS, 1):
                y = row[col].strip()
                if y not in ("0", "1"):
                    raise ValueError("final-exam target must be binary")
                values[str(i)] = int(y)
            if learner in exam:
                if exam[learner] != values:
                    conflicted.add(learner)
                else:
                    identical += 1
            else:
                exam[learner] = values
            counts["exam_rows"] += 1
    # Conflicting anonymized IDs cannot safely link quiz histories to exam
    # outcomes. Exclude every occurrence rather than choosing one by order.
    for learner in conflicted:
        del exam[learner]
    counts["exam_conflicting_ids_excluded"] = len(conflicted)
    counts["exam_identical_duplicate_rows"] = identical
    counts["exam_unique_valid_learners"] = len(exam)
    if not quiz or not exam:
        raise ValueError("both weekly and exam data are required")
    for key in quiz:
        quiz[key].sort(key=lambda r: (r["order"], r["row"]))
    counts["matched_learners"] = len({learner for learner, _ in quiz} & set(exam))
    counts["matched_learner_skills"] = sum(1 for learner, concept in quiz
                                           if learner in exam and concept in exam[learner])
    return quiz, exam, counts


def baseline_priors(exam, train_learners):
    global_correct = sum(y for u in train_learners for y in exam[u].values())
    total = 10 * len(train_learners)
    global_prior = (1 + global_correct) / (2 + total)
    prior = {}
    for concept in map(str, range(1, 11)):
        successes = sum(exam[u][concept] for u in train_learners)
        prior[concept] = (successes + global_prior * 8) / (len(train_learners) + 8)
    return global_prior, prior


def split_learners(exam, seed):
    result = {"train": set(), "validation": set(), "test": set()}
    for u in exam:
        part = bucket(u, seed)
        result["train" if part < 6000 else "validation" if part < 8000 else "test"].add(u)
    if not all(result.values()):
        raise ValueError("need sufficient students for three disjoint groups")
    return result


def examine(quiz, exam, users, global_prior, by_skill, min_history):
    preds = []
    for u in sorted(users):
        for concept, y in exam[u].items():
            events = quiz.get((u, concept), [])
            if len(events) < min_history:
                continue
            average_score = sum(e["score"] for e in events)
            recent = events[-3:]
            concept_base = by_skill.get(concept, global_prior)
            d = estimate(events)
            preds.append({
                "learner": u, "target": y, "concept": concept,
                "global": global_prior, "concept_prior": concept_base,
                "quiz_average": (average_score + 4*concept_base) / (len(events)+4),
                "quiz_recent3": (sum(e["score"] for e in recent) +
                                 4*concept_base) / (len(recent)+4),
                "diagnostic_index": d["rate"], "diagnostic_label": d["label"],
                "history_count": len(events)
            })
    return preds


def bootstrap_delta(rows, model_a, model_b, n_boot=250, seed=2026):
    groups = defaultdict(list)
    for row in rows:
        groups[row["learner"]].append(row)
    users = sorted(groups)
    if n_boot < 5 or len(users) < 5:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(n_boot):
        sample = [r for u in rng.choices(users, k=len(users)) for r in groups[u]]
        a = auc([(r[model_a], r["target"]) for r in sample])
        b = auc([(r[model_b], r["target"]) for r in sample])
        if a is not None and b is not None:
            values.append(a-b)
    if len(values) < 5:
        return None
    values.sort()
    return [values[int(0.025*(len(values)-1))],
            values[int(0.975*(len(values)-1))]]


def summarize(predictions, bootstraps, seed):
    models = ["global", "concept_prior", "quiz_average", "quiz_recent3",
              "diagnostic_index"]
    metrics = {name: metric(predictions, name, probability=name!="diagnostic_index")
               for name in models}
    labels = {}
    for label in ("untested", "insufficient_evidence", "needs_review",
                  "developing", "tentatively_strong"):
        selected = [r for r in predictions if r["diagnostic_label"] == label]
        n = len(selected)
        missed = sum(1-r["target"] for r in selected)
        labels[label] = {"count": n, "learners": len({r["learner"] for r in selected}),
                         "exam_error_rate": missed/n if n else None,
                         "error_rate_wilson_95": wilson(missed, n)}
    return {
        "n": len(predictions),
        "learners": len({r["learner"] for r in predictions}),
        "models": metrics, "diagnostic_labels": labels,
        "index_minus_quiz_average_auc_95ci":
            bootstrap_delta(predictions, "diagnostic_index", "quiz_average",
                            bootstraps, seed),
        "index_minus_quiz_recent3_auc_95ci":
            bootstrap_delta(predictions, "diagnostic_index", "quiz_recent3",
                            bootstraps, seed+1)
    }


def evaluate(quiz, exam, counts, seed=2026, min_history=2, bootstraps=250):
    if min_history < 1 or bootstraps < 0 or bootstraps > 2000:
        raise ValueError("invalid evaluation options")
    splits = split_learners(exam, seed)
    global_prior, skill_prior = baseline_priors(exam, splits["train"])
    result = {
        "dataset": "FORGET-SE",
        "dataset_url": "https://github.com/alyssa-sha/FORGET-SE",
        "license": "CC BY 4.0 (upstream)",
        "task": "weekly_quiz_history_to_independent_final_exam_KC_binary",
        "data_counts": counts, "seed": seed, "min_history": min_history,
        "split_learners": {name: len(users) for name, users in splits.items()},
        "leakage_controls": [
            "Exam outcomes from validation/test learners never enter fitted priors",
            "All split membership is by SHA256(student_id, seed), student-disjoint",
            "Exam outcome is only evaluated after summarizing weekly history",
            "No individual student output; no weekly dataset redistributed"
        ]
    }
    for split in ("validation", "test"):
        predictions = examine(quiz, exam, splits[split], global_prior,
                              skill_prior, min_history)
        result[split] = summarize(predictions, bootstraps, seed)
    strong = result["test"]["diagnostic_labels"]["tentatively_strong"]
    result["decision"] = {
        "status": "needs_more_evidence",
        "add_bkt_or_irt": False,
        "can_evaluate_provisional_strong": strong["count"] >= 30,
        "reason": ("FORGET-SE has de-identified chronology, no validated cognitive "
                   "level tags, and no item calibration; final exam tests predictive "
                   "association, not latent mastery or adaptive policy impact.")
    }
    result["interpretation_constraints"] = [
        "The final exam is an external criterion, not a definitive mastery label.",
        "Cognitive levels are unknown and cannot be invented from question IDs.",
        "Anonymized log IDs are order signals only: no delayed-retrieval claim.",
        "Diagnostic index is a descriptive score, not a predicted probability.",
        "The retrospective dataset does not identify adaptive question-policy effects.",
        "Any AUC improvement must be judged against its learner-clustered CI."
    ]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="FORGET-SE external-criterion evaluation")
    parser.add_argument("--weekly", required=True, help="local forget_se.csv")
    parser.add_argument("--exam", required=True, help="local exam.csv")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--min-history", type=int, default=2)
    parser.add_argument("--bootstraps", type=int, default=250)
    parser.add_argument("--output", help="aggregate JSON output")
    args = parser.parse_args(argv)
    try:
        quiz, exam, audit = load(args.weekly, args.exam)
        result = evaluate(quiz, exam, audit, args.seed,
                          args.min_history, args.bootstraps)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            path = Path(args.output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded, encoding="utf-8")
        else:
            print(encoded)
        return 0
    except (ValueError, OSError, csv.Error) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
