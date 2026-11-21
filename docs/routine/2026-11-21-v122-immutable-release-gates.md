# 2026-11-21 — v1.2.2 versioning and release smoke gate for compact evaluation report

## Actual changes
- Bump `VERSION` and Skill metadata to 1.2.2; sync source/packaging CI, release script ZIP names, release tag name, immutable-tag guard, expected source release notes and extraction root to 1.2.2.
- Add the optional `scripts/skill_eval_report.py` and bilingual guides to the **Full required** modules, leaving the Core allowlist unchanged.
- Produce `dist/skill-eval-demo.html` **only from a named synthetic fixture** and include it in SHA256SUMS, CI artifact upload and GitHub release attachments.
- On freshly extracted Full ZIP, run the renderer and assert the English synthetic banner, summary details and static HTML. Keep the existing Core extraction budget, ZIP hash and complete Python test suite intact.
- Add `docs/RELEASE_NOTES_v1.2.2.md` with the feature and explicit non-claims.

## Next
1. Extend regression to ensure the renderer/fixture exists only in Full and not Core; verify bilingual README/installation/release links and real-test NOT RUN status.
2. Complete PR review and six-platform tests, then merge.
3. Confirm the release workflow *actually* publishes v1.2.2 and check the five assets and SHA256 list before announcing availability. No real teacher/model studies are implied.
