# Question-QA-Skill v1.0.0 — Back to the Teaching Core / 回到AI教学初衷

## One central promise
A lightweight Agent Skill that writes deep but fair **source-grounded** questions, probes one answer at a time, distinguishes justified understanding from guesses or assistance and recommends one high-information follow-up without inventing diagnoses.

## Shipped changes
- SKILL.md reduced from roughly 16k to around 3.2k characters. QUICK and DEEP interaction rules are first class; safety/assessment, research and operations are accessed only through references/operations.md when explicitly needed.
- New scripts/tutor_core.py makes pedagogical next-step decisions: baseline, prerequisite repair, reasoning clarification, independent verification, transfer challenge, session closure and a source-reviewable new-question draft when the reviewed bank is exhausted.
- Local CLI remains compatible: qa.py next now exposes tutor_intent; answer exposes tutor_next_move; report provides a teaching_summary for the current session. No student raw response, unpublished answer key or rubric is exposed in these newly added internal tutoring fields.
- Candidate question fit is explicitly evaluated against the intended cognitive level and item family; a candidate that fails to distinguish understanding from memorization is flagged for revision rather than called optimal.
- Fixed the session summary to keep partially correct observations unresolved and to stop asking new questions once the agreed question budget is reached.
- Rewritten bilingual README; added adaptive tutoring guidance and a six-dimensional **human review rubric** for future question/follow-up quality evaluation.
- Expanded synthetic branch/CLI regression tests and full Ubuntu/Windows/macOS Python3.9/3.12, deterministic SHA256-checked ZIP and extracted-package test gates.

## What this version does not claim
This is not a new calibrated IRT/BKT/FSRS learner model, general free-response semantic auto-grader or measured improvement in real student outcomes. Previously published independent real-data studies found no reliable predictive uplift over simpler history baselines; their holdout results were not reused to optimize model weights. Human source review and prospective, appropriately authorized educational studies are required to establish pedagogical impact.

All previous optional operations (manual adjudication, score appeals, local credential checks/HMAC audits, data lifecycle and private review-study tools) remain available for explicit advanced use. v0.9.0 remains an immutable prior release.
