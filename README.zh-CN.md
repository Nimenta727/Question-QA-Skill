# Question-QA-Skill｜深入命题、快问快答与学习漏洞诊断

[English](README.md)

> **一套让 AI 先问好问题，再根据回答追问的轻量 Skill。** 它不是考试管理平台，也不会凭一个数字宣称学生“已经掌握”。

## 直接使用：无需先启动脚本

把仓库作为 Agent Skills 兼容的 Skill 安装在 AI 助手中，或者让助手读取 SKILL.md，就可以提出：

- **快问快答**：“根据我这节数据结构课，给我做六轮学习诊断。一次只问一道题，答完再追问。”
- **针对薄弱点**：“我总是分不清队列和栈，先测一题，然后根据我的回答判断该追问哪一步。”
- **深度命题**：“根据老师的课件出五道有区分度但不偏不怪的题，交卷前不要展示答案。”
- **继续练习**：“别重复上一道题，换一种表征验证我是不是真的理解。”

**QUICK** 默认六轮，一次一问；**DEEP** 默认五道，先按课程来源和评分标准设计，避免超纲或死记细节。用户随时可以叫停。

## AI 如何做出下一问

| 学生表现 | 正确的教学动作 |
|---|---|
| 答错但原因还不确定 | 先要求说明步骤或验证前置知识，**不能臆测误区** |
| 答对但猜测、借助提示 | 同一知识点换不同题族，无提示再确认 |
| 答对且有可靠解释 | 问应用、反例、边界条件或迁移 |
| 只满足部分评分标准 | 只追问关键的缺失环节 |
| 题库缺题 | 根据课件生成并**重新验收**一个新变式，而不是直接承诺其正确性 |

技能入口 [SKILL.md](SKILL.md) 已精简为日常教学合同；详细追问策略在 [references/tutoring.md](references/tutoring.md)，深度命题标准在 [references/authoring.md](references/authoring.md)。

## 可选：离线题库、进度与可解释追问

无需额外依赖，Python 3.9+ 即可：

~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python3 scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

现在 next 输出安全的题面和内部教学意图 tutor_intent；answer 输出得分、依据和 tutor_next_move；report 包含本轮 teaching_summary，指出已测、未测和独立证据不足的内容。上述内部字段不应直接展示给学生；Agent应把它转成简洁反馈和**一道**下一问。

它不会自动理解任意文字答案。主观题需使用教师或 AI 审阅的明确 rubric；无法独立核验时应先澄清或标记“待复核”，而不是擅自判零。示例题库为**合成代数题，不是老师真实课件**。

## 可靠性边界

- 一题正确 ≠ 已掌握；猜对、提示后正确和同题改数字都不是独立掌握证据。
- 描述性证据指数不是掌握概率。既有外部真实数据验证未证实旧启发式诊断明显优于简单历史成绩基线；不要夸大。
- 自动测试可验证软件对答错/猜对等场景选择了正确分支，**不能证明真实 AI 出题质量、学生学习收益或教育测评效度**。人工审题、校验真实课程和独立教学评估依然重要。

[教学质量人工评估协议](docs/TEACHING_EVALUATION.zh-CN.md) · [研究事实与限制](docs/VALIDATION.zh-CN.md) · [版本记录](CHANGELOG.md)

## 已有高级工具，默认不参与教学

此前的双审阅、申诉、安全审计、备份、研究工作流及离线看板均保留。只有确实需要时才按 [references/operations.md](references/operations.md) 找到相应工具和说明。安全与数据管理不应该增加普通六轮答题的复杂度。

代码使用 MIT 许可证；日常 Skill 不依赖网络服务。若处理真实学生记录，务必本地妥善保护数据与必要授权。
