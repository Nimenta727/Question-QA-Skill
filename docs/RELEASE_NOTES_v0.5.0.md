# Question-QA-Skill v0.5.0 / 命题质量审查与第二数据集验证

- Added a dedicated offline question-quality auditor: detect exact and near-duplicate questions, suspicious source metadata, duplicate rubric criteria, cross-concept item-family reuse, and optional exact rational arithmetic contradictions (including numerically equivalent distractors).
- Independent review gate now creates a bank-SHA256-bound, all-false review template. Answer/source/scope/ambiguity/fairness/rubric confirmation must be supplied by a genuine reviewer before strict passing; no automatic claims of verified educational correctness.
- Added independent ASSISTments 2015 real mathematics next-response evaluation, with 708,631 public source records, learner-disjoint sample and replay, fixed Git blob hash, aggregate-only output and AUC/CI against simple baselines.
- Real held-out test (280 eligible students, 5,728 forecasts): v0.2 descriptive index AUC 0.620, below simple smoothed learner-history 0.710. Pooled difference CI entirely negative; within-skill macro difference CI overlaps zero. No verified long-term mastery labels available.
- Retains bilingual offline dashboard, reviewer-based student answer assessment, deterministic standard-library CLI and reproducible ZIP with SHA256 manifest.

中文重点：**质量审查能自动发现形式与数值错误，但不能代替独立教师审核。第二组真实数据再次没有支持启发式诊断指数比简单历史表现更准确。** 本版本不加入未经标定的 BKT/IRT，也不上传真实学生原始回答。

Install docs: docs/INSTALL.zh-CN.md / docs/INSTALL.md. Quality audit: docs/QUESTION_QUALITY.zh-CN.md / docs/QUESTION_QUALITY.md. Research: docs/VALIDATION_ASSIST2015.zh-CN.md / docs/VALIDATION_ASSIST2015.md.
