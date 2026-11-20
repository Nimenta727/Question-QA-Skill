# Changelog / 版本记录

## v1.0.0 — 2026-11-21 — Return to evidence-driven AI tutoring

- Replaced the continually growing primary SKILL.md with a compact, course-faithful QUICK and DEEP tutoring contract. Previously implemented security, data lifecycle, audit and research tools remain available only when requested via references/operations.md.
- Added a bounded, answer-key-free scripts/tutor_core.py pedagogical decision layer. Incorrect and unverified reasoning, guessed/hint-assisted correct answers, rubric-partial credit, transfer requests, missing reviewed question families and session end-of-budget each receive an explicit next teaching intent.
- Exposed safe tutor_intent on qa.py next, tutor_next_move on answer, and teaching_summary on report and completed session. All historical grading, local storage and v0.2 scientific diagnostic indices remain backward-compatible.
- New item-authoring briefs contain the scope and independent review checklist, not fictitious question keys; a suggested reviewed bank item is marked for reconsideration when its family/level cannot satisfy the intended probe.
- Added synthetic teaching-path regression tests (question budget, alternate family, no key leak, partial evidence, novice prerequisite gaps) and independent human-review quality criteria; passing tests do not demonstrate learner outcome gains.
- Rewrote bilingual README and maintained all advanced optional tooling. Scientific findings on two external real datasets remain negative/inconclusive, with no refitting of held-out test data.


## v0.9.0 — 2026-11-20

- Added offline administrator-scoped reviewer credentials, secure local token files, salted PBKDF2 verifiers and revocation; protected score corrections require verified active reviewer token possession rather than legacy self-declaration.
- Added HMAC-SHA256 appeal audit chain for open/resolve operations, a separate signed policy marker, integrity checking and independently archived keyed checkpoints; does not claim teacher identity verification, cryptographic non-repudiation or absolute immunity to rollback without external trust.
- Strengthened recovery and secret destination controls, and disallowed protected-mode downgrade through normal legacy correction paths.
- Added frozen-round independent expert-reference comparison with aggregate-only agreement/absolute errors, common reviewer-reference disagreements and case-bootstrap uncertainty, plus eight wholly synthetic end-to-end cases. No real student/teacher study or independently certified gold-standard accuracy.
- Additional security/research/privacy regressions; GitHub CI on Ubuntu/Windows/macOS with Python 3.9/3.12, immutable checksummed distribution and full fresh-extraction smoke tests.


## v0.9.0 — 2026-11-20

- Added stdlib-only, local credential-based reviewer enrollment, authenticated review, revocation and private token-file handling with salted PBKDF2-HMAC verifiers; actual educator identity, professional qualifications and blind-review independence are not verified by software.
- Added HMAC-linked appeal audit sequence, external signed policy binding, effective-score consistency checks and optional independently stored rollback-detecting checkpoint receipts. High-trust appeal correction requires reviewer credentials plus audit key, and signed-state rollback/deletion has explicit extra confirmation.
- Added third-party disputed-criteria finalization for previously frozen A/B reviewer study packets. A synthetic expert-reference comparison tool and samples can assess agreement with a declared reference, not prove expert correctness or demonstrate real human participation.
- Retained legacy local appeal behavior with explicit unauthenticated label, unchanged formative heuristic diagnostics, private data defaults and existing learning-state backward compatibility.
- Extended synthetic adversarial tests and Linux/Windows/macOS Python3.9/3.12 CI, immutable release ZIP with SHA256 and fresh-extraction smoke test.


## v0.8.0 — 2026-11-20

- Learner grade appeal life cycle, opaque event IDs and lazy legacy-ID migration, reviewer-confirmed corrections with rubric-consistent numeric before/after audit and reports using corrected grade.
- Rolling five local state snapshots and prior .bak, selected snapshot recovery with explicit confirmation, aggregate-only export by default, doubly confirmed private export, and typed-confirmation deletion of managed local files (not forensic erasure).
- Separate offline consent-gated reviewer-trial **preparation** utility: pseudonymous and independently randomized A/B assignment packets, frozen-round rubric validation, packet content SHA256 and aggregate agreement/uncertainty. Real authorizations/blinding cannot be verified by software and no real human trial occurred.
- New security and privacy regression tests; Linux/Windows/macOS × Python 3.9/3.12 verification and immutable checksummed v0.8.0 ZIP. Continues to avoid unvalidated latent-mastery or learning-benefit claims.


## v0.7.0 — 2026-11-20

- Opt-in exact rational/limited polynomial equivalence grading for short answers, bounded AST/Fraction evaluator, conservative unverified-response gate, unchanged legacy key behavior.
- Cross-platform native local file locks for full state transactions, atomic previous-valid snapshot, explicit integrity checks and confirmed rollback. Backups are private and recovery can lose one transaction.
- Private, aggregate-only two-reviewer study statistics: rubric agreement, weighted Cohen kappa, case-clustered bootstrap interval, adjudication completeness, synthetic example and protocol; no real human study has been completed.
- More unit, concurrency, privacy and security regression cases; GitHub CI for Linux/Windows/macOS Python3.9/3.12 and a fresh ZIP smoke test.
- Continues to refrain from BKT/IRT or other models tuned on previously exposed real-data test cohorts.


## v0.6.0 — 2026-11-20

- Independent double-reviewer manual-answer assessment, mandatory distinct third adjudicator when scores differ, verifiable exact quotations, missing-adjudication no-score gate, numeric-only private state.
- New --response-file avoids placing original student answers in command-line arguments; legacy grading interfaces remain compatible.
- Formative evidence sufficiency, fixed uncalibrated historical score comparison and rule-based adaptive-choice explanations separated into independent modules. Existing v0.2 heuristic remains unchanged for fair historical validation.
- Cross-platform CI on Ubuntu, Windows and macOS (Python 3.9/3.12). New release process verifies all three OSes, builds reproducibly, checks ZIP and SHA256, and publishes one immutable Git-tagged version without replacing old assets.
- Updated bilingual guide, synthetic arbitration examples, limitations and protocol. No automatic semantic scoring, verified reviewer independence or proven student outcome advantage is claimed.


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
