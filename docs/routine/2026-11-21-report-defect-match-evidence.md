# 2026-11-21 — Prevent false defect-detection credit from a generic block

## Actual change
- Added per-case `caught_actual_defect` for reference-labeled defective items that the reviewer blocked. It must be an explicit boolean and requires an independently adjudicated **match to the true defect**, not merely that the model rejected the item.
- Detection numerator now counts only blocked cases whose detected reason matches the gold defect. A generic block with a wrong reason is reported separately as `unmatched_block`, not credited as a successful detection.
- Added sample fixture labels and adversarial regression tests for missing match evidence and blocks for incorrect reasons.
- Bounded numeric inputs to avoid extreme/unrepresentable values, in addition to finite nonnegative checks.

## Next
- Check cross-platform regression, update schema/handoff documentation and add the generator to Full-only release gates. All real-study RM cases remain NOT RUN.
