"""Non-predictive formative evidence: count independent opportunities and gaps.

Keep this interpretation separate from historical-performance baselines and
item choice. The existing v0.2 heuristic estimate remains unchanged for
historical benchmark reproducibility and backward-compatible CLI fields.
"""
try:
    from . import diagnosis
except ImportError:
    import diagnosis


def profile(events):
    summary = diagnosis.estimate(events)
    gates = {
        "at_least_three_independent_item_families": summary["families"] >= 3,
        "observed_on_multiple_utc_dates": summary["days"] >= 2,
        "multiple_cognitive_levels": len(summary["levels"]) >= 2,
        "verified_higher_order_success": (
            "no_verified_higher_order_success" not in summary["gaps"]),
        "not_recently_missed": "recent_miss" not in summary["flags"]
    }
    return {
        "kind": "observed_evidence_not_prediction",
        "label": summary["label"],
        "observations": summary["count"],
        "unique_items": summary["unique_items"],
        "independent_item_families": summary["families"],
        "utc_dates": summary["days"],
        "levels_observed": summary["levels"],
        "flags": summary["flags"],
        "missing_evidence": summary["gaps"],
        "gates": gates,
        "heuristic_evidence_index": summary["rate"],
        "calibrated_probability": False,
        "caution": ("Cross-date observations are not proof of delayed retention. "
                    "Evidence index is a descriptive heuristic, not future-response "
                    "accuracy or a probability of conceptual mastery.")
    }
