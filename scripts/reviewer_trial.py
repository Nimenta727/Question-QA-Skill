#!/usr/bin/env python3
"""Offline planning and round-one freeze for genuinely independent reviewers.

No participant records, actual student responses or reviewer names are loaded.
Authorizations and blind independence are self-declared; the software does
not establish an ethics approval, recruitment or validity of real results.
"""
import argparse
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

try:
    from . import reviewer_study
except ImportError:
    import reviewer_study


def _read(path):
    source=Path(path)
    if source.stat().st_size>1_000_000:
        raise ValueError("private protocol input too large")
    return json.loads(source.read_text(encoding="utf-8"))


def _write_new(path,content):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(str(p),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as out:
            json.dump(content,out,ensure_ascii=False,indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        p.unlink(missing_ok=True)
        raise


def validate_plan(obj):
    if (not isinstance(obj,dict) or set(obj)!={"study_type","authorized",
               "rubric_frozen","case_ids_and_criterion_counts"}):
        raise ValueError("plan must declare study_type, authorized, rubric_frozen, cases")
    if obj["study_type"] not in ("synthetic","authorized_real_self_declared"):
        raise ValueError("invalid study_type")
    if obj["rubric_frozen"] is not True:
        raise ValueError("pre-register and freeze scoring rubric before assigning cases")
    if obj["study_type"]=="authorized_real_self_declared" and obj["authorized"] is not True:
        raise ValueError("real study requires a separate recorded authorization and consent")
    if type(obj["authorized"]) is not bool:
        raise ValueError("authorization must be explicitly true/false")
    cases=obj["case_ids_and_criterion_counts"]
    if not isinstance(cases,list) or not 2<=len(cases)<=1000:
        raise ValueError("2..1000 pseudonymous cases required")
    ids=set()
    for entry in cases:
        if not isinstance(entry,dict) or set(entry)!={"case_id","criteria"}:
            raise ValueError("each case requires only case_id and criteria count")
        ident=entry["case_id"]
        n=entry["criteria"]
        if (not isinstance(ident,str) or not 2<=len(ident)<=80 or
                "\n" in ident or "\r" in ident or ident in ids
                or type(n) is not int or not 1<=n<=25):
            raise ValueError("invalid/duplicate pseudonymous case or criterion count")
        ids.add(ident)
    return cases


def prepare(plan,output_dir):
    cases=validate_plan(plan)
    folder=Path(output_dir)
    folder.mkdir(parents=True,exist_ok=False,mode=0o700)
    manifest={"format":1,"stage":"prepared","study_type":plan["study_type"],
              "authorization_self_declared":plan["authorized"],
              "rubric_frozen_self_declared":True,
              "case_ids_and_criterion_counts":cases,
              "notice":"Private participant IDs; do not publish. Blindness unverified."}
    _write_new(folder/"private-manifest.json",manifest)
    for slot in ("A","B"):
        order=list(cases)
        secrets.SystemRandom().shuffle(order)
        _write_new(folder/("reviewer-"+slot+"-tasks.json"),
                   {"reviewer_slot":slot,
                    "case_ids_and_criterion_counts":order,
                    "notice":"Task identifiers only. Student answers must be accessed "
                             "privately and independently by each reviewer."})
    return {"prepared":True,"cases":len(cases),
            "study_type_self_declared":plan["study_type"],
            "output_directory":str(folder),
            "human_authorization_verified_by_software":False}


def freeze(manifest,review_a,review_b,bootstraps=200,seed=2028):
    if not isinstance(manifest,dict) or manifest.get("stage")!="prepared":
        raise ValueError("invalid private manifest")
    cases=validate_plan({
        "study_type":manifest.get("study_type"),
        "authorized":manifest.get("authorization_self_declared"),
        "rubric_frozen":manifest.get("rubric_frozen_self_declared"),
        "case_ids_and_criterion_counts":manifest.get("case_ids_and_criterion_counts")})
    expected={x["case_id"]:x["criteria"] for x in cases}
    def rows(packet,slot):
        if (not isinstance(packet,dict) or set(packet)!={"reviewer_slot","cases"}
                or packet["reviewer_slot"]!=slot
                or not isinstance(packet["cases"],list)):
            raise ValueError("invalid independent reviewer "+slot+" file")
        found={}
        for entry in packet["cases"]:
            if not isinstance(entry,dict) or set(entry)!={"case_id","scores"}:
                raise ValueError("round-one review needs case_id and rubric scores only")
            case_id=entry["case_id"]
            if case_id not in expected or case_id in found:
                raise ValueError("review packet has unknown or duplicate cases")
            grades=reviewer_study.normalized_scores(entry["scores"])
            if len(grades)!=expected[case_id]:
                raise ValueError("rubric length does not match pre-registered plan")
            found[case_id]=grades
        if set(found)!=set(expected):
            raise ValueError("missing first-round scores; cannot freeze")
        return found
    a,b=rows(review_a,"A"),rows(review_b,"B")
    payload={"study_type":("synthetic" if manifest["study_type"]=="synthetic"
                           else "real_private_self_declared"),
             "cases":[{"case_id":case_id,"scores_a":a[case_id],"scores_b":b[case_id]}
                      for case_id in sorted(expected)]}
    agg=reviewer_study.report(payload,bootstraps,seed)
    # Hash normalized scores and pseudonymous IDs; never expose raw records.
    checks={
        slot:hashlib.sha256(json.dumps(packet,ensure_ascii=True,sort_keys=True)
                            .encode("utf-8")).hexdigest()
        for slot,packet in (("A",review_a),("B",review_b))}
    return {
        "stage":"first_round_frozen","cases":len(cases),
        "study_type_self_declared":manifest["study_type"],
        "authorization_verified_by_software":False,
        "reviewer_independence_verified_by_software":False,
        "first_round_packet_sha256":checks,
        "agreement":agg["assessment"],
        "case_cluster_bootstrap_exact_agreement_ci95":
            agg["case_cluster_bootstrap_exact_agreement_ci95"],
        "note":("Hashes commit to submitted review packets but do not prove "
                "when reviews were created or that reviewers were blinded. "
                "This is NOT a human study without external participant authorization. "
                "Adjudicate disputes only after first-round freeze. "
                "No case IDs or original student answers are exported.")
    }


def finalize(manifest,round_one,a,b,adjudicator):
    """Validate third-party dispute decisions AFTER frozen first-round packets."""
    if (not isinstance(round_one,dict) or round_one.get("stage")!="first_round_frozen"):
        raise ValueError("first-round freeze record required")
    if (not isinstance(adjudicator,dict) or
            set(adjudicator)!={"adjudicator_id","independent_self_declared","decisions"}
            or not isinstance(adjudicator["adjudicator_id"],str)
            or not 3<=len(adjudicator["adjudicator_id"])<=64
            or adjudicator["independent_self_declared"] is not True):
        raise ValueError("third-party adjudicator identity declaration and decisions required")
    first=freeze(manifest,a,b,bootstraps=0)
    if (first["first_round_packet_sha256"]!=round_one.get("first_round_packet_sha256")
            or first["cases"]!=round_one.get("cases")
            or first["study_type_self_declared"]!=round_one.get("study_type_self_declared")):
        raise ValueError("review packets differ from immutable first-round freeze")
    aa={row["case_id"]:row["scores"] for row in a["cases"]}
    bb={row["case_id"]:row["scores"] for row in b["cases"]}
    expected={(case,i) for case in aa
              for i,(left,right) in enumerate(zip(aa[case],bb[case]))
              if left!=right}
    decision_list=adjudicator["decisions"]
    if not isinstance(decision_list,list):
        raise ValueError("adjudication decisions must be a list")
    chosen={}
    for row in decision_list:
        if (not isinstance(row,dict)
                or set(row)!={"case_id","criterion_index","score","reason_code"}
                or type(row["criterion_index"]) is not int
                or type(row["score"]) not in (int,float)
                or row["score"] not in (0,0.5,1)
                or row["reason_code"] not in (
                    "rubric_clarification","factual_correction",
                    "missing_step","other")):
            raise ValueError("invalid adjudication decision")
        key=(row["case_id"],row["criterion_index"])
        if key not in expected or key in chosen:
            raise ValueError("adjudication must cover only each disputed criterion once")
        chosen[key]=float(row["score"])
    if set(chosen)!=expected:
        raise ValueError("all frozen first-round disagreements require adjudication")
    combined=[]
    chosen_a=chosen_b=compromise=0
    for case in sorted(aa):
        left=aa[case]
        right=bb[case]
        final=[]
        for i,(x,y) in enumerate(zip(left,right)):
            if x==y:
                final.append(x)
                continue
            score=chosen[(case,i)]
            final.append(score)
            chosen_a+=score==x
            chosen_b+=score==y
            compromise+=score not in (x,y)
        combined.append({"case_id":case,"scores_a":left,
                         "scores_b":right,"final":final})
    audited=reviewer_study.read_cases({
        "study_type":"synthetic" if manifest["study_type"]=="synthetic"
                     else "real_private_self_declared",
        "cases":combined})
    stats=reviewer_study.summarize(audited)
    if stats["unresolved_cases"]!=0:
        raise ValueError("unresolved disagreements remain after adjudication")
    result={
        "stage":"adjudication_complete",
        "study_type_self_declared":manifest["study_type"],
        "cases":len(combined),"disputed_criteria_adjudicated":len(chosen),
        "decisions_matching_A":chosen_a,"decisions_matching_B":chosen_b,
        "decisions_other_supported_value":compromise,
        "unresolved_cases":0,
        "first_round_packet_sha256":first["first_round_packet_sha256"],
        "adjudication_packet_sha256":hashlib.sha256(
            json.dumps(adjudicator,ensure_ascii=True,sort_keys=True)
            .encode("utf-8")).hexdigest(),
        "first_round_exact_agreement":stats["exact_agreement"],
        "human_authorization_verified":False,
        "independent_adjudicator_identity_verified":False,
        "score_correctness_established":False,
        "note":("This proves structured decisions match the frozen score packets, "
                "not that real human graders were independent or right. "
                "No pseudonymous case IDs or student responses are exported.")
    }
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description="Pseudonymous independent-review protocol helper")
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("prepare")
    a.add_argument("--plan",required=True)
    a.add_argument("--output-dir",required=True)
    b=sub.add_parser("freeze")
    b.add_argument("--manifest",required=True)
    b.add_argument("--review-a",required=True)
    b.add_argument("--review-b",required=True)
    b.add_argument("--output",required=True)
    b.add_argument("--bootstraps",type=int,default=200)
    b.add_argument("--seed",type=int,default=2028)
    c=sub.add_parser("finalize")
    c.add_argument("--manifest",required=True)
    c.add_argument("--first-round",required=True)
    c.add_argument("--review-a",required=True)
    c.add_argument("--review-b",required=True)
    c.add_argument("--adjudication",required=True)
    c.add_argument("--output",required=True)
    args=p.parse_args(argv)
    try:
        if args.cmd=="prepare":
            result=prepare(_read(args.plan),args.output_dir)
        elif args.cmd=="freeze":
            result=freeze(_read(args.manifest),_read(args.review_a),
                          _read(args.review_b),args.bootstraps,args.seed)
            _write_new(args.output,result)
            result={"frozen":True,"output":args.output,
                    "case_count":result["cases"],
                    "human_participation_verified":False}
        else:
            result=finalize(_read(args.manifest),_read(args.first_round),
                            _read(args.review_a),_read(args.review_b),
                            _read(args.adjudication))
            _write_new(args.output,result)
            result={"finalized":True,"output":args.output,
                    "cases":result["cases"],
                    "real_human_participation_verified":False}
        print(json.dumps(result,ensure_ascii=True))
        return 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
