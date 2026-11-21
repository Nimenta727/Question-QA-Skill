# 正式发行与完整性校验｜v1.2.0

[文档导航](INDEX.zh-CN.md) · [正式发行](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0) · [Token策略](TOKEN_BUDGET.zh-CN.md)

**2026 年 11 月 21 日已正式发布。** 首次 Core 解压烟测脚本问题修复后，跨平台测试与不可变发行工作流已成功；GitHub Release 实际包含：

- `question-qa-skill-core-1.2.0.zip`：轻量提示 Skill、4 份按需参考及基本清单。
- `question-qa-skill-1.2.0.zip`：兼容的 Python 3.9+ 离线题库、审核和研发工具。
- `SHA256SUMS.txt`：两个 ZIP 和 `demo-dashboard.html` 的外部 SHA256 校验记录。
- `demo-dashboard.html`：合成示例的离线可视化，**不是已证实的教学有效性报告**。

## 构建与复验

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.0.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.0.zip
python -m unittest discover -s tests -v
~~~

构建器锁定 ZIP 内部条目顺序和时间信息；`manifest.json` 对每个文件做摘要记录。Core 严格限制允许文件，Full 核验重要评分、状态、审计模块；CI 对发行包进行全新解压复验，旧发行 Tag 和附件不会因为文档整理而改变。

下载时应以 Release 提供的 `SHA256SUMS.txt` 核对下载 ZIP 的 SHA256。**校验和只能证明文件完整性**，无法证明题目答案准确、模型真正独立审题或学生能力变化。

## 隐私与历史

禁止在公开发行中包含真实学生信息、未授权的课程原文、审核者凭据/密钥与私人审题包。默认 Core 只加载 `SKILL.md`，不应把全部研发资料塞入普通课堂对话。更早版本的安装与发行方案查阅 [Git Tags](https://github.com/Nimenta727/Question-QA-Skill/tags) 和 [Git 提交历史](https://github.com/Nimenta727/Question-QA-Skill/commits/main/)；本次主分支文档更新**不会修改已发布 v1.2.0 的 ZIP**。
