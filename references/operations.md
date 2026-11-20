# 按需使用的非核心模块 / Optional operations

普通 QUICK/DEEP 教学不需要读取本文或调用下列模块。只在用户明确要求时进入；历史实现与全部细节已在原有docs/及Git历史中保留。

| 额外需求 | 对应文档/脚本 | 使用边界 |
|---|---|---|
| 题目质量检查、独立命题审核 | scripts/question_quality.py，docs/QUESTION_QUALITY.zh-CN.md | 静态检查不是教学效度 |
| 数据证据、外部实证研究 | docs/VALIDATION.zh-CN.md，docs/VALIDATION_ASSIST2015.zh-CN.md | 现有指数未证明优于简单历史基线 |
| 主观题双审阅、仲裁 | docs/ASSESSMENT.zh-CN.md | 需要实际独立复核，不能凭身份自声明 |
| 评分申诉 | docs/APPEALS.zh-CN.md | 真实教育责任由教师与机构负责 |
| 学习数据备份、导出和删除 | docs/DATA_LIFECYCLE.zh-CN.md | 本地删除不是安全擦除 |
| 本地审核凭据、HMAC审计 | docs/SECURITY_AUDIT.zh-CN.md | 不是现实实名验证或绝对不可修改的账本 |
| 经授权的研究准备 | docs/REVIEW_TRIAL.zh-CN.md，docs/REVIEWER_STUDY.zh-CN.md | 必须另获授权，合成流程不代表真人研究 |
| 打包发行 | scripts/build_release.py，docs/RELEASE.md | 严格排除私人学习记录 |

核心边界：Agent默认只需命题→学生作答→可靠证据→单个追问。运维和审计模块不参与日常教学，避免无效上下文成本。


## v1.1.0 strict AI question verification
New and edited items intended for students must follow references/model_audit.md first: the reviewing model independently solves **before** viewing the author's proposed answer, then challenges each option/rubric, source and diagnostic rationale. For a real separate reviewing-model packet, scripts/model_audit.py validates required evidence, the entire bank/source SHA256 and exact quotations, and qa.py next --require-model-audit --model-audit FILE blocks failed/incomplete reviews. This is core *pedagogical safety*, not a reviewer identity platform. It cannot by itself prove semantic truth or run another model API; qualified human review is still needed for formal examinations. See docs/MODEL_AUDIT.zh-CN.md.
