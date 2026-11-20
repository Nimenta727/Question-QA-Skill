# Question-QA-Skill v0.8.0 — Installation & usage

An Agent Skills-compatible skill plus an independent offline Python CLI (Python 3.9+, standard library, Windows/macOS/Linux). It is not a Python package requiring pip installation.

## Install
Download question-qa-skill-0.8.0.zip and SHA256SUMS.txt from GitHub Releases, verify SHA256 and extract. Register/copy the entire extracted directory to the location recognized by your Agent host (exact paths are host-specific). Or run from its directory:

    python3 scripts/qa.py validate examples/sample_bank.json

On Windows, py -3 may be available in place of python3.

## Adaptive quiz and diagnosis

    python3 scripts/qa.py start examples/sample_bank.json --state .qa-state.json --mode quick --limit 6
    python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json
    python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C --confidence unsure
    python3 scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json

The next command never reveals keys; review responses after submitting an answer. Never expose the whole bank to the learner during a quiz.

## Student answer assessment

Objective single-choice answers are checked against the explicit key. Short answers use exact normalized matching; an independent reviewer may mark an equivalent string with --review-equivalent and a defensible --reason. Unchecked synonyms or mathematically equivalent forms are not automatically treated as conceptual failures.

Open/manual responses require a teacher or Agent reviewer to inspect the actual answer against each rubric criterion. **The local script does not automatically understand arbitrary natural-language responses.** Create an array of score/evidence/feedback objects in a JSON file (see examples/sample_review.json for format only, NOT a rubric to reuse unchanged). Each score must be 0, 0.5 or 1. Example:

    python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response "student response" --reason "criterion-by-criterion review" --rubric-judgments @review.json

Returns per-criterion strengths, incomplete points, overall score, actionable feedback, and a suggested next probe. Only numeric criterion scores are persisted in the state, not raw student answers or narrative feedback. Older --score and --reason manual grading remains supported.

CLI argument values can be visible in shell history and process listings; avoid entering identifying student data. Keep local state files private.

## Offline dashboard

    python3 scripts/dashboard.py examples/sample_bank.json --state .qa-state.json --output learning-dashboard.html --lang en
    python3 scripts/dashboard.py examples/sample_bank.json --state examples/demo_state.json --output demo-dashboard.html --lang zh

Open the generated HTML in any modern browser. It uses no remote scripts, fonts, services or models. Visualizations include prerequisite map, evidence coverage, cognitive-level observed scores, reviewer-tagged misconceptions, rubric criterion summaries, daily trends and review suggestions. Toggle English/Chinese, print or export to PDF in the browser.

**The displayed indicators are descriptive study evidence, NOT calibrated proficiency probabilities.**

## Verify/rebuild the release

    python3 -m unittest discover -s tests -v
    python3 scripts/build_release.py --output dist
    python3 scripts/build_release.py --verify dist/question-qa-skill-0.8.0.zip

A deterministic archive is covered by a per-file SHA256 manifest; release also provides SHA256SUMS.txt. See CHANGELOG.md and docs/RELEASE.md.

## Scientific limitation

The first real-world FORGET-SE final-exam benchmark did not establish superiority of the heuristic diagnostic index over simple historical-score baselines. No BKT/IRT calibration or latent mastery claim is made. See docs/VALIDATION.md.


## New in v0.8.0: question-quality and second-cohort validation

    python3 scripts/question_quality.py examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json
    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

Reviewers must independently check each item rather than automatically approving generated questions. Read docs/QUESTION_QUALITY.md and docs/VALIDATION_ASSIST2015.md; the source mathematics research dataset is governed by its own research-use conditions and is never bundled.


## v0.8.0 double-review grading
For a pending manual item, pass --response-file PRIVATE_ANSWER.txt --independent-reviews @reviews.json. If the reviewers disagree, an additional --adjudication @decisions.json is mandatory; the pending item is not consumed until all disputes are resolved. All sample packets are synthetic. See docs/ASSESSMENT.md for the reviewer and adjudicator formats; docs/ARCHITECTURE.md separates diagnostic evidence, historical score comparison and question-choice reasons.


## New in v0.8.0
- Math: opt-in exact arithmetic/polynomial short-answer equivalence only; documentation at docs/MATH_EQUIVALENCE.md.
- State health: python scripts/qa.py state-check --state .qa-state.json; deliberate previous-version rollback: python scripts/qa.py state-recover --state .qa-state.json --confirm. Private last-good backup is .bak, lock is .lock.
- Reviewer study: python scripts/reviewer_study.py --input examples/sample_reviewer_study.json --output aggregate.json. The sample is synthetic; no real review study has been performed. See docs/REVIEWER_STUDY.md.


## v0.8.0 appeals and retention
Each recorded answer has event_id. Request a correction with appeal-open --event-id ID --reason rubric_dispute. Reviewers must independently verify the marking evidence before appeal-resolve --appeal-id ID --decision correct --reason rubric_rechecked --reviewer-confirmed and revised scores. Details: docs/APPEALS.md.

State snapshots: state-snapshots, optional state-recover --snapshot ID --confirm. Aggregate-only export: state-export --output qa-export-summary.json. Full private export: additionally supply --include-private --confirm-private. Local deletion: state-delete --confirm-delete DELETE-LOCAL; this does NOT forensically erase external copies. See docs/DATA_LIFECYCLE.md. Trial-preparation tools require real authorization handled outside this software; see docs/REVIEW_TRIAL.md.


## v0.9.0 protected review setup
To set up credential-gated review, create a private reviewer registry and private admin/reviewer token files with scripts/reviewer_credentials.py. Then enable a protected audit on a local learner state *before opening any appeals* using qa.py audit-init with an administrator token; the tool creates an external HMAC key and state audit-policy marker. Protected appeal-resolve requires registry, reviewer ID, reviewer-token-file and audit-key-file, not only legacy --reviewer-confirmed. Use audit-verify and retain separately protected audit-checkpoint receipts. Read docs/SECURITY_AUDIT.md first; external reviewer identity is not established by tokens alone.


## v0.9.0 protected reviewer mode and independent reference scoring
Use scripts/reviewer_credentials.py to initialize the local registry, enroll/revoke teachers under administrator control, and scripts/qa.py audit-init to protect a fresh learner state. Protected appeal corrections require the valid reviewer token, registry and independently secured HMAC key. Retain audit-checkpoint receipts separately to compare against rollback. Full protocol: docs/SECURE_REVIEW.md and docs/SECURITY_AUDIT.md. For a future externally authorized pilot, use the frozen A/B score packets and scripts/reviewer_pilot.py with a separate expert reference; docs/REFERENCE_PILOT.md includes a fully synthetic demonstration.
