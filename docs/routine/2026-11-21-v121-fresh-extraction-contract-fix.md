# 2026-11-21 — v1.2.1 Full extraction release blocker

## Root cause and change
- The main-branch v1.2.1 release workflow passed the Ubuntu/macOS/Windows release gates but failed in the freshly extracted Full ZIP regression.
- `test_release_contract.py` assumed that `.github/workflows/*.yml` was present even though the Full ZIP intentionally excludes `.github/`. That mismatch is an archive-vs-repository test boundary, not evidence of a diagnosis algorithm failure.
- Skip only the workflow-YAML *source inspection* test when the workflow file is absent in an extracted distribution. Preserve all source-checkout assertions and add a separate release-notes-in-package assertion that continues to execute inside the ZIP.
- Do not ship GitHub workflow sources in Full and do not weaken Core/Full manifest or extraction gates.

## Validation and next steps
1. Run the six-platform pull request test matrix and new release platform/extraction verification.
2. Keep the published v1.2.0 artifacts immutable; allow v1.2.1 only after verified source checkout and extracted Full suite succeed.
3. Check the actual tag, four release assets and SHA256 before claiming publication.
4. Follow up with a **separate** compact real-model evaluation report feature; no synthetic record should be misrepresented as a real model trial.
