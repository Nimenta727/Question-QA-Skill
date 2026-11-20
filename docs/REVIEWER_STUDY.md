# v0.7.0 private paired-review reliability study protocol

**No real human study has been conducted in this release.** The implementation and example fixtures are synthetic. Matching reviewer scores do not demonstrate factual correctness, reviewer independence, score calibration or fairness.

A proposed prospective independent study should: obtain appropriate institutional/teacher and parental or guardian permissions as necessary; use genuinely authorized, pseudonymized student answers; prespecify the item set, rubric and primary endpoints; blind two actual reviewers to each other's first-round scores; freeze initial ratings before independent third-party adjudication; and validate scoring correctness against an independent specialist benchmark. Protect all answer-level files outside this repository and release aggregate statistics only.

The scorer accepts a private JSON document with exactly study_type and cases. Each case has an opaque unique case_id and equal-length arrays scores_a and scores_b, with 0/0.5/1 per rubric criterion, optionally a final array from third-party adjudication. Final adjudication cannot alter entries on which both reviewers already agreed. study_type is synthetic or real_private_self_declared; this choice is **not independent evidence of real human participation**.

Run:
    python scripts/reviewer_study.py --input examples/sample_reviewer_study.json --bootstraps 200 --output aggregate.json

The output includes exact criterion agreement, full-case agreement, quadratic weighted Cohen kappa, mean absolute gap, disputes, unresolved cases and optional case-clustered bootstrap interval for agreement. Reviewer IDs, case IDs, quotations and original student responses are never exported. Kappa is null if its chance-correction denominator is zero. Do not tune systems or claim model validation on this synthetic example.
