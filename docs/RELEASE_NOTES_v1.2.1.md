# Question-QA-Skill v1.2.1 — Release readiness and real-test handoff

**Type:** maintenance/documentation release, based on the verified v1.2.0 Core/Full Skill. The v1.2.0 Git tag and release assets are not modified.

## Delivered
- Reissue the latest consolidated bilingual README, installation, architecture, diagnosis and review documents in the signed-off Full distribution.
- Update current Core/Full distribution version identifiers, release automation and cross-platform test expectations to 1.2.1.
- Document concrete **still-required** independent model/question/diagnosis testing, review evidence, sample-splitting, defect categories, metrics, privacy rules and acceptance reporting; label those plans as **NOT RUN**.
- Preserve Core lazy-loading and the offline Python API/diagnostic semantics. No external model is called by the package.

## Verification expected before publication
- Python 3.9/3.12 cross-platform suite on Ubuntu, Windows and macOS.
- Release-specific platform gate, deterministic Core and Full ZIP verification and fresh-extraction smoke tests.
- SHA256SUMS for both ZIPs and the synthetic dashboard, current-main SHA check, and immutable new v1.2.1 Git tag/assets.
- Actual release availability and asset names/sizes must be checked after CI; a PR pass alone is not a published release.

## Evidence boundary
This release makes no new claim of real model item-authoring accuracy, reviewer sensitivity/specificity, student learning gain, retained mastery or measured Token reductions. CI verifies engineering behavior, not educational truth. Human/independent review is still outstanding under the documented future protocol.

[中文测试与状态](TEST_STATUS.zh-CN.md) · [Full validation protocol](QUALITY_VALIDATION.md) · [Release details](RELEASE.md)
