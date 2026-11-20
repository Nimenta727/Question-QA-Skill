# v0.7.0 concurrency-safe local state and last-good recovery

All CLI actions involving one state path now hold an OS-native advisory exclusive lock for the entire read/modify/write transaction: fcntl.flock on Linux/macOS, msvcrt.locking on Windows. The lock sidecar STATE.lock is intentionally never deleted because unlinking it could split the lock domain. Locks are released on process exit. Contending processes retry briefly, then fail with a clear busy error. Local filesystems only; not a distributed lock for cloud sync or networked storage.

Each new write validates the previous JSON state, atomically saves its bytes as STATE.bak, and atomically replaces the primary state using a same-directory file with flush/fsync. An invalid primary cannot overwrite a known-good previous backup. The .bak is **one prior committed snapshot**; restoring can discard the newest completed action. This is not multi-version retention or a database WAL.

CLI:
    python scripts/qa.py state-check --state .qa-state.json
    python scripts/qa.py state-recover --state .qa-state.json --confirm

The check reports status, counts and hashes only, not source text. Recovery requires explicit confirmation and preserves backup contents. Protect both primary and backup with local account permissions. Do not publish them. A private state file can still contain sensitive learning behavior even though the system does not persist raw student answers. No cloud migration, external write coordination or power-loss consistency on every filesystem is claimed.


## v0.9.0 protected rollback and retention
When learner state has an authenticated appeal audit, restoring an earlier snapshot additionally requires --acknowledge-audit-rollback and --audit-key-file and rejects a snapshot without the same signed reviewer-registry binding. External checkpoint receipts can detect rollback to an older valid signed audit chain. Protected local deletion also requires --acknowledge-audit-deletion. The HMAC key, reviewer credential files, policy marker and independent checkpoints are security-sensitive; see docs/SECURITY_AUDIT.md. This is local authenticity checking, not immutable storage or cloud erasure.
