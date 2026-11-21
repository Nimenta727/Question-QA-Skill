# Question-QA-Skill v1.2.2 — compact evidence-aware post-Skill evaluation report

## New in Full
- Offline standard-library `scripts/skill_eval_report.py` converts **already recorded** Skill evaluations into a concise, local HTML report.
- Shows at most **three conditional indicators** (defect correctly detected, sound item accepted, target follow-up matched), with exact sample denominators and conservative small-sample/independent-family interval disclosure.
- Prioritizes wrong releases, false alarms, wrong-reason blocks, unresolved review and misdirected follow-ups; shows at most one compact defect-category graphic. Details, actual tokens and latency appear only when expanded.
- Defect detection requires an explicit reviewer-identified match to the **actual** flaw (`caught_actual_defect=true`), not merely blocking a question.
- Strict allowlisted input, HTML escaping, no network scripts, no raw student answers, no third-party packages. Correctness rates are **withheld without independent reference labels**.

## Distributions and evidence
- **Core** remains the minimal Skill prompt and on-demand references. It does not load a model-evaluation dashboard on each conversation.
- **Full** includes the script, bilingual guidance, unit tests, synthetic fixture and source-evidence limits.
- A new `skill-eval-demo.html` release attachment is generated from an **explicitly synthetic** fixture; its numbers are demonstration only, *never* measured real model performance.
- Two versioned ZIPs, `demo-dashboard.html`, the new synthetic report and `SHA256SUMS.txt` must pass full reproducible build, cross-platform CI and fresh-extraction smoke gates before publication. Existing v1.2.1 and earlier tags/assets remain immutable.

## Scientifically honest limits
- The offline renderer does **not** invoke any model, test live Skill invocations, identify experts, calibrate mastery probabilities or establish genuine learner gains.
- RM-01–RM-12 real-model and educator tests remain **NOT RUN** until separately executed and independently adjudicated.
- See [English guide](SKILL_EVAL_REPORT.md), [中文指南](SKILL_EVAL_REPORT.zh-CN.md), [real-model test cases](REAL_MODEL_TESTS.md) and [evidence ledger](TEST_STATUS.md).
