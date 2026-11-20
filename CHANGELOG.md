# Changelog / 版本记录

## v0.5.0 — 2026-11-20

- Added Python standard-library offline question quality auditor with duplicate/near-duplicate and rubric detection, optional exact-rational arithmetic answer witnesses and bank-hash-bound independent review templates. Strict gate refuses missing audits.
- Added a second licensed-research-data cohort: ASSISTments 2015 real mathematics sequences. Pinned 17.6MB source content hash, de-identified learner-disjoint splits, causal next-response replay, baseline AUC, student-clustered 95% intervals, aggregate-only reports.
- Held-out ASSIST2015 test: 280 eligible learners, 5,728 forecasts, v0.2 index AUC 0.620 vs smoothed learner history 0.710. Within-concept macro AUC difference uncertainty includes zero. No claim of latent mastery accuracy or causal adaptive learning benefit.
- Updated bilingual docs, Skill instructions, regression and CI release gates; retains P2 offline dashboard, reviewer-led open-answer feedback, zero-third-party-runtime dependencies.
- Existing v0.4.0 release remains immutable; this is a new separately versioned release.



## v0.4.0 — 2026-11-20

- **P2 offline dashboard**: single-file self-contained bilingual HTML, knowledge/prerequisite map, question coverage, evidence flags, cognitive-level response summaries, reviewed misconception labels, rubric criteria, historical trend and review dates.
- **Student answer assessment**: criterion-by-criterion reviewer-provided evidence, partial scores, strengths, actionable feedback, and explicit short-answer equivalence review. No claims of automatic semantic scoring or verified mastery probabilities.
- **Official distribution**: deterministic offline ZIP, SHA-256 file manifest, release smoke tests, bilingual installation notes, GitHub Actions package and GitHub Release publishing.
- **Data protection**: keep raw learner text and review evidence out of persistent state/dashboard/release package; no external resources required.
- **Research honesty**: retain v0.3 negative/inconclusive FORGET-SE external criterion findings. No BKT/IRT model or learning performance guarantees.

## v0.3.x — 2026-11-20

Independent historical-response evaluation and FORGET-SE external final exam benchmark, with student-disjoint splits, conflicting anonymized ID exclusion, statistical uncertainty, pinned data source and bilingual validation reports.

## v0.2 — 2026-11-20

Conservative independence/retention gates, confidence/hint flags, adaptive question targeting, reviewed misconception labels, session bounds and concept/cognitive-level reports.

## v0.1.0 — 2026-11-20

Initial bilingual Agent Skill, question bank, deterministic objective grading, reviewer-scored manual questions, local learning history, references and Python CI.
