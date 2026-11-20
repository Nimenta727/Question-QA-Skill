#!/usr/bin/env python3
"""External replication on ASSISTments 2015 skill-builder practice logs.

Dataset is independently sourced from FORGET-SE. No item identifiers,
cognitive-level labels or real session timestamps are provided by the four-
column ASSIST2015 dataset: do not invent them or claim delayed/mastery validity.
Use locally under ASSISTments terms, never redistribute student rows.
"""
import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

try:
    from . import evaluate as core
    from .evaluate_forget_se import macro_auc_by_concept, bootstrap_delta
except ImportError:
    import evaluate as core
    from evaluate_forget_se import macro_auc_by_concept, bootstrap_delta

REQUIRED = {"user_id", "log_id", "sequence_id", "correct"}


def _stable_sort_key(student, seed):
    return (hashlib.sha256((str(seed)+":"+student).encode("utf-8")).hexdigest(), student)


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as stream:
        csvreader = csv.DictReader(stream)
        if not csvreader.fieldnames or not REQUIRED.issubset(csvreader.fieldnames):
            raise ValueError("ASSISTments 2015 CSV requires four known columns")
        for row in csvreader:
            yield row


def load(path, seed=2026, max_learners=2000, max_rows=1000000):
    """Deterministic learner sample, independent of file row order."""
    if not 30 <= max_learners <= 20000:
        raise ValueError("max-learners must be between 30 and 20000")
    if max_rows < 100 or max_rows > 5000000:
        raise ValueError("max-rows must be between 100 and 5000000")
    students = set()
    count = 0
    for row in _read_csv(path):
        count += 1
        if count > max_rows:
            raise ValueError("input row limit exceeded")
        student = str(row["user_id"] or "").strip()
        if student:
            students.add(student)
    if len(students) < 30:
        raise ValueError("too few independent learners to evaluate")
    picked = set(sorted(students, key=lambda u: _stable_sort_key(u, seed))[:max_learners])
    events = []
    seen = {}
    invalid = 0
    deduplicated = 0
    for index, row in enumerate(_read_csv(path)):
        learner = str(row["user_id"] or "").strip()
        if learner not in picked:
            continue
        concept = str(row["sequence_id"] or "").strip()
        target = str(row["correct"] or "").strip()
        raw_order = str(row["log_id"] or "").strip()
        if not concept or target not in ("0", "1") or not raw_order:
            invalid += 1
            continue
        try:
            order = int(raw_order)
        except ValueError:
            invalid += 1
            continue
        if order < 0:
            invalid += 1
            continue
        key = (learner, order, concept)
        if key in seen:
            if seen[key] != target:
                raise ValueError("conflicting repeated learner/log/sequence record")
            deduplicated += 1
            continue
        seen[key] = target
        # No question IDs exist: all steps in the SAME skill are assigned one
        # UNKNOWN family so repeated observations cannot masquerade as independent
        # items. All events get the same sentinel date; none prove spaced recall.
        synthetic_id = "unknown_item_for_" + concept
        events.append({
            "learner": learner, "concept": concept, "id": synthetic_id,
            "family": synthetic_id, "correct": int(target),
            "score": float(target), "order": float(order), "row": index,
            "level": "understand", "type": "short", "difficulty": 2,
            "confidence": "none", "hint_used": False,
            "stamp": None, "at": "2020-01-01T00:00:00+00:00"})
    events.sort(key=lambda e: (e["learner"], e["order"], e["row"]))
    audit = {
        "source_rows": count, "source_learners": len(students),
        "sample_learners_requested": max_learners,
        "sample_learners_usable": len({x["learner"] for x in events}),
        "sample_rows": len(events), "sample_invalid_rows": invalid,
        "sample_duplicate_rows": deduplicated,
        "skill_count": len({x["concept"] for x in events}),
        "real_timestamps_available": False,
        "item_ids_available": False, "validated_cognitive_levels": False,
        "sample_selection": "lowest SHA256(seed, anonymized learner ID) after full first pass"
    }
    if audit["sample_learners_usable"] < 30:
        raise ValueError("fewer than 30 eligible learners after cleaning")
    return events, audit


def _subset_report(observations, bootstraps, seed):
    keys = ("global", "concept_prior", "local_history", "diagnostic_index")
    within = {key: macro_auc_by_concept(observations, key) for key in keys}
    ci = bootstrap_delta(observations, "diagnostic_index",
                         "local_history", bootstraps, seed, within_concept=True)
    pooled = bootstrap_delta(observations, "diagnostic_index",
                             "local_history", bootstraps, seed+1,
                             within_concept=False)
    return {"within_concept_macro_auc": within,
            "index_minus_local_within_concept_auc_ci95": ci,
            "index_minus_local_pooled_auc_ci95": pooled}


def evaluate(events, audit, seed=2026, min_history=2, bootstraps=150):
    out = core.evaluate(events, seed=seed, min_history=min_history,
                        bootstraps=bootstraps)
    for cohort in ("validation", "test"):
        partitions = core.split_rows(events, seed)
        global_rate, prior = core.priors(partitions["train"])
        observations = core.replay(partitions[cohort], global_rate, prior, min_history)
        out[cohort].update(_subset_report(observations, bootstraps, seed))
    out["dataset"] = "ASSISTments 2015 — 100 Skill Builders"
    out["dataset_source"] = "https://sites.google.com/site/assistmentsdata/datasets/2015-assistments-skill-builder-data"
    out["data_mirror_source"] = "https://github.com/pykt-team/pykt-toolkit"
    out["source_terms"] = "ASSISTments research data use terms; do not redistribute or re-identify"
    out["input_audit"] = audit
    out["experimental_scope"] = (
        "Real independent mathematics practice responses, NOT an independent exam "
        "criterion. 2015 log_id is used as order, not a verified UTC timestamp. "
        "Item identity, family independence and level are unavailable. "
        "The heuristic index cannot pass verified high-order/delayed mastery gates.")
    out["readiness"]["bkt_irt_decision"] = "do_not_add_yet"
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description="ASSIST2015 real learner disjoint next-response benchmark")
    p.add_argument("--input", required=True)
    p.add_argument("--seed",type=int,default=2026)
    p.add_argument("--max-learners",type=int,default=2000)
    p.add_argument("--max-rows",type=int,default=1000000)
    p.add_argument("--min-history",type=int,default=2)
    p.add_argument("--bootstraps",type=int,default=150)
    p.add_argument("--output")
    args=p.parse_args(argv)
    try:
        events,audit=load(args.input,args.seed,args.max_learners,args.max_rows)
        out=evaluate(events,audit,args.seed,args.min_history,args.bootstraps)
        result=json.dumps(out,ensure_ascii=False,indent=2)+"\n"
        if args.output:
            dest=Path(args.output)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(result,encoding="utf-8")
        else:
            print(result)
        return 0
    except (ValueError,OSError,csv.Error) as err:
        print("error: "+str(err),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
