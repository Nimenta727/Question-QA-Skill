# Question-QA-Skill｜严谨命题与自适应学习诊断

**基于真实课件 · 一题一问 · 依据作答推理追问 · 审题结果可追溯**

[English](README.md) · [文档目录](docs/INDEX.zh-CN.md) · [v1.2.0 正式发行](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0) · [路线图](docs/ROADMAP.md)

本项目将普通问答升级为**有证据的形成性学习诊断**：先依据真正读到的材料编制题目，独立求解并检查题目，再根据学生的回答与推理选择下一问。它不是在线教育平台，也**不能仅凭一道题就认定学生已经掌握知识**。

## 选择安装版本

| 版本 | 推荐场景 | 内容 |
| --- | --- | --- |
| **Core 轻量版（推荐）**：`question-qa-skill-core-1.2.0.zip` | 平时直接与 AI 学习，降低初始上下文 | `SKILL.md`、4 份按需参考、简短 README、LICENSE、VERSION、校验清单 |
| **Full 完整版**：`question-qa-skill-1.2.0.zip` | 本地题库、诊断记录、审题凭证及项目研发 | Core + Python 3.9+ 标准库工具、示例、测试、中英文文档和研究证据 |

v1.2.0 已正式发布，两个 ZIP 及 `SHA256SUMS.txt` 都可在 [GitHub Releases](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0) 获取。下载后先核对 SHA256。**默认只把 `SKILL.md` 加入 AI 上下文**，出现具体需要时才读取参考资料；压缩包文件大小不能等同于实际 Token 消耗。[安装指南](docs/INSTALL.zh-CN.md) · [Token 策略](docs/TOKEN_BUDGET.zh-CN.md)

## 直接开始

1. 将 Core 解压目录注册到兼容 Agent Skills 的助手，或让助手先读取 `SKILL.md`。
2. 提供有权使用的课程课件，明确学科、范围及希望诊断的知识点。
3. 输入：**“根据我提供的课件一次只问一道题。每次回答后检查我的推理、简要反馈，再决定最有诊断价值的下一题。答题前不要显示答案。”**

**QUICK** 默认不超过六轮，允许随时停止；**DEEP** 生成少量有深度、有正确答案和课程依据的题目，并分开提供学生版与解析。没有实际读到课程文件时，只能标注为**通用练习**，不能虚构老师课件的出处。所有新题与改题都需要先求解，再检查多解、歧义、来源、干扰项或评分细则、公平性及诊断价值。

## Full 版：可选离线命令

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

离线工具**不会自行调用大模型**。`scripts/model_audit.py` 只能验证**已经填写的审核记录**之结构、来源与有限客观一致性，不能代替真实独立模型审题。[严格审题协议](docs/MODEL_AUDIT.zh-CN.md) · [当前架构](docs/ARCHITECTURE.md)

## 已完成与尚待验证

- **工程发行已验证：** 2026-11-21 的 v1.2.0 发行与跨平台自动测试通过；这不等于已经证实教学效果。
- **旧诊断指数未建立优越性：** 现有外部研究没有证明它优于简单历史表现基线；不要把启发式得分解释为经校准的掌握概率，也不能由一次答对推断长期保持。[实证结果](docs/VALIDATION.zh-CN.md)
- **真正需要验证：** 真实课件的命题准确率、模型审题漏检率与误报率、学习漏洞归因的可靠性、自适应追问相对固定题序的收益。[验收与评测方案](docs/QUALITY_VALIDATION.zh-CN.md)
- **双开发智能体：** 开发者与独立代码审计者服务于 GitHub 仓库研发，不代表每次学生答题必须调用两个模型；未真实执行的独立审阅不得宣称通过。

当前文档只描述有效设计；被替代的历史方案请查 [Git 提交历史](https://github.com/Nimenta727/Question-QA-Skill/commits/main/) 与 [Tags](https://github.com/Nimenta727/Question-QA-Skill/tags)。逐次研发记录保留在 `docs/routine/`。

**许可证：MIT。** 不上传真实学生隐私记录、未授权课程全文、审核凭据或密钥。高风险正式考试仍需有资质的真人复核。
