# v0.6.0 modular diagnostic architecture

Three separate concerns are now exposed by the CLI while preserving the previously tested v0.2 algorithm:

1. scripts/evidence_engine.py reports observed independent families, UTC dates, cognitive levels, error flags, evidence gaps and a legacy descriptive index. It is evidence about observed responses, not a forecast and NOT a mastery probability.
2. scripts/prediction_engine.py computes a fixed smoothed historical-score baseline with two pseudo-counts at prior 0.5. It is an interpretable comparison signal, not fitted, calibrated or independently validated individual probability.
3. scripts/adaptive_engine.py continues to use the unchanged diagnosis.select_item policy, adding reason codes for knowledge coverage, uncertain answers, mistake repair and item-family diversity. These reason codes describe broad factors, not exact computed priority contributions or causal learning benefits.

The qa.py report and answer output keep legacy rate/status fields for compatibility and also return evidence_profile and prediction_baseline. The qa.py next command returns a cached selection explanation for the active pending question, without exposing the correct answer or rubric before submission.

FORGET-SE external exam and ASSISTments2015 practice prediction studies did not establish index improvement over simple history baselines. We have not tuned the original model on these two used test sets. Reliable evaluation of strong mastery labels still requires real item identities, independent and delayed recalls, expert-reviewed cognitive annotations, and genuinely unseen target assessments. Adaptive benefits require a separate prospective controlled comparison.
