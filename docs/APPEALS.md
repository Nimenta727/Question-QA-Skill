# v0.8.0 learner grading appeals and corrections

CLI appeal records are **auditable metadata**, not an automatic semantic regrade or proof of qualified independent review.

After an answer, retain the returned event_id privately; older saved events may be selected by zero-based --event-index when opening their first appeal. The system adds an ID to that legacy event without wholesale schema migration.

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason rubric_dispute
    python scripts/qa.py appeal-list --state .qa-state.json
    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason rubric_rechecked --new-score 1 --reviewer-confirmed

Opening reasons: possible_key_error, equivalent_answer, rubric_dispute, scoring_error, other. Resolution reasons: key_verified, equivalence_reviewed, rubric_rechecked, scoring_corrected; for uphold use appeal_upheld without modified scores. --reviewer-confirmed is a self-declaration: qualified review must actually happen externally.

For previously rubric-scored manual answers, supply --criterion-scores '[1,0.5,1]' matching the exact original criterion count, and let the overall score derive from their mean; a supplied --new-score must agree. Objective corrections remain binary. The same score cannot be corrected into itself. Duplicate open or repeatedly resolved appeals are rejected.

Corrected event scores immediately feed historical reports and downstream formative logic. Stored audit records retain only identifiers, reason codes, timestamps and before/after numeric scores, not private student words, reviewer names or free-form notes. Clearing an earlier misconception after full-credit correction avoids false labels. Real high-stakes decisions need verified institutional review, transparency and appeal rights.


## v0.9.0 credential-gated corrections (opt-in)
For a protected learner state, the appeal lifecycle requires HMAC audit key on appeal-open and a valid, active reviewer token and bound registry plus audit key on appeal-resolve. A self-declared --reviewer-confirmed flag cannot bypass secure mode. Unprotected states remain v0.8-compatible but are labeled self_declared_not_authenticated. Read docs/SECURITY_AUDIT.md for registration, signed audit verification, independent checkpoints and rollback safeguards.
