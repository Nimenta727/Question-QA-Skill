# Question-QA-Skill — Core 轻量版 / Lightweight Core

适合兼容 Agent Skills 的日常 AI 学习：**默认只读取 `SKILL.md`**，需要具体策略时按需读取 `references/`。Core 无 Python、自动模型API调用、学生状态、历史研发和测试文件。

## 中文快速开始

1. 解压并注册 Core 文件夹，或让助手读取 `SKILL.md`。
2. 提供有权使用、能够实际读取的课件，再输入：“根据课件一次只问一道题，检查我的推理，并选择更有区分力的下一问。回答前不显示答案。”
3. QUICK 追问必要时读 `references/tutoring.md`，DEEP 命题读 `references/authoring.md`，有审题疑点读 `references/model_audit.md`，特殊学科条件读 `references/subjects.md`。

**必须守住的边界：** 新题与追问题先独立求解、找其他正确答案和反例；来源未核对不可冒称老师课件；仅有同模型自审不能说成独立审核；正确一题不能说明长期掌握。正式考试需要合格真人复核。

要运行离线 `scripts/qa.py`、严格审核JSON门禁、测试或研究脚本，请安装单独的 **Full** 发行包 `question-qa-skill-1.2.1.zip`。Full有当前文档、研发记录与研究结果；更早废弃的文档通过 Git 提交历史查看。压缩包大小不代表精确模型Token用量。

**许可证：MIT。** 不上传学生隐私、未经授权的教材或审核凭据。

---

## English quick start

Core is the smallest self-contained Agent Skill for conversational tutoring. Register the folder or ask the assistant to read `SKILL.md`. Do **not** load all references automatically: use `references/tutoring.md` for adaptive QUICK decisions, `references/authoring.md` for DEEP writing, `references/model_audit.md` for difficult reviews and `references/subjects.md` for discipline-specific constraints.

Example: “Use the course excerpts I provide. Ask one question at a time, check my reasoning, and select a distinct informative follow-up. Withhold the key until I answer.”

Review every newly authored or revised item before showing it. Label missing-course questions as general practice, disclose same-model self-review, and never infer durable mastery from one response. The separate **Full** ZIP (`question-qa-skill-1.2.1.zip`) contains optional Python 3.9+ offline tools and current documentation; superseded instructions remain in Git history. Core itself does not call an LLM or guarantee a fixed billable-token reduction. MIT licensed.
