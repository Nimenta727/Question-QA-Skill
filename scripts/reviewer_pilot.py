#!/usr/bin/env python3
"""Compare independently frozen ordinal reviewer scores to a reference rubric.

This module NEVER decides that the expert reference is correct. Reference
scoring and participant consent are self-declared, not authenticated. Output
contains aggregate metrics only, with resampling at the case level.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys
from pathlib import Path

try:
    from . import reviewer_study, reviewer_trial
except ImportError:
    import reviewer_study
    import reviewer_trial


def _load(path):
    f=Path(path)
    if f.is_symlink() or not f.is_file() or f.stat().st_size>2000000:
        raise ValueError("invalid, symlinked or oversized private study input")
    return json.loads(f.read_text(encoding="utf-8"))


def _digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=True,sort_keys=True,
                                    allow_nan=False).encode("utf-8")).hexdigest()


def _scores(packet,expected,slot):
    if (not isinstance(packet,dict) or set(packet)!={"reviewer_slot","cases"}
            or packet["reviewer_slot"]!=slot or not isinstance(packet["cases"],list)):
        raise ValueError("invalid "+slot+" first-round packet")
    result={}
    for item in packet["cases"]:
        if not isinstance(item,dict) or set(item)!={"case_id","scores"}:
            raise ValueError("first-round item has extra or missing fields")
        case=item["case_id"]
        if not isinstance(case,str) or case not in expected or case in result:
            raise ValueError("unknown or duplicated case in "+slot+" packet")
        scores=reviewer_study.normalized_scores(item["scores"])
        if len(scores)!=expected[case]:
            raise ValueError("first-round rubric length mismatch")
        result[case]=scores
    if set(result)!=set(expected):
        raise ValueError("incomplete first-round packet")
    return result


def _reference(packet,expected):
    if (not isinstance(packet,dict) or set(packet)!={"expert_reference_self_declared","cases"}
            or packet["expert_reference_self_declared"] is not True
            or not isinstance(packet["cases"],list)):
        raise ValueError("independent expert reference must be explicitly self-declared")
    result={}
    for item in packet["cases"]:
        if not isinstance(item,dict) or set(item)!={"case_id","scores"}:
            raise ValueError("expert reference item requires case_id and scores")
        case=item["case_id"]
        if not isinstance(case,str) or case not in expected or case in result:
            raise ValueError("unknown or duplicate expert reference case")
        scores=reviewer_study.normalized_scores(item["scores"])
        if len(scores)!=expected[case]:
            raise ValueError("expert reference rubric length mismatch")
        result[case]=scores
    if set(result)!=set(expected):
        raise ValueError("incomplete expert reference")
    return result


def _summary(cases):
    # Each tuple contains A, B, and expert-reference rating arrays.
    total=sum(len(a) for a,b,e in cases)
    correct_a=sum(x==z for a,b,e in cases for x,z in zip(a,e))
    correct_b=sum(x==z for a,b,e in cases for x,z in zip(b,e))
    exact_both=sum(x==y for a,b,e in cases for x,y in zip(a,b))
    consensus_ok=sum(x==y==z for a,b,e in cases for x,y,z in zip(a,b,e))
    mae_a=sum(abs(x-z) for a,b,e in cases for x,z in zip(a,e))/total
    mae_b=sum(abs(x-z) for a,b,e in cases for x,z in zip(b,e))/total
    return {
        "cases":len(cases),"rubric_decisions":total,
        "reviewer_a_expert_reference_agreement":round(correct_a/total,5),
        "reviewer_b_expert_reference_agreement":round(correct_b/total,5),
        "reviewer_a_reference_mae":round(mae_a,5),
        "reviewer_b_reference_mae":round(mae_b,5),
        "reviewer_interagreement":round(exact_both/total,5),
        "consensus_coverage":round(exact_both/total,5),
        "consensus_given_expert_reference_agreement":
            round(consensus_ok/exact_both,5) if exact_both else None,
        "consensus_agreed_but_reference_disagreed":exact_both-consensus_ok,
        "difference_a_minus_b_reference_agreement":
            round((correct_a-correct_b)/total,5)
    }


def _interval(cases,draws,seed):
    if type(draws) is not int or not 0<=draws<=1000:
        raise ValueError("bootstraps must be 0..1000")
    if len(cases)<5 or draws==0:
        return None
    rng=random.Random(seed)
    n=len(cases)
    values=sorted(_summary([cases[rng.randrange(n)] for _ in range(n)])
                  ["difference_a_minus_b_reference_agreement"] for _ in range(draws))
    return [values[int(.025*(draws-1))],values[int(.975*(draws-1))]]


def evaluate(manifest,frozen,packet_a,packet_b,reference,bootstraps=200,seed=2029):
    if (not isinstance(frozen,dict) or frozen.get("stage")!="first_round_frozen"
            or frozen.get("cases") is None
            or not isinstance(frozen.get("first_round_packet_sha256"),dict)
            or set(frozen["first_round_packet_sha256"])!={"A","B"}):
        raise ValueError("first-round frozen report missing")
    cases=reviewer_trial.validate_plan({
        "study_type":manifest.get("study_type"),
        "authorized":manifest.get("authorization_self_declared"),
        "rubric_frozen":manifest.get("rubric_frozen_self_declared"),
        "case_ids_and_criterion_counts":manifest.get("case_ids_and_criterion_counts")
    })
    if frozen["cases"]!=len(cases) or frozen.get("study_type_self_declared")!=manifest["study_type"]:
        raise ValueError("frozen report is not bound to the registered cases/type")
    for slot,packet in (("A",packet_a),("B",packet_b)):
        if not isinstance(frozen["first_round_packet_sha256"][slot],str) or not (
                hashlib.compare_digest if hasattr(hashlib,"compare_digest") else __import__("hmac").compare_digest
            )(_digest(packet),frozen["first_round_packet_sha256"][slot]):
            raise ValueError("first-round packet hash changed after freeze")
    expected={item["case_id"]:item["criteria"] for item in cases}
    a,b=_scores(packet_a,expected,"A"),_scores(packet_b,expected,"B")
    expert=_reference(reference,expected)
    rows=[(a[key],b[key],expert[key]) for key in sorted(expected)]
    main=_summary(rows)
    return {
        "study_type_self_declared":manifest["study_type"],
        "genuine_human_review_verified":False,
        "expert_correctness_independently_verified":False,
        "reviewer_blinding_verified":False,
        "metrics":main,
        "case_bootstrap_a_minus_b_reference_agreement_ci95":
            _interval(rows,bootstraps,seed),
        "expert_reference_packet_sha256":_digest(reference),
        "caution":("Agreement with the supplied expert reference is NOT an "
                   "independently proven correct grade. Consent, assessor competence, "
                   "review independence and study ethics need real institutional review. "
                   "Raw answers and participant identifiers are never exported.")
    }


def main(argv=None):
    p=argparse.ArgumentParser(description="Compare frozen grades to separate expert reference")
    p.add_argument("--manifest",required=True)
    p.add_argument("--frozen",required=True)
    p.add_argument("--review-a",required=True)
    p.add_argument("--review-b",required=True)
    p.add_argument("--expert",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--bootstraps",type=int,default=200)
    p.add_argument("--seed",type=int,default=2029)
    args=p.parse_args(argv)
    try:
        summary=evaluate(_load(args.manifest),_load(args.frozen),
                         _load(args.review_a),_load(args.review_b),
                         _load(args.expert),args.bootstraps,args.seed)
        # Distinct nonoverwriting private output; never print case-level data.
        reviewer_trial._write_new(args.output,summary)
        print(json.dumps({"aggregate_created":args.output,
                          "cases":summary["metrics"]["cases"],
                          "human_study_verified":False},ensure_ascii=True))
        return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
