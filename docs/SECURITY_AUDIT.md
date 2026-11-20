# v0.9.0 locally verified reviewer capabilities and HMAC appeal audit

This version introduces local reviewer credential verification and an HMAC-linked appeal ledger. These are **tamper-evident under limited local trust assumptions**, not verified real-world identity, a qualified teacher directory, a public-key signature scheme or immutable storage.

## Register local capabilities

    python scripts/reviewer_credentials.py init --registry .qa-reviewers.json --admin-token-output .qa-admin.token
    python scripts/reviewer_credentials.py enroll --registry .qa-reviewers.json --admin-token-file .qa-admin.token --reviewer-id teacher-A --token-output .qa-teacher-A.token
    python scripts/reviewer_credentials.py check --registry .qa-reviewers.json --reviewer-id teacher-A --token-file .qa-teacher-A.token

A trusted local administrator must independently verify that the intended reviewer actually holds the assigned token and meets the required qualification, separation and consent rules. Reviewer tokens are 32-byte random secrets; the registry stores salted PBKDF2-HMAC verifiers, not token plaintext. Keep token files separate from the repository and learner state. On POSIX credential files must not be accessible to group/world; on Windows configure and inspect OS ACLs separately. Revocation:

    python scripts/reviewer_credentials.py revoke --registry .qa-reviewers.json --admin-token-file .qa-admin.token --reviewer-id teacher-A

## Protect a learner state (before any appeal has been opened)

    python scripts/qa.py audit-init --state .qa-state.json --registry .qa-reviewers.json --admin-token-file .qa-admin.token --audit-key-output .qa-audit-key.hex

The audit key is a random separate 32-byte HMAC secret, NEVER stored in learner state or any release asset. The state gains an audit chain and a separately authenticated .audit-policy marker to prevent silently stripping the metadata and reverting to legacy self-declared grading. Previously opened appeals cannot be retroactively claimed as verified; use a fresh state or an institutionally reviewed migration outside this tool.

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason rubric_dispute --audit-key-file .qa-audit-key.hex
    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason rubric_rechecked --new-score 1 --registry .qa-reviewers.json --reviewer-id teacher-A --reviewer-token-file .qa-teacher-A.token --audit-key-file .qa-audit-key.hex

An active registered reviewer token and the corresponding HMAC key are mandatory in protected mode; the legacy --reviewer-confirmed boolean cannot bypass either. Corrected rubric-scored items still require a complete revised --criterion-scores array. Legacy states remain usable but their approval is explicitly labeled self_declared_not_authenticated, not verified identity.

## Tamper and rollback checking

    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file .qa-audit-key.hex
    python scripts/qa.py audit-checkpoint --state .qa-state.json --audit-key-file .qa-audit-key.hex --output /separately/protected/checkpoint.json
    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file .qa-audit-key.hex --checkpoint /separately/protected/checkpoint.json

Each signed appeal record commits to its monotonic sequence, previous MAC, appeal snapshot and current effective grade; the verifier checks the chain and consistency with the current appeal metadata and corresponding events. A separately retained signed checkpoint contains the chain length/head and helps detect **replacement of the entire state by an older, otherwise valid signed snapshot**. It must be stored and retained separately from the state/backups. Checkpoint file creation never overwrites an existing file.

Protected rollback requires both --acknowledge-audit-rollback and --audit-key-file, and the destination must itself be a valid signed chain from the same reviewer registry. A previously retained independent checkpoint can still reveal the rollback. Protected deletion requires --acknowledge-audit-deletion in addition to the usual confirmation; external keys and receipts are deliberately not erased.

## Security boundaries and caution
- Possession of a locally enrolled secret does **not** establish a reviewer’s real name, institution, expertise or actual independent work. The trusted admin and operating system remain inside the trust boundary.
- An attacker holding the HMAC key can forge MACs; anyone able to delete both the state and all independent receipts can destroy the audit evidence. This is not cryptographically immutable, and there is no trusted timestamp or remote notary.
- Only appeal-related events and the grade they correct are authenticated, not every historical response, source question or private original student answer.
- state-check is not an HMAC verifier. Use audit-verify for protected integrity checks.
- Keep the admin token, reviewer secrets, audit key, reviewer registry and receipts private; exclude all from version control and release packages. High-stakes educational processes still require qualified external review and an independent appeals pathway.
