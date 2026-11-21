# v1.2.0 — Core and Full distributions (2026-11-21)

**Release published:** [v1.2.0](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0). After correcting the Core extraction smoke-test indentation, both the cross-platform test matrix and immutable release workflow completed successfully.

## Delivered in the published artifacts

- **Core:** `question-qa-skill-core-1.2.0.zip`, containing concise `SKILL.md`, four on-demand pedagogical references, README, VERSION, LICENSE and `manifest.json`.
- **Full:** `question-qa-skill-1.2.0.zip`, containing the compatible offline Python toolkit, tests, research evidence and (at release time) historical documentation.
- **Verification:** deterministic ZIP builds, per-file SHA256 manifests and released `SHA256SUMS.txt` for both archives and the synthetic HTML dashboard.
- **Context:** at release, `SKILL.md` was approximately 1,965 Unicode characters versus roughly 4,018 previously. This is a source-character reduction, **not** a measured model-token reduction.

## What was not established by this release

The release did not train or calibrate a mastery model, run real LLM calls in the offline CLI, independently verify each authored question, or demonstrate better learner outcomes. The nine-point review remains a required model/author procedure; `scripts/model_audit.py` checks an **already-filled** evidence record, not the semantic truth of its reasoning. High-stakes uses still require an independent qualified reviewer.

## Post-release main-branch maintenance

Subsequent main-branch documentation now focuses on current operation and validation tasks. Superseded installation/release narratives are being removed **from the current tree only**, while their content remains recoverable from the immutable v1.2.0 release assets, prior commits and historical tags. Updating main documentation does **not** modify the already published ZIP files or tag. Current guides: [English](INDEX.md) / [中文](INDEX.zh-CN.md).
