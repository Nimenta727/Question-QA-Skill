# 2026-11-21 — Synthetic fixtures and regression gates for compact evaluation

## Actual changes
- Add `examples/synthetic_skill_eval.json`, with explicit `synthetic_demo` and `synthetic_labels` provenance; these cases are **fabricated test fixtures**, not actual model or learner observations.
- Add `tests/test_skill_eval_report.py`, checking exact numerator/denominator math, Wilson bounds, duplicate-family interval suppression, no-data behavior, unverified-model suppression, unknown-field privacy rejection, HTML injection escaping and CLI generation.
- Verify the report is offline, has native expandable details, includes at most 3 headline metrics and only one compact issue-category visualization; no external JS/CSS, no master-probability claims.

## Next steps
1. Run cross-platform CI; if tests fail, correct errors and document each repository modification in docs/routine.
2. Add user-facing bilingual workflow docs and ensure only Full contains the reporting script (Core remains lean).
3. Add real model run evidence **only after independent reference labels exist**; no synthesis numbers should be marketed as real scores.
