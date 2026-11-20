# v0.8.0 learner state retention, controlled export and deletion

A local state file contains scores, concepts, timestamps and appeal records. Even without raw student answers these are potentially sensitive learning data.

In addition to state.json.bak, each successful modification now retains a rolling set of at most five prior valid snapshots under state.json.snapshots/. State commits and recoveries use OS-native locks and atomic replace. Lock sidecars (state.json.lock) are intentionally persistent to prevent split locking.

    python scripts/qa.py state-snapshots --state .qa-state.json
    python scripts/qa.py state-recover --state .qa-state.json --snapshot SNAPSHOT_ID --confirm

Without --snapshot recovery still uses the previous .bak. Rollbacks may discard *all* completed actions newer than the chosen snapshot; current valid state is additionally snapshotted before recovery.

Aggregate-only export by default:

    python scripts/qa.py state-export --state .qa-state.json --output qa-export-summary.json

Full private learner state requires explicit opt-in:

    python scripts/qa.py state-export --state .qa-state.json --output qa-export-private.json --include-private --confirm-private

Exports never overwrite existing targets and may not target the primary state, backup, lock or managed snapshot directory. Even aggregate statistics can be sensitive in tiny cohorts. Secure the exported files yourself.

Explicit local deletion:

    python scripts/qa.py state-delete --state .qa-state.json --confirm-delete DELETE-LOCAL

Removes the managed primary, .bak and generated snapshots under the state lock, but not the persistent lock file, external/cloud backups, exported copies, operating system remnants or other files. This is ordinary unlink, **not cryptographic or forensic erasure**. Follow applicable institutional retention and student privacy policies when working with real records.
