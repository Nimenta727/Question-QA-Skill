#!/usr/bin/env python3
"""Fail-closed evidence contracts for independent model audit of authored questions.

This module DOES NOT call a language model, establish reviewer independence,
or prove that a model's prose is true. It prepares a blank audit packet which
a separate reviewing model must fill, and verifies its completeness, binding
to the actual bank/source, objectively checkable answers and risk decisions.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from . import question_quality, math_equivalence
    from .qa import read_bank, normalize
except ImportError:
    import question_quality
    import math_equivalence
    from qa import read_bank, normalize

CHECKS = (
    "source_scope", "independent_solution", "answer_and_equivalents",
    "ambiguity_and_conditions", "options_or_rubric", "diagnostic_value",
    "cognitive_alignment", "fairness_and_accessibility", "novelty",
)
RESULTS = ("pass", "fail", "uncertain")
SOURCE_MODES = ("course", "general_practice")
MAX_INPUT = 2_000_000


def _read_json(path):
    if Path(path).stat().st_size > MAX_INPUT:
        raise ValueError("audit input is too large")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_digest(path):
    if path is None:
        return None
    data = Path(path).read_bytes()
    if len(data) > MAX_INPUT:
        raise ValueError("source text is too large")
    return hashlib.sha256(data).hexdigest()


def _problem(code, item_id=None, detail=None):
    result = {"code": code}
    if item_id is not None:
        result["item_id"] = item_id
    if detail is not None:
        result["detail"] = detail
    return result


def make_template(bank, bank_digest, source_path=None, author_id="author"):
    """Return an entirely unapproved packet; suitable as AI audit input."""
    digest = source_digest(source_path)
    mode = "course" if source_path is not None else "general_practice"
    return {
        "format": 1,
        "bank_sha256": bank_digest,
        "source_sha256": digest,
        "source_mode": mode,
        "author_id": author_id,
        "auditor_id": "",
        "auditor_kind": "model",
        "independence_self_declared": False,
        "items": {
            q["id"]: {
                "decision": "needs_review",
                "independent_answer": "",
                "independent_solution": "",
                "source_quote": "",
                "accepted_alternatives": [],
                "distractor_analyses": {},
                "rubric_analyses": [],
                "checks": {name: {"result": "uncertain", "reason": ""}
                           for name in CHECKS},
                "risk_notes": [],
                "acknowledged_static_warnings": []
            }
            for q in bank["items"]
        },
        "notice": ("Template is unapproved. A separately prompted reviewing model "
                   "must solve independently, test alternatives, cite verbatim "
                   "source text if course-backed and justify every check. "
                   "Formal classroom assessment still needs qualified human review.")
    }


def _substantive(text):
    return isinstance(text, str) and len(text.strip()) >= 16 and len(text.strip()) <= 3000


def _answer_matches(q, answer):
    if not isinstance(answer, str) or not answer.strip():
        return False
    if q["type"] == "single":
        return answer.strip().upper() == q["answer"]
    if q["type"] == "short":
        allowed = {normalize(q["answer"])} | {normalize(x) for x in q.get("aliases", [])}
        if normalize(answer) in allowed:
            return True
        if "answer_equivalence" in q:
            try:
                return math_equivalence.matches(q["answer"], answer, q["answer_equivalence"])
            except (ValueError, TypeError):
                return False
        return False
    return True


def verify(bank, digest, audit, source_path=None, require_course=False):
    """Validate model-audit record structure, provenance and safety decisions.

    Passing is a *recorded model review*, NOT proof that content is correct.
    Treat any unknown/missing field and every unresolved issue as BLOCKED.
    """
    failures = []
    if not isinstance(audit, dict):
        return {"gate": "blocked", "failures": [_problem("audit_not_object")]}
    exact_top = {
        "format", "bank_sha256", "source_sha256", "source_mode",
        "author_id", "auditor_id", "auditor_kind",
        "independence_self_declared", "items", "notice"
    }
    if set(audit) != exact_top or audit.get("format") != 1:
        failures.append(_problem("audit_schema_invalid"))
    if audit.get("bank_sha256") != digest:
        failures.append(_problem("bank_hash_mismatch"))
    expected_source = source_digest(source_path)
    if audit.get("source_sha256") != expected_source:
        failures.append(_problem("source_hash_mismatch"))
    mode = "course" if source_path is not None else "general_practice"
    if audit.get("source_mode") != mode or (require_course and mode != "course"):
        failures.append(_problem("source_mode_invalid_or_course_required"))
    author = audit.get("author_id")
    auditor = audit.get("auditor_id")
    if (not isinstance(author, str) or not author.strip()
            or not isinstance(auditor, str) or not auditor.strip()
            or author.strip() == auditor.strip()
            or audit.get("independence_self_declared") is not True
            or audit.get("auditor_kind") != "model"):
        failures.append(_problem("independent_model_review_not_declared"))
    records = audit.get("items")
    expected_ids = {q["id"] for q in bank["items"]}
    if not isinstance(records, dict) or set(records) != expected_ids:
        failures.append(_problem("missing_extra_or_invalid_items"))
        records = records if isinstance(records, dict) else {}
    source_text = None
    if source_path is not None:
        source_text = Path(source_path).read_text(encoding="utf-8")
    statics = question_quality.audit(bank, digest)
    warnings = {qid: set() for qid in expected_ids}
    for finding in statics:
        if finding["severity"] == "error":
            failures.append(_problem("deterministic_hard_error", finding.get("item_id"),
                                     finding["code"]))
        if finding["severity"] == "warning" and finding.get("item_id") in warnings:
            warnings[finding["item_id"]].add(finding["code"])
    for q in bank["items"]:
        ident = q["id"]
        row = records.get(ident)
        if not isinstance(row, dict):
            failures.append(_problem("item_audit_missing", ident))
            continue
        fields = {"decision", "independent_answer", "independent_solution",
                  "source_quote", "accepted_alternatives", "distractor_analyses",
                  "rubric_analyses", "checks", "risk_notes",
                  "acknowledged_static_warnings"}
        if set(row) != fields:
            failures.append(_problem("item_schema_invalid", ident))
            continue
        if row["decision"] != "pass":
            failures.append(_problem("item_not_passed", ident))
        if not _substantive(row["independent_solution"]):
            failures.append(_problem("missing_independent_reasoning", ident))
        if not _answer_matches(q, row["independent_answer"]):
            failures.append(_problem("independent_answer_conflicts_with_key", ident))
        alternatives = row["accepted_alternatives"]
        if not isinstance(alternatives, list) or not all(
                isinstance(x, str) and x.strip() and len(x) <= 300
                for x in alternatives):
            failures.append(_problem("alternatives_unexamined", ident))
        elif q["type"] == "single" and alternatives:
            failures.append(_problem("single_choice_cannot_have_other_accepted_keys", ident))
        elif q["type"] == "short" and any(not _answer_matches(q, alt)
                                           for alt in alternatives):
            failures.append(_problem("alternatives_missing_from_actual_grading_key", ident))
        # A reviewer cannot simply check every box: each judgment needs
        # substantive text, and quoted course material must match the
        # independently supplied source byte-for-byte.
        checks = row["checks"]
        if not isinstance(checks, dict) or set(checks) != set(CHECKS):
            failures.append(_problem("review_criteria_incomplete", ident))
        else:
            for name in CHECKS:
                check = checks[name]
                if (not isinstance(check, dict) or set(check) != {"result", "reason"}
                        or check.get("result") not in RESULTS
                        or not _substantive(check.get("reason"))):
                    failures.append(_problem("review_criterion_incomplete", ident, name))
                elif check["result"] != "pass":
                    failures.append(_problem("review_criterion_not_passed", ident, name))
        quote = row["source_quote"]
        if mode == "course":
            if (not isinstance(quote, str) or len(quote.strip()) < 10
                    or len(quote) > 800 or quote.strip() not in source_text):
                failures.append(_problem("source_quote_not_found", ident))
            if q["source"].startswith("original-example:"):
                failures.append(_problem("original_example_not_course_citation", ident))
        elif quote != "":
            failures.append(_problem("general_practice_cannot_claim_source_quote", ident))
        if mode == "general_practice" and not q["source"].startswith("original-example:"):
            failures.append(_problem("course_citation_claim_without_course_source", ident))
        if q["type"] == "single":
            d = row["distractor_analyses"]
            if (not isinstance(d, dict) or set(d) != (set("ABCD")-{q["answer"]})
                    or any(not _substantive(x) for x in d.values())):
                failures.append(_problem("three_distractors_not_analyzed", ident))
            if row["rubric_analyses"] != []:
                failures.append(_problem("unexpected_rubric_analysis", ident))
        elif q["type"] == "manual":
            rubric = row["rubric_analyses"]
            if (not isinstance(rubric, list) or len(rubric) != len(q["rubric"])
                    or any(not _substantive(x) for x in rubric)):
                failures.append(_problem("rubric_not_independently_checked", ident))
            if row["distractor_analyses"] != {}:
                failures.append(_problem("unexpected_distractors", ident))
        else:
            if row["distractor_analyses"] != {} or row["rubric_analyses"] != []:
                failures.append(_problem("unexpected_option_or_rubric_analysis", ident))
        risk = row["risk_notes"]
        if not isinstance(risk, list) or any(
                not isinstance(x, str) or not x.strip() for x in risk):
            failures.append(_problem("invalid_risk_notes", ident))
        elif risk:
            failures.append(_problem("unresolved_risks", ident))
        ack = row["acknowledged_static_warnings"]
        if (not isinstance(ack, list) or any(not isinstance(x, str) for x in ack)
                or len(ack) != len(set(ack))):
            failures.append(_problem("invalid_static_warning_acknowledgment", ident))
        elif set(ack) != warnings[ident]:
            failures.append(_problem("static_warnings_unresolved", ident))
    gate = "model_review_recorded_for_practice" if not failures else "blocked"
    return {
        "gate": gate,
        "can_present_for_formative_practice": not failures,
        "course_source_verified_by_string_match": not failures and mode == "course",
        "actual_semantic_correctness_proven": False,
        "actual_independent_reviewer_identity_proven": False,
        "suitable_for_high_stakes_exams_without_human_review": False,
        "bank_sha256": digest,
        "source_sha256": expected_source,
        "items": len(bank["items"]),
        "failure_count": len(failures),
        "failures": failures,
        "notice": ("Passing validates a complete separately declared MODEL critique "
                   "and mechanically checked provenance/answers, NOT the truth "
                   "of every explanation or genuine independent model identity. "
                   "Resolve doubts and request qualified human review for exams.")
    }


def main(argv=None):
    p=argparse.ArgumentParser(description="Strict model-authored question audit contract")
    p.add_argument("bank")
    p.add_argument("--template", help="write all-unapproved evidence-based model review form")
    p.add_argument("--review", help="completed JSON from separate auditing model")
    p.add_argument("--source-file", help="actual instructor source TEXT; mandatory for course claims")
    p.add_argument("--author-id", default="question_author")
    p.add_argument("--require-course", action="store_true")
    p.add_argument("--output", help="write aggregate verdict without keys/stems")
    args=p.parse_args(argv)
    try:
        bank, digest=read_bank(args.bank)
        if args.template:
            if args.review or args.output:
                raise ValueError("--template cannot also verify or write a report")
            path=Path(args.template)
            if path.exists():
                raise ValueError("template already exists; refusing to overwrite")
            template=make_template(bank,digest,args.source_file,args.author_id)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(json.dumps(template,ensure_ascii=False,indent=2)+"\n",
                            encoding="utf-8")
            print(json.dumps({"created":str(path),"items":len(bank["items"]),
                              "all_pass":False},ensure_ascii=True))
            return 0
        if not args.review:
            raise ValueError("provide --review or --template")
        result=verify(bank,digest,_read_json(args.review),args.source_file,args.require_course)
        output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if args.output:
            target=Path(args.output)
            if target.exists():
                raise ValueError("audit verdict output exists; refusing overwrite")
            target.write_text(output,encoding="utf-8")
        else:
            print(output)
        return 0 if result["can_present_for_formative_practice"] else 2
    except (OSError,ValueError,TypeError,UnicodeError,KeyError,json.JSONDecodeError) as exc:
        print("error: "+str(exc),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
