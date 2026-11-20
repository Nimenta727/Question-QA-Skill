#!/usr/bin/env python3
"""Conservative, auditable question-quality checks (Python stdlib, offline).

Checks syntax, near-duplicates, evidence alignment metadata, optional exact
arithmetic witnesses and bank-bound human-review attestations. This code
does not claim to verify factual truth, educational fairness or scope itself.
"""
import argparse
import ast
import hashlib
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from fractions import Fraction
from pathlib import Path

try:
    from .qa import read_bank, normalize
except ImportError:
    from qa import read_bank, normalize

REVIEW_FIELDS = ("answer_verified", "source_verified", "scope_checked",
                 "ambiguity_checked", "fairness_checked", "rubric_checked")
MAX_INT = 10 ** 9


def normalized_stem(text):
    return re.sub(r"[\W_]+", "", unicodedata.normalize("NFKC", text).casefold())


def _number(expression):
    """Bounded rational arithmetic, never eval/exec; rejects names/functions."""
    if not isinstance(expression, str) or len(expression) > 100:
        raise ValueError("arithmetic expression must be a short string")
    tree = ast.parse(expression, mode="eval")

    def walk(node, depth=0):
        if depth > 16:
            raise ValueError("arithmetic expression is too deep")
        if isinstance(node, ast.Expression):
            return walk(node.body, depth+1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > MAX_INT or not str(node.value).replace(".", "").replace("-", "").isdigit():
                raise ValueError("numeric literal is out of range")
            return Fraction(str(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            number = walk(node.operand, depth+1)
            return number if isinstance(node.op, ast.UAdd) else -number
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a, b = walk(node.left, depth+1), walk(node.right, depth+1)
            if isinstance(node.op, ast.Add):
                result = a+b
            elif isinstance(node.op, ast.Sub):
                result = a-b
            elif isinstance(node.op, ast.Mult):
                result = a*b
            else:
                if b == 0:
                    raise ValueError("division by zero")
                result = a/b
            if result.numerator.bit_length() > 128 or result.denominator.bit_length() > 128:
                raise ValueError("result exceeds arithmetic limit")
            return result
        raise ValueError("only rational arithmetic (+,-,*,/) is allowed")
    return walk(tree)


def check_witness(q):
    if "verification" not in q:
        return None
    witness = q["verification"]
    if not isinstance(witness, dict) or set(witness) != {"kind", "expression"}:
        return "verification must be {kind: arithmetic, expression: ...}"
    if witness["kind"] != "arithmetic":
        return "unknown deterministic verification kind"
    if q["type"] not in ("single", "short"):
        return "arithmetic witness is only supported for objective items"
    answer = q["options"]["ABCD".index(q["answer"])] if q["type"] == "single" else q["answer"]
    try:
        expected = _number(witness["expression"])
        actual = _number(answer)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError) as exc:
        return "unverifiable arithmetic witness or numeric answer: " + str(exc)
    if actual != expected:
        return "key mismatch: arithmetic witness does not equal marked answer"
    if q["type"] == "single":
        for j, option in enumerate(q["options"]):
            try:
                if j != "ABCD".index(q["answer"]) and _number(option) == expected:
                    return "multiple numerically equivalent option keys"
            except (ValueError, SyntaxError, TypeError, ZeroDivisionError, OverflowError):
                pass
    return None


def _problem(code, severity, item=None, related=None):
    value = {"code": code, "severity": severity}
    if item is not None:
        value["item_id"] = item
    if related is not None:
        value["related_item_id"] = related
    return value


def audit(bank, digest, review=None):
    findings = []
    items = bank["items"]
    compact = {}
    by_family = {}
    for q in items:
        qid = q["id"]
        stem = normalized_stem(q["stem"])
        if len(stem) < 8:
            findings.append(_problem("extremely_short_stem", "warning", qid))
        if len(q["explanation"].strip()) < 8:
            findings.append(_problem("explanation_too_short_to_audit", "warning", qid))
        if not q["source"].startswith(("lesson:", "textbook:", "url:", "original-example:")):
            findings.append(_problem("unrecognized_source_anchor", "warning", qid))
        if q["source"].startswith("original-example:"):
            findings.append(_problem("unverified_original_source", "info", qid))
        if q["type"] == "manual":
            if len(set(map(normalize, q["rubric"]))) != len(q["rubric"]):
                findings.append(_problem("duplicate_rubric_criteria", "error", qid))
            if len(q["rubric"]) == 1:
                findings.append(_problem("single_criterion_open_response", "warning", qid))
        if q["type"] == "single":
            key = q["options"]["ABCD".index(q["answer"])]
            if len(key.strip()) <= 1 and not key.strip().isnumeric():
                findings.append(_problem("extremely_short_key", "warning", qid))
        if q["type"] == "short" and len(q["answer"].strip()) > 160:
            findings.append(_problem("unusually_long_short_key", "warning", qid))
        failure = check_witness(q)
        if failure:
            findings.append(_problem("invalid_arithmetic_witness", "error", qid))
        elif "verification" not in q:
            findings.append(_problem("deterministic_solution_not_provided", "info", qid))
        family = q.get("family", qid)
        if family in by_family and by_family[family]["concept"] != q["concept"]:
            findings.append(_problem("family_spans_concepts", "warning", qid,
                                     by_family[family]["id"]))
        by_family.setdefault(family, q)
        for previous_id, previous in compact.items():
            if stem == previous["stem"]:
                findings.append(_problem("duplicate_stem", "error", qid, previous_id))
            elif (q["concept"] == previous["concept"] and len(stem) >= 15
                  and len(previous["stem"]) >= 15
                  and SequenceMatcher(None, stem, previous["stem"]).ratio() >= 0.90):
                findings.append(_problem("near_duplicate_stem", "warning", qid, previous_id))
        compact[qid] = {"stem": stem, "concept": q["concept"]}
    if review is not None:
        if not isinstance(review, dict) or review.get("bank_sha256") != digest:
            findings.append(_problem("review_digest_mismatch", "error"))
        reviews = review.get("items", {}) if isinstance(review, dict) else {}
        if not isinstance(reviews, dict):
            findings.append(_problem("review_items_invalid", "error"))
            reviews = {}
        for q in items:
            record = reviews.get(q["id"])
            if not isinstance(record, dict) or any(record.get(field) is not True
                                                    for field in REVIEW_FIELDS):
                findings.append(_problem("incomplete_independent_review", "error", q["id"]))
                continue
            reviewer = record.get("reviewer", "")
            if not isinstance(reviewer, str) or len(reviewer.strip()) < 2:
                findings.append(_problem("missing_reviewer_identity", "error", q["id"]))
            if record.get("limitations"):
                findings.append(_problem("reviewer_reported_limitations", "warning", q["id"]))
    return findings


def report(bank, digest, review=None):
    problems = audit(bank, digest, review)
    counts = {severity: sum(f["severity"] == severity for f in problems)
              for severity in ("error", "warning", "info")}
    return {
        "items": len(bank["items"]), "bank_sha256": digest,
        "quality_status": ("blocked" if counts["error"] else
                           "reviewed_with_warnings" if review is not None and counts["warning"] else
                           "review_recorded" if review is not None else "review_required"),
        "counts": counts, "findings": problems,
        "review_attested": review is not None and counts["error"] == 0,
        "disclaimer": ("Static checks and reviewer attestations, not an independent proof "
                       "of factual correctness, fairness, curriculum alignment or mastery.")
    }


def review_template(bank, digest):
    """A blank, non-attesting form: no answer key or automatic approvals."""
    return {
        "bank_sha256": digest,
        "items": {
            q["id"]: {
                "reviewer": "",
                "answer_verified": False, "source_verified": False,
                "scope_checked": False, "ambiguity_checked": False,
                "fairness_checked": False, "rubric_checked": False,
                "limitations": ""
            } for q in bank["items"]
        },
        "notice": "All checks must be completed by an independent reviewer. "
                  "Do not use an AI-generated affirmation as proof of correctness."
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline item-quality audit / 命题质量审查")
    p.add_argument("bank")
    p.add_argument("--review", help="bank-digest-bound reviewer attestations JSON")
    p.add_argument("--review-template", help="write an all-false reviewer template JSON")
    p.add_argument("--strict", action="store_true", help="require review and zero errors")
    p.add_argument("--output", help="save aggregate and item-ID findings JSON")
    args = p.parse_args(argv)
    try:
        bank, digest = read_bank(args.bank)
        if args.review_template:
            if args.review or args.strict or args.output:
                raise ValueError("--review-template cannot be combined with review, strict or output")
            destination = Path(args.review_template)
            if destination.exists():
                raise ValueError("review template destination exists; avoid overwriting human reviews")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(review_template(bank, digest), ensure_ascii=False, indent=2)
                + "\n", encoding="utf-8")
            print(json.dumps({"template_created": str(destination),
                              "items": len(bank["items"]),
                              "bank_sha256": digest}, ensure_ascii=False))
            return 0
        review = json.loads(Path(args.review).read_text(encoding="utf-8")) if args.review else None
        result = report(bank, digest, review)
        if args.strict and (not args.review or result["counts"]["error"]):
            result["quality_status"] = "blocked"
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text)
        return 2 if result["quality_status"] == "blocked" else 0
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print("error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
