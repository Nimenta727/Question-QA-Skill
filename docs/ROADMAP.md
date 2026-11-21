# Roadmap / 路线图 — evidence before feature expansion

**Current source target:** v1.2.3 Core + Full. Verify actual release tag/assets before claiming publication; v1.2.1 remains the prior verified release. This document states planned work; no row below implies experimental validation has been completed.

## P0 — release readiness and current-documentation convergence (engineering)

- Align bilingual README, installation, architecture, audit, diagnostics and source references with actual v1.2.1 code and release status.
- Remove superseded version-specific narratives from the working tree; preserve historical commits/tags and the dated `docs/routine/` engineering trail.
- Keep Core prompt short and lazy-loaded, update related tests and code docstrings without altering grading or scoring semantics.
- **Exit evidence:** PR diff reviewed, local links resolve, current package test and cross-platform CI green, independent reviewer concerns recorded rather than silently bypassed.

## P0 — v1.3 quality-evidence pilot (NOT completed)

1. **Verified curriculum blueprint.** Obtain permissioned source excerpts for at least one concrete course; record knowledge claims, source locations, expected reasoning, independent item families and misconceptions *as hypotheses*.
2. **Independent authored-item review.** Blind solve before opening the author's key; use nine-field adversarial review; label deliberately flawed items and correct ones; report actual catch, miss, false-alarm and unresolved rates by defect category.
3. **Observed-learning diagnosis.** On consented or clearly synthetic responses, test wrong-with-unknown-cause, hinted success, guessed success, partial credit, justified success and stop conditions. Compare follow-up plans with a preregistered fixed-sequence baseline.
4. **Outcome claims only after evidence.** Separate implementation tests, reviewer agreement, accurate source attribution, later retention and causal adaptive improvements. No score-label-to-mastery shortcut.
5. **Token/cost tracking.** Measure actual input tokens and number of review/model invocations under identical source inputs; do not infer savings from compressed ZIP bytes.

See the [12-case real-model execution matrix](REAL_MODEL_TESTS.md) / [中文测试矩阵](REAL_MODEL_TESTS.zh-CN.md), [verification status ledger](TEST_STATUS.md), and [English study gates](QUALITY_VALIDATION.md) / [中文验收方案](QUALITY_VALIDATION.zh-CN.md) for design, denominators and failure policy. **RM-01–RM-12 are all NOT RUN until real evidence is recorded.**

## P1 — independent data and domain tools

- Verify genuine alternative solutions and equivalent answers in mathematics and C/programming with controlled domain-specific execution where available; preserve uncertainty otherwise.
- Acquire a truly unseen cohort with item identity, question family, timing, source permissions, blinded expert standards and delayed follow-ups if ethically authorized.
- Pre-register metrics, baselines and cutoffs before opening holdout results. Previous FORGET-SE and ASSISTments2015 evaluation splits are **not new untouched test sets**.
- Explore calibrated BKT/IRT or similar models **only** if appropriate data, calibration evidence and incremental baselines support them.

## P2 — optional tooling, not part of normal tutoring

- Maintain appeals, security controls, state recovery, investigator scripts and separate development-agent/PR review workflow as optional Full capabilities.
- Treat feature requests as modular additions. Do not force external model calls, student-data storage or multi-agent overhead into the default Core loop.

## Non-negotiable claims boundary

A successful CI run proves the engineered checks ran; it does not demonstrate learning gain. An LLM self-review cannot be presented as an independent specialist endorsement. A heuristic `rate` or `tentatively_strong` label cannot be reported as a validated probability or a definitive student ability judgment. High-stakes assessment requires independent qualified human review.

## v1.2.3 — post-Skill evidence reporting (engineering)

- Ship a Full-only offline HTML report for **already recorded** Skill evaluations; Core stays lean.
- Give ratios with defensible denominators and conditional intervals, at most one useful defect visualization, and failures first. Clearly mark synthetic demos.
- Do not mark RM-01–RM-12 complete until genuine model calls and independent adjudicated labels exist. [Report method](SKILL_EVAL_REPORT.md) · [Status](TEST_STATUS.md).

## v1.2.3 — dedicated empirical evaluation workspace

Three still-unrun protocols are now organized in [docs/evaluations](evaluations/README.md): licensed real-course item quality, independently adjudicated auditing misses/false alarms, and paired adaptive-vs-fixed-order question selection. Next obtain authorized materials, freeze reference labels and fixed-order baseline, actually run the Skill, then publish privacy-safe denominated aggregates. Offline replay is not a causal learning-gain study.
