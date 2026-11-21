# Question-QA-Skill｜深度命题 · 自适应快问快答 · 严格审题

[English](README.md) · [文档导航](docs/INDEX.zh-CN.md) · [更新记录](CHANGELOG.md)

**一句话：** 让 AI 依据真实课程出有深度但公平的问题，学生每答一题就根据**可观察的理解证据**决定下一问。一次只问一题，默认六轮；不能凭一次正确或错误就判断长期掌握。

## 选哪个发行包？

| 发行包 | 内容 | 适合 |
|---|---|---|
| **Core 轻量版（推荐）**：\`question-qa-skill-core-1.2.0.zip\` | 一个简短SKILL与4份**按需读取**的教学参考；不含脚本、测试或历史研究 | 平时直接和AI聊天，优先节省Token |
| **Full 完整版**：\`question-qa-skill-1.2.0.zip\` | Core教学说明 + 离线Python题库工具、严格审题JSON门禁、全部测试、文档与开发记录 | 需要本地题库、学习记录、开发和研究工具 |

两个ZIP都有固定SHA256清单；**体积小不等于模型一定只消耗这些Token**。实际成本取决于宿主如何加载Skill及每轮教材/问答长度。安装后通常只需先读 \`SKILL.md\`，详见 [Token与结构优化](docs/TOKEN_BUDGET.zh-CN.md)。

## 30 秒开始

1. 到 [Releases](https://github.com/Nimenta727/Question-QA-Skill/releases) 下载Core或Full并校验 \`SHA256SUMS.txt\`。
2. 解压，把目录注册为兼容 Agent Skills 的Skill；不支持Skills的助手也可以直接阅读其中 \`SKILL.md\`。
3. 把课件交给助手，输入：“依据我提供的课程内容考考我，先问一题，答后再追问。不能编造超纲内容或在提问前泄漏答案。”

其他示例：“根据课件设计五道有区分度的深度题，交卷前不提供答案。”“我不理解C语言指针，请用最多六个问题找出我的推理缺口。”

## 教学与审题规则

- **QUICK**：错且原因不明→追问推导；猜对或借助提示→换题族无提示核对；部分正确→追缺失步骤；解释充分→应用与迁移。
- **DEEP**：先由课程断言建立题目蓝图，核验可解性、答案等价形式、认知层次和公平性。
- **严格审题**：新题、修改题及追问题展示前先独立求解、找多解与反例、检查实际教材出处及干扰项/rubric。若有无法解决的疑点，修题或更换；只有一个模型时不能冒称独立审阅。
- **克制诊断**：正确不等于掌握、旧启发式不是校准概率、合成软件测试不是教学效果评估。高风险正式考试需专业人员核验。

详细工作协议通过 \`references/authoring.md\`、\`references/tutoring.md\`、\`references/model_audit.md\` **按需**加载，不应每轮全部读取。

## Full版：可选本地命令行

Python 3.9+，不需要pip依赖，也不会自行调用LLM：

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

题库审阅可使用 \`scripts/model_audit.py\`；它检查审核记录、来源和少量客观一致性，不能代替实际模型独立求解或教师审查。参考 [完整安装说明](docs/INSTALL.zh-CN.md) 与 [严格审题说明](docs/MODEL_AUDIT.zh-CN.md)。

## 项目状态与研发边界

核心Skill已有跨平台软件回归，**真实课程命题质量、知识漏洞判断和学习效果尚需独立实测**。仓库另有双开发Agent流程的独立PR，但这属于改进项目的方法，**不是学生每轮必须调用两个模型**；未完成的独立审阅不应写成已审核通过。

许可证 MIT；不要将真实学生记录、未获授权的课程源文件或审核凭据放进公开仓库。
