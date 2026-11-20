# Roadmap / 下一步计划

## v0.1 — delivered
- Cross-platform Agent Skill with original deep questions + six-turn adaptive oral/written checks.
- Local no-dependency JSON question bank validator, one-at-a-time selector, objective and rubric-backed grading, compact learning history, provisional proficiency labels, spacing suggestions.
- Bilingual documentation, provenance and fairness rules, example data and repeatable tests.

## v0.2 — next
1. Per-session limits/coverage constraints and a short-question budget with a clear stop condition.
2. Question variants and stronger novelty/duplication audit; answer equivalence checks for algebra expressions.
3. Independent solution verification for generated mathematics and subject-specific unit tests.
4. Export/import portable summaries and privacy-preserving classroom reports.

## v0.3 — later
1. Optional, separately labeled BKT/IRT modules *only* after sufficient item/learner calibration evidence.
2. Item-level discrimination / exposure metrics and teacher review UI.
3. Configurable learning goals and scheduling, accessibility/localization reviews.
4. External verified question sources with license/provenance checks.

Priorities: accuracy and fairness > observable evidence > maintainability > unnecessary orchestration; no inflated token cost.


## v0.2 — shipped, diagnosis fidelity improvements
- Independent item family/day evidence, higher-order and delayed-retrieval gates.
- Guess/hint and overconfidence signals; optional rubric-backed misconception tags.
- Bounded adaptive quick sessions, focus concept, no exact item repeats, explicit exhaustion.
- Concept and cognitive-level reports, bilingual docs and regression tests.

## v0.3 — next: rigorous validation
- Anonymous, consented held-out answer-sequence evaluation with leakage-safe splits.
- Measure false-strong diagnosis rate, future-answer prediction, calibration and group fairness.
- Verify real question banks, equivalent answers and source fidelity with human review.
- Consider optional learned BKT/IRT/FSRS adapters only with calibration evidence and sensible fallback.

## v0.3 evaluation milestone — delivered (2026-11-20)
- Learner-disjoint next-response replay benchmark with AUC, probability-baseline Brier/ECE, learner bootstrap uncertainty.
- Fixed-version public FORGET-SE external-criterion benchmark with conflict-ID exclusion; report pooled and within-concept AUC.
- 61 Python regressions passed across 3.9 and 3.12; published negative/inconclusive findings in [VALIDATION.md](VALIDATION.md).

## Next gate before any BKT/IRT
1. Acquire a **second independent** and appropriately licensed cohort with reviewed item families, cognitive levels and genuine spaced recalls.
2. Separate evidence sufficiency/diagnostic follow-up rules from empirically calibrated future-answer forecasting.
3. Pre-register holdout evaluation, calibration, false-strong risk and fairness criteria. Never tune on the existing held-out test.
4. Only then compare optional calibrated BKT/IRT to simple baselines. Keep default local skill zero extra API or model-token cost.
