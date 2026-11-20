"""Transparent, uncalibrated history-only score; no latent-mastery claims.

This is intentionally a simple baseline, not BKT/IRT or an empirically
recalibrated student model. No new parameters are fit on previous held-out sets.
"""
import math


def history_baseline(events, prior=0.5, prior_weight=2.0):
    if type(prior) not in (int, float) or not math.isfinite(prior) or not 0 <= prior <= 1:
        raise ValueError("prior must be a finite scalar in [0,1]")
    if (type(prior_weight) not in (int,float) or not math.isfinite(prior_weight)
            or prior_weight <= 0):
        raise ValueError("prior_weight must be positive and finite")
    scores = []
    for event in events:
        score = event.get("score")
        if type(score) not in (int,float) or not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("response scores must be finite in [0,1]")
        scores.append(float(score))
    value = (prior * prior_weight + sum(scores))/(prior_weight + len(scores))
    return {
        "kind": "history_only_comparison_baseline",
        "observations": len(scores),
        "observed_mean": round(sum(scores)/len(scores), 4) if scores else None,
        "smoothed_history_score": round(value, 4),
        "calibrated": False,
        "is_mastery_probability": False,
        "note": ("A fixed smoothed average from observed scores; for comparison only. "
                 "It is not a validated individual probability, and is NOT "
                 "combined with the evidence-sufficiency gates.")
    }
