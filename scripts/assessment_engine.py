"""Two-reviewer, rubric-aligned assessment with mandatory conflict arbitration.

This module validates structured judgments and direct answer quotations; it
DOES NOT infer semantic correctness or verify review independence. No answer
or rationale is persisted: callers choose what summary to retain.
"""
import json
import math
from pathlib import Path

try:
    from .feedback import parse_judgments
except ImportError:
    from feedback import parse_judgments


def read_json_argument(argument):
    if not isinstance(argument, str) or not argument.strip():
        raise ValueError("review JSON or @file must be supplied")
    if argument.startswith("@"):
        return json.loads(Path(argument[1:]).read_text(encoding="utf-8"))
    return json.loads(argument)


def _id(value):
    return (isinstance(value, str) and 2 <= len(value.strip()) <= 80
            and all(c not in "\n\r\t" for c in value))


def _anchored_judgments(criteria, judgments, answer):
    """Require each reviewer to point to a verbatim excerpt from the answer."""
    if not isinstance(judgments, list) or len(judgments) != len(criteria):
        raise ValueError("one judgment is required for every rubric criterion")
    sanitized = []
    for i, (criterion, item) in enumerate(zip(criteria, judgments)):
        if not isinstance(item, dict) or set(item) != {"score", "evidence", "feedback", "quote"}:
            raise ValueError("review criterion %d needs score/evidence/feedback/quote" % (i + 1))
        quote = item["quote"]
        if (not isinstance(quote, str) or not quote.strip()
                or len(quote) > 600 or quote not in answer):
            raise ValueError("criterion %d quote must occur verbatim in student's answer" % (i + 1))
        checked = parse_judgments(json.dumps([{
            "score": item["score"], "evidence": item["evidence"],
            "feedback": item["feedback"]
        }], ensure_ascii=False), [criterion])[0]
        checked["quote"] = quote
        sanitized.append(checked)
    return sanitized


def resolve(criteria, response, reviews_arg, adjudication_arg=None):
    """Return a transient item-level result; raises on unadjudicated disagreement.

    Independent labels are declarations only, not verified independent authors.
    Score arithmetic is auditable, but assessment correctness is not automatic.
    """
    if not isinstance(response, str) or not response.strip():
        raise ValueError("student response cannot be empty for independent review")
    content = read_json_argument(reviews_arg)
    if not isinstance(content, dict) or set(content) != {"reviews"}:
        raise ValueError("independent-review JSON must contain only reviews")
    reviewers = content["reviews"]
    if not isinstance(reviewers, list) or len(reviewers) != 2:
        raise ValueError("exactly two independently recorded reviewers required")
    ids = []
    collected = []
    for entry in reviewers:
        if not isinstance(entry, dict) or set(entry) != {"reviewer_id", "judgments", "independent"}:
            raise ValueError("reviewer record needs reviewer_id, judgments, independent")
        label = entry["reviewer_id"]
        if not _id(label) or entry["independent"] is not True:
            raise ValueError("reviewer must declare a distinct identity and independence")
        ids.append(label.strip())
        collected.append(_anchored_judgments(criteria, entry["judgments"], response))
    if ids[0] == ids[1]:
        raise ValueError("reviewers must use distinct identifiers")
    disagreements = [i for i in range(len(criteria))
                     if collected[0][i]["score"] != collected[1][i]["score"]]
    if adjudication_arg is not None and not disagreements:
        raise ValueError("adjudication not needed: both reviewers agree")
    arbitration = {}
    if disagreements:
        if adjudication_arg is None:
            raise ValueError("review_disagreement: adjudication needed for criterion indices "
                             + ",".join(str(i + 1) for i in disagreements))
        obj = read_json_argument(adjudication_arg)
        if not isinstance(obj, dict) or set(obj) != {"adjudicator_id", "decisions"}:
            raise ValueError("adjudication needs adjudicator_id and decisions")
        aid = obj["adjudicator_id"]
        if not _id(aid) or aid.strip() in ids:
            raise ValueError("adjudicator must be distinct from both reviewers")
        decisions = obj["decisions"]
        if not isinstance(decisions, list) or len(decisions) != len(disagreements):
            raise ValueError("adjudication must decide each disputed criterion exactly once")
        for decision in decisions:
            if not isinstance(decision, dict) or set(decision) != {
                "criterion_index", "score", "reason", "quote"
            }:
                raise ValueError("adjudication decision requires criterion_index/score/reason/quote")
            i = decision["criterion_index"]
            score = decision["score"]
            reason = decision["reason"]
            quote = decision["quote"]
            if type(i) is not int or i not in disagreements or i in arbitration:
                raise ValueError("invalid or duplicate adjudicated criterion index")
            if type(score) not in (int, float) or not math.isfinite(score) or score not in (0, .5, 1):
                raise ValueError("adjudicated score must be 0/0.5/1")
            if (not isinstance(reason, str) or not reason.strip() or len(reason) > 1500
                    or not isinstance(quote, str) or not quote.strip()
                    or len(quote) > 600 or quote not in response):
                raise ValueError("adjudication requires reason and verbatim response quote")
            arbitration[i] = {"score": float(score), "reason": reason, "quote": quote}
        if set(arbitration) != set(disagreements):
            raise ValueError("all disputed rubric criteria must be adjudicated")
    final = []
    for i, criterion in enumerate(criteria):
        first, second = collected[0][i], collected[1][i]
        if i in arbitration:
            grade = arbitration[i]["score"]
            mechanism = "adjudicated"
        else:
            grade = first["score"]
            mechanism = "reviewer_agreement"
        final.append({
            "criterion": criterion, "score": grade, "resolution": mechanism,
            "reviewer_scores": [first["score"], second["score"]],
            "evidence": [first["evidence"], second["evidence"]],
            "feedback": [first["feedback"], second["feedback"]],
            "quotes": [first["quote"], second["quote"]],
            **({"adjudication_reason": arbitration[i]["reason"]}
               if i in arbitration else {})
        })
    avg = sum(x["score"] for x in final) / len(final)
    return {
        "score": avg, "method": ("adjudicated_rubric_review" if disagreements
                               else "two_reviewer_agreement"),
        "criteria": final,
        "agreement": {
            "exact": len(criteria) - len(disagreements),
            "total": len(criteria),
            "rate": (len(criteria) - len(disagreements)) / len(criteria),
            "disputed_indices": [i + 1 for i in disagreements],
            "mean_absolute_score_gap": sum(
                abs(collected[0][i]["score"] - collected[1][i]["score"])
                for i in range(len(criteria))) / len(criteria)
        },
        "strengths": [r["criterion"] for r in final if r["score"] == 1],
        "improve": [r["criterion"] for r in final if r["score"] < 1],
        "next_step": ("Review an incomplete criterion and try a new question."
                      if any(r["score"] < 1 for r in final)
                      else "Try a distinct transfer question."),
        "notice": ("Review identity and independence are self-declared; quote matching "
                   "checks presence, not reasoning correctness. Human/Agent assessors "
                   "must confirm the rubric and source independently.")
    }
