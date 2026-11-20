#!/usr/bin/env python3
"""Aggregate-only ordinal inter-rater agreement; not score validity."""
import argparse
import json
import math
import random
import sys
from pathlib import Path

SCORES=(0.0,0.5,1.0)


def normalized_scores(values):
    if (not isinstance(values,list) or not 1<=len(values)<=25
            or any(type(v) not in (int,float) or not math.isfinite(v)
                   or v not in SCORES for v in values)):
        raise ValueError("rubric needs 1..25 scores of 0/0.5/1")
    return [float(x) for x in values]


def read_cases(payload):
    if not isinstance(payload,dict) or set(payload)!={"study_type","cases"}:
        raise ValueError("input must have study_type and cases")
    if payload["study_type"] not in ("synthetic","real_private_self_declared"):
        raise ValueError("invalid study_type")
    rows=payload["cases"]
    if not isinstance(rows,list) or not 1<=len(rows)<=10000:
        raise ValueError("require 1..10000 cases")
    seen=set()
    cases=[]
    for row in rows:
        if (not isinstance(row,dict)
                or not {"case_id","scores_a","scores_b"}.issubset(row)
                or set(row)-{"case_id","scores_a","scores_b","final"}):
            raise ValueError("case requires case_id, scores_a, scores_b, optional final")
        identifier=row["case_id"]
        if not isinstance(identifier,str) or not identifier or len(identifier)>100 or identifier in seen:
            raise ValueError("case_id must be unique opaque <=100 char text")
        seen.add(identifier)
        a,b=normalized_scores(row["scores_a"]),normalized_scores(row["scores_b"])
        if len(a)!=len(b):
            raise ValueError("reviewer rubric lengths differ")
        final=None
        if "final" in row:
            final=normalized_scores(row["final"])
            if len(final)!=len(a) or any(x==y and z!=x for x,y,z in zip(a,b,final)):
                raise ValueError("arbitration must preserve agreed criteria and rubric length")
        cases.append((a,b,final))
    return cases


def kappa(pairs):
    n=len(pairs)
    grid=[[0]*3 for _ in range(3)]
    for a,b in pairs:
        grid[SCORES.index(a)][SCORES.index(b)]+=1
    row=[sum(r) for r in grid]
    col=[sum(grid[i][j] for i in range(3)) for j in range(3)]
    observed=sum(grid[i][j]*((i-j)/2)**2 for i in range(3) for j in range(3))/n
    expected=sum(row[i]*col[j]*((i-j)/2)**2 for i in range(3) for j in range(3))/(n*n)
    return round(1-observed/expected,5) if expected else None


def summarize(cases):
    pairs=[(x,y) for a,b,_ in cases for x,y in zip(a,b)]
    total=len(pairs)
    agree=sum(a==b for a,b in pairs)
    dispute_cases=sum(any(x!=y for x,y in zip(a,b)) for a,b,_ in cases)
    unresolved=sum(final is None and any(x!=y for x,y in zip(a,b))
                   for a,b,final in cases)
    return {
        "cases":len(cases),"rubric_decisions":total,
        "exact_agreement":round(agree/total,5),
        "complete_case_agreement":round(sum(all(x==y for x,y in zip(a,b))
            for a,b,_ in cases)/len(cases),5),
        "quadratic_weighted_kappa":kappa(pairs),
        "mean_absolute_score_gap":round(sum(abs(x-y) for x,y in pairs)/total,5),
        "disputed_rubric_decisions":total-agree,
        "disputed_cases":dispute_cases,
        "unresolved_cases":unresolved
    }


def interval(cases,draws=200,seed=2027):
    if not 0<=draws<=1000:
        raise ValueError("bootstraps must be 0..1000")
    if len(cases)<5 or not draws:
        return None
    rand=random.Random(seed)
    n=len(cases)
    scores=sorted(summarize([cases[rand.randrange(n)] for _ in range(n)])
                  ["exact_agreement"] for _ in range(draws))
    return [scores[int(.025*(draws-1))],scores[int(.975*(draws-1))]]


def report(payload,draws=200,seed=2027):
    cases=read_cases(payload)
    return {
        "study_type_self_declared":payload["study_type"],
        "human_participation_verified":False,
        "reviewer_independence_verified":False,
        "validity_or_correctness_established":False,
        "assessment":summarize(cases),
        "case_cluster_bootstrap_exact_agreement_ci95":interval(cases,draws,seed),
        "caution":("Agreement is not correctness or fairness; Kappa may be undefined. "
                   "No case IDs, review packets, student text or personal data are exported.")
    }


def main(argv=None):
    p=argparse.ArgumentParser(description="Aggregate-only paired rubric agreement")
    p.add_argument("--input",required=True)
    p.add_argument("--output")
    p.add_argument("--bootstraps",type=int,default=200)
    p.add_argument("--seed",type=int,default=2027)
    args=p.parse_args(argv)
    try:
        source=Path(args.input)
        if source.stat().st_size>2000000:
            raise ValueError("private input too large")
        payload=json.loads(source.read_text(encoding="utf-8"))
        result=json.dumps(report(payload,args.bootstraps,args.seed),indent=2,ensure_ascii=True)+"\n"
        if args.output:
            dest=Path(args.output)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(result,encoding="utf-8")
            print(json.dumps({"aggregate_created":str(dest)}))
        else:
            print(result)
        return 0
    except (ValueError,OSError,TypeError,json.JSONDecodeError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
