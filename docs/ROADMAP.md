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


## v0.4.0 — P2 release and reviewed answer assessment (delivered)
- **Offline HTML visualization**: knowledge map, coverage, level-based observed scores, reviewer-tagged mistakes, response trends, rubric criteria and suggested review schedule. Works bilingually without any external fonts, scripts or network.
- **Reviewed student assessment**: per-criterion open-answer scoring with evidence, partial credit and actionable corrections; explicit short-answer equivalence override by reviewer.
- **Official artifact pipeline**: deterministic, privacy-safe ZIP, embedded SHA256 manifest, standalone install documentation, CI tests against freshly extracted package, and GitHub Release workflow.
- **Scientific restraint**: v0.2 index still lacks proven predictive uplift; not a calibrated learner model.

## Beyond v0.4.0
1. Independent question-bank correctness and fairness validator.
2. Second real learner cohort with verified time intervals, author-reviewed item family/cognitive metadata and subject-level analysis.
3. Accessibility review and multilingual screen-reader checks for the offline dashboard; opt-in aggregate exports only.
4. Pilot observation of rubric reviewer agreement and score consistency; further model calibration only when independently demonstrated.


## v0.5.0 — delivered: item validation + independent mathematics benchmark
- Safe deterministic item-quality auditor (exact/near duplicate, optional rational witness, provenance/rubric anomalies) with independent reviewer approval gating.
- Public ASSISTments2015 real learner evaluation, pinned verified source, no raw student data redistribution, independent per-learner historical prediction.
- Honest negative/inconclusive findings: AUC 0.620 evidence index vs 0.710 learner history; within-skill confidence interval spans zero. See VALIDATION_ASSIST2015.md.
- Next: vetted problem identities, two-reviewer disagreement analysis, true delayed response dates, independent course scope alignment, prospective opt-in adaptive policy trials and sample-adequate separate calibrated models only if baseline comparison warrants them.


## v0.6.0 — delivered: assessment consensus and explainable architecture
- Two separate reviewer packets and mandatory third-party adjudication before recording disputed free-form scores, with proof-of-presence for quoted student phrases; still requires genuine semantic assessment.
- Separately exposed observed evidence, history baseline and adaptive-selection explanation modules without modifying already evaluated v0.2 scoring weights or claims.
- Privacy-friendly response-file handling and more complete compatibility testing across Linux, macOS, Windows.
- Immutable, tag-versioned SHA256-verified releases; main branch changes cannot silently replace a published version.

## After v0.6.0
1. Build real reviewer-blinded validation protocol with provenance and judge agreement outcomes, and a documented appeal/correction process. Synthetic identity declarations alone are not proof.
2. Add optional, well-tested mathematics equivalence verification and safe, isolated code-answer unit testing; do NOT run untrusted submissions in the host OS.
3. Add atomic, private state storage with concurrency-safe locking, backup/recovery and selective deletion.
4. Collect consented third independent cohort with reviewed problem IDs and authentic time gaps; measure diagnostic mistakes and adaptive policy effectiveness before trying calibrated models.


## v0.7.0 — delivered
- Bounded exact rational and polynomial equivalence on author-opted-in short numeric items; unsupported student input is escalated instead of blindly marked incorrect.
- Native same-state file locks, one-step last-good backup, atomic snapshots, explicit integrity inspection and opt-in recovery on local filesystems.
- Aggregate private rubric inter-rater comparison and protocol for a future real, appropriately authorized blinded study; synthetic test cases are not validation evidence.
- Cross-platform verification maintained; immutable tag v0.7.0 release distinct from prior versions.

## v0.8.0 candidates (not yet implemented)
1. Consent-based prospective independent reviewer pilot, source-grounded expert adjudication and formal learner correction/appeal mechanisms.
2. Accessible user-facing mathematical-expression editor, careful symbol normalization and exact-condition annotation; avoid generic symbolic solvers without independent evaluation.
3. Multi-snapshot encrypted backup/retention, optional SQLite transaction backend for classroom concurrency, secure deletion/export controls.
4. New independent external cohort with authentic question identity/timing for diagnostic false-positive and adaptive learning outcome measurement. Do not reuse old held-out tests for hyperparameters.


## v0.8.0 — delivered
- Review-gated grade appeal lifecycle; before/after correction audit, revised learner evidence immediately reflected in reports and rule-based selection, legacy history migration without breaking schema.
- At most five rolling verified previous local state snapshots, explicit rollback, safe aggregate vs consent-confirmed private export, and user-confirmed deletion of managed files.
- Pseudonymous independent reviewer trial preparation and first-round freeze tooling with authorization self-declaration gate, exact rubric matching and aggregate-only reliability report; **no genuine human participants have yet been enrolled**.
- Previous versions remain immutable and historical external test results remain unaffected.

## v0.9.0 candidates (not yet completed)
1. Implement authenticated reviewer identity and tamper-evident correction ledger; retain school-level appeal rights, not just locally editable JSON.
2. Under actual education-institution and guardian/student approval, run a prospective blinded two-reviewer pilot with independently adjudicated reference grades; publish aggregate uncertainty, never raw learner records.
3. Optional encrypted snapshot retention policies and stronger shared-database consistency for classroom-scale deployments, with secure key handling.
4. New independent longitudinal validation data containing problem identities, actual review timing and checked cognitive levels before calibrating any learner-prediction model.
