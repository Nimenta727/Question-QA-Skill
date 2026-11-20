# v0.9.0 local reviewer credentials and HMAC appeal audit

The CLI provides offline reviewer key-possession checks, administrator revocation, HMAC-chained appeal records and independently retained checkpoints. These mechanisms **do not certify a real teacher's identity, qualifications, consent, blind independence or scoring accuracy**.

## 1. Local credentials
Keep all secrets and the reviewer registry outside the Git repository in a directory protected by suitable OS permissions. PRIVATE_DIR is a placeholder.

    python scripts/reviewer_credentials.py init --registry PRIVATE_DIR/reviewers.json --admin-token-output PRIVATE_DIR/admin.token
    python scripts/reviewer_credentials.py enroll --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --reviewer-id teacher_01 --token-output PRIVATE_DIR/teacher_01.token
    python scripts/reviewer_credentials.py check --registry PRIVATE_DIR/reviewers.json --reviewer-id teacher_01 --token-file PRIVATE_DIR/teacher_01.token

The registry stores salted PBKDF2-HMAC-SHA256 verifiers rather than cleartext secrets. Reviewer and administrator tokens are separately generated and guarded. POSIX secret-file modes are checked, while Windows ACL management remains an administrator responsibility.

    python scripts/reviewer_credentials.py revoke --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --reviewer-id teacher_01

Revocation blocks future local authentication; it does not retroactively invalidate past reviews.

## 2. Protect a fresh learner state
Create a normal learner state first. Existing appeals cannot be retroactively authenticated.

    python scripts/qa.py audit-init --state .qa-state.json --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --audit-key-output PRIVATE_DIR/audit.key

Protected appeal resolution must now authenticate a locally enrolled reviewer and supply the separate HMAC key. The old self-declared --reviewer-confirmed flag cannot bypass this mode.

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason possible_key_error --audit-key-file PRIVATE_DIR/audit.key
    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason key_verified --new-score 1 --registry PRIVATE_DIR/reviewers.json --reviewer-id teacher_01 --reviewer-token-file PRIVATE_DIR/teacher_01.token --audit-key-file PRIVATE_DIR/audit.key

A real reviewer still needs to inspect the original response and marking rubric. Existing criterion-score arrays require complete consistent corrections, not arbitrary total-score overrides.

## 3. Verify integrity and store independent receipts

    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key
    python scripts/qa.py audit-checkpoint --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key --output PRIVATE_DIR/checkpoint-0001.json
    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key --checkpoint PRIVATE_DIR/checkpoint-0001.json

HMAC-SHA256 links each opened or resolved appeal to the preceding record and detects edits without the audit secret. **Without an independently retained trusted receipt, full-state rollback/deletion cannot reliably be detected.** Anyone obtaining the shared audit key may recompute valid MACs. A checkpoint refers to a specific record version; retain older receipts and make new ones after later legitimate changes.

HMAC is shared-secret authentication, **not** an asymmetric non-repudiable legal signature. Protected rollback requires --acknowledge-audit-rollback and the audit key, and managed deletion requires --acknowledge-audit-deletion. These remain intentional administrator actions, not forensic-grade immutable storage.

No real human study has taken place. Actual institutional approval, qualified assessors, protected student responses and applicable guardian/student consent remain external requirements. Consult docs/REVIEW_TRIAL.md and docs/REFERENCE_PILOT.md.
