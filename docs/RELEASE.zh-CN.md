# 正式发行与完整性校验｜v1.2.1

[文档导航](INDEX.zh-CN.md) · [正式发行](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.1) · [Token策略](TOKEN_BUDGET.zh-CN.md)

**v1.2.1 维护版发行：** GitHub Actions 需要先通过跨平台测试、双包可重复构建、全新解压和 SHA256 校验，才会创建不可变 Tag。是否发布成功应核实 GitHub Release 的真实附件；预期包含：

- `question-qa-skill-core-1.2.1.zip`：轻量提示 Skill、4 份按需参考及基本清单。
- `question-qa-skill-1.2.1.zip`：兼容的 Python 3.9+ 离线题库、审核和研发工具。
- `SHA256SUMS.txt`：两个 ZIP 和 `demo-dashboard.html` 的外部 SHA256 校验记录。
- `demo-dashboard.html`：合成示例的离线可视化，**不是已证实的教学有效性报告**。

## 构建与复验

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.1.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.1.zip
python -m unittest discover -s tests -v
~~~

构建器锁定 ZIP 内部条目顺序和时间信息；`manifest.json` 对每个文件做摘要记录。Core 严格限制允许文件，Full 核验重要评分、状态、审计模块；CI 对发行包进行全新解压复验，旧发行 Tag 和附件不会因为文档整理而改变。

下载时应以 Release 提供的 `SHA256SUMS.txt` 核对下载 ZIP 的 SHA256。**校验和只能证明文件完整性**，无法证明题目答案准确、模型真正独立审题或学生能力变化。

## 隐私与历史

禁止在公开发行中包含真实学生信息、未授权的课程原文、审核者凭据/密钥与私人审题包。默认 Core 只加载 `SKILL.md`，不应把全部研发资料塞入普通课堂对话。更早版本的安装与发行方案查阅 [Git Tags](https://github.com/Nimenta727/Question-QA-Skill/tags) 和 [Git 提交历史](https://github.com/Nimenta727/Question-QA-Skill/commits/main/)；本次主分支文档更新**不会修改已发布 v1.2.1 的 ZIP**。

## 真实模型测试与发行CI分开

参见 [12项真实测试矩阵](REAL_MODEL_TESTS.zh-CN.md) 与 [验证状态台账](TEST_STATUS.zh-CN.md)。发行门禁只能证明包完整性、兼容性和现有测试通过，**不等于**独立模型审题正确率、长期掌握概率或教学增益。没有真实实验记录前全部 RM 项保持“未执行”。
