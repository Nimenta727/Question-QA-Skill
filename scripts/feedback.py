"""Evidence-linked assessment of open answers, reviewed outside this CLI.

The reviewer must actually inspect the student's response against each rubric
criterion. This code validates the review; it does NOT semantically grade text.
It does not store raw student response or rubric evidence.
"""
import json
import math
from pathlib import Path


def parse_judgments(argument, criteria):
    raw = Path(argument[1:]).read_text(encoding="utf-8") if argument.startswith("@") else argument
    data = json.loads(raw)
    if not isinstance(data, list) or len(data) != len(criteria):
        raise ValueError("rubric judgments must have one entry for each criterion")
    results = []
    for n, (criterion, item) in enumerate(zip(criteria, data), 1):
        if not isinstance(item, dict) or set(item) != {"score", "evidence", "feedback"}:
            raise ValueError("criterion %d requires score, evidence and feedback" % n)
        score = item["score"]
        if type(score) not in (int, float) or not math.isfinite(score) or score not in (0, 0.5, 1):
            raise ValueError("criterion %d score must be 0/0.5/1" % n)
        for key in ("evidence", "feedback"):
            if (not isinstance(item[key], str) or not item[key].strip()
                    or len(item[key]) > 1500):
                raise ValueError("criterion %d %s must be nonempty and <=1500 chars" % (n, key))
        results.append({"criterion": criterion, "score": float(score),
                        "evidence": item["evidence"].strip(),
                        "feedback": item["feedback"].strip()})
    return results


def assess_rubric(criteria, argument):
    reviews = parse_judgments(argument, criteria)
    score = sum(r["score"] for r in reviews) / len(reviews)
    missing = [r["criterion"] for r in reviews if r["score"] < 1]
    return {"score": score, "method": "criterion_rubric_review",
            "criteria": reviews,
            "strengths": [r["criterion"] for r in reviews if r["score"] == 1],
            "improve": missing,
            "next_step": ("Review an incomplete criterion and retry with a fresh example."
                          if missing else "Try an independent application or transfer item."),
            "notice": "Evidence was supplied by the human or AI reviewer; not verified by local code."}


def concise_feedback(item, score, misconception=None, confidence="none"):
    if item["type"] == "manual":
        return None
    if score >= 1:
        result = "Correct against the explicit answer key."
        if confidence in ("guess", "unsure"):
            result += " Confirm with a different question before assuming mastery."
        return result
    if item["type"] == "short":
        return ("Exact normalized key did not match. Equivalent mathematical or "
                "natural-language answers require review; no conceptual error inferred.")
    if misconception:
        return ("Incorrect selection; reviewer-tagged possible error: "
                + misconception + ". Compare with the explanation.")
    return "Incorrect selection. Review the explanation and try a different example."
