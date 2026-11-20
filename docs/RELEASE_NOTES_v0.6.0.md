# Question-QA-Skill v0.6.0 / 评估智能与诊断架构

- Double-reviewer open-response evaluation contract with per-criterion verbatim evidence, partial scores, specific feedback, agreement summary and mandatory distinct third-reviewer arbitration for differences; disputed answers stay pending until resolved.
- New --response-file option reduces shell-history exposure of private student responses; state retains only numeric scores, reviewer agreement rate and dispute counts. The local program cannot automatically validate arbitrary semantic correctness.
- Separated formative evidence, fixed historical-score comparison and adaptive-choice explanations. Preserved already-evaluated v0.2 inference and selection policy for reproducibility; never claim fitted mastery probabilities.
- Cross-platform CI on Ubuntu, Windows and macOS for Python 3.9 and 3.12. Distribution is checked for SHA256 integrity and smoke-tested after fresh extraction. Official v0.6.0 gets its own immutable Git tag and GitHub Release; main updates cannot replace an existing asset in place.
- Source-anchored question-quality checks and the two independent real-data studies remain in place. Findings did not show robust predictive advantage over simple baselines. Reviewer agreement does NOT prove educational truth or independent human identity.

中文：此次核心是有证据的双审阅及争议仲裁、诊断三模块分离和跨平台不可变发行。原始学生答卷、身份、引文和评语均不持久化到本地学习状态。请阅读 docs/ASSESSMENT.zh-CN.md、docs/ARCHITECTURE.md 和 docs/RELEASE.md。
