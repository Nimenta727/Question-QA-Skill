# 安装与校验｜v1.2.3

[首页](../README.zh-CN.md) · [文档目录](INDEX.zh-CN.md) · [正式发行](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.3)

## Core：日常学习推荐
1. 在**已发布**的 v1.2.3 Release 中下载 `question-qa-skill-core-1.2.3.zip` 和 `SHA256SUMS.txt`。
2. 使用系统 SHA256 校验工具核对 ZIP 与清单中的摘要。
3. 解压并在兼容 Agent Skills 的助手中注册目录，或要求助手读取 `SKILL.md`。
4. **初始只读取 SKILL**；只有需要追问、深度命题、复杂审题或特殊学科时才分别读取对应 `references/` 文件。

示例：“依据我提供的 C 语言课件，一次问一道理解题，回答后检查我的思路再追问。” 未提供或未核对课件时，只能标注通用练习。

## Full：可选离线 Python 工具
下载 `question-qa-skill-1.2.3.zip`。使用 Python 3.9+，无额外 pip 依赖：

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

Windows 可使用 `py -3`。示例数据是合成的，不是真实学生实验。严格门禁需要外部独立审核者先完成记录；`scripts/model_audit.py` **不调用大模型**，仅校验记录的来源、格式与部分客观一致性。参阅 [模型审核](MODEL_AUDIT.zh-CN.md)。

## 完整性、隐私和历史
ZIP 内 `manifest.json` 按文件记录 SHA256，单独发布的 `SHA256SUMS.txt` 用于核对整个压缩包；构建与自动化测试参阅 [发行指南](RELEASE.zh-CN.md)。禁止把本地学生状态、未经授权的课程内容、审阅者凭据或密钥放进公开仓库。

旧安装方案通过 [Git Tags](https://github.com/Nimenta727/Question-QA-Skill/tags) 与 [Git 提交历史](https://github.com/Nimenta727/Question-QA-Skill/commits/main/) 查阅，不再与当前安装步骤混放。

## Full 测试后的精简报告

合成示例：`python scripts/skill_eval_report.py examples/synthetic_skill_eval.json --output dist/skill-eval-demo.html`。这**不是实际模型测试**；应先真正用 Skill 完成冻结测试并取得独立标准。参见 [报告指南](SKILL_EVAL_REPORT.zh-CN.md)。
