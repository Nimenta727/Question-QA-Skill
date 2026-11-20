# Question-QA-Skill v0.4.0 / 发行说明

The first packaged, offline release includes:
- A bilingual HTML learning dashboard: knowledge/prerequisite map, concept coverage, response history, evidence gaps, cognitive level scores, reviewed mistake labels, criterion-level manual assessment and review suggestions.
- Rubric-based student-answer evaluation with per-criterion evidence, feedback and partial scores. Automatic objective grading remains deterministic; semantic equivalence requires explicit reviewer confirmation.
- Reproducible release ZIP, embedded per-file SHA256 manifest, SHA256SUMS.txt, fresh-extraction smoke test, and bilingual installation guides.
- Public real-data validation disclosures: the current formative index has NOT demonstrated a reliable advantage in external exam prediction. No calibrated BKT/IRT is shipped.
- Offline Python 3.9+ standard library only; no analytics trackers, private learner data, remote fonts or external runtime.

中文提示：逐项评估证据必须由教师或 Agent 对照学生真实回答审核。生成的 HTML 仅呈现汇总学习证据，不包含题库标准答案。请勿把本项目中的推测性指数当作精确的掌握概率。

Start with docs/INSTALL.zh-CN.md or docs/INSTALL.md. License: MIT.
