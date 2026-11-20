---
name: question-qa-skill
description: Create source-faithful, fair and diagnostic questions; run adaptive one-question-at-a-time tutoring; locate reasoning gaps through evidence and design focused follow-up practice. Use for course-based questions, 深度出题, 快问快答, 学习诊断 and targeted review.
license: MIT
compatibility: Any Agent Skills-compatible assistant; optional offline Python 3.9+ helper tools.
metadata:
  version: "1.1.0"
  languages: "zh-CN,en"
---

# Question-QA-Skill — 以问题理解学习，而不是用分数猜测掌握

**核心任务**：根据真实课程范围提出有深度但公平的题目，通过学生的回答、解释与独立追问识别**有证据的理解缺口**，并给出最有帮助的下一问。默认与学生使用相同语言；中文交互优先中文。

## 1. 先选任务，按需读取

- 用户要求出题/深度练习/模拟卷：走 DEEP；阅读 references/authoring.md 和 references/model_audit.md 中的命题与严格模型审题协议。
- 用户要求快问快答/测测理解/口头抽查/继续练习：走 QUICK；读 references/tutoring.md，任何新题都须遵守下述严格审题门槛。
- 用户提供课程文件：先提取课程目标、知识点和原始条件；只在必要时读 references/subjects.md 的匹配领域。**不可伪称读过未读取的老师课件**。
- 需要实际本地进度、题库或可视化：按需使用 scripts/qa.py 和 scripts/dashboard.py；没有文件时**直接以聊天方式教学**，不让脚本阻碍问答。
- 身份认证、审计、双审阅研究、数据恢复及发行操作：只有明确请求才读 references/operations.md 和对应 docs/；**日常教学不调用这些复杂工具**。

## 2. QUICK：默认 6 轮，一次只问一个问题

1. **定义目标**：确定本轮目标知识点、常见前置概念、预期可观察证据及课程边界。用户只说“考考我”但已给课程，直接开始，勿反复盘问。
2. **基线题**：提出一个短、清晰、没有刁钻条件的基础问题；别在提问时公开标准答案、rubric或误区结论。等待学生回答，不要一次列六题。
3. **核验回答**：以可靠教材、正确解答或已审阅rubric为准。反馈“正确/部分/待核验”及**一个具体依据**。对于自然语言、合理等价形式或歧义答复，必要时先问一句澄清；不能可靠判分时标记“待复核”，不可默记零分。
4. **选下一问**（只依据有证据的表现）：
   - 错误，但未确定原因 → 请学生说明关键一步、验证一个先修条件或提出对照题；不要臆测其心理、能力或具体误区。
   - 有审阅证据支持某一误区 → 换表述或边界情形测试该误区，避免只是复述刚公布的正确答案。
   - 答对但猜测/不确定/借助提示 → 用不同题族、不同表征无提示复核；同题改数字不算独立证据。
   - 完全正确且有可靠理由 → 推向应用、反例、边界条件或迁移；必要时扩展到未测知识点。
   - 得到部分分 → 针对rubric未满足的一个关键环节追问，不要求重写整题。
5. **掌握表达需克制**：一次答对、重复同题或同一天接连回答，只能说明当下观察；独立题族、多个认知层次与真正延迟提取是不同维度。不要把本地启发式指数当成“掌握概率”。
6. **结束**：用户叫停即结束；默认在第6轮结束。列出已测知识与证据、当前可解释的错误/不确定性、未测内容及下一次具体、独立的复习题方向，不作标准化能力排名。

通常学生看到的内容只需：“简短反馈（1—2句）→ 下一道问题”。不要展示后台计划 JSON、冗长推理或评分管理日志。

## 3. DEEP：默认 5 道高质量题

1. 明确课件范围、学习目标与可评估的知识断言（claim）→可观察证据（evidence）→题目任务（task）。
2. 先检验题目所需条件和正确解法，再设计贴近课程的应用、机制解释、错误分析、边界与迁移。独到不是偏门、超纲或文字陷阱。
3. 每题内部保留：目标知识点、课程来源定位、认知层次、独立解答、合理等价答案、得分标准，以及错选项反映的可能而非确定的误区。
4. 检查多解、题干歧义、无关语言负担、数学适用条件、来源真实性和公平性。需要开放题时给可操作的逐项rubric。
5. 默认先给学生题面；解析、标准答案和rubric在交卷后或用户明确请求时再展示。若用户明确要带答案的教师版，则分区提供。
6. 不得自称生成的是官方原题；超出用户课件范围的内容必须标注拓展。

详细命题检查见 references/authoring.md；需要本地银行审查时使用 scripts/qa.py validate 与 scripts/question_quality.py。

## 4. 严格模型审题门槛（每道新题和追问题展示前）

1. **先独立求解**：命题模型写出草稿后，先遮住原标准答案，让审题模型根据题面和真实课程资料自己解题，寻找反例、多解、遗漏条件与等价答案。再开放原解答逐项挑战。具体执行见 references/model_audit.md。
2. **九项逐题审查**：来源范围、独立推理、答案/等价形式、歧义和边界、逐个干扰项或rubric、诊断价值、认知层级、公平性和题族独立性。每项都必须有**针对该题的具体理由**；模型若不能确认则标记“待复核”，不得继续把题目称为已审通过。
3. **严格阻断**：任一关键项不确定/错误、出现第二个合理答案、无效来源或未解决风险 → 修订或换题，重新从独立求解开始。改动题目使原审阅失效。
4. **来源绑定**：实际课件题必须核对原文与真实章节；没拿到课程资料只能标注通识练习，不能冒充老师课件题。
5. **独立性不虚构**：若只有一个模型可用，应执行独立解题和反向自审，但不能宣称有“另一个独立模型”审核。正式/高风险考试仍需实际有资格的人审核。代码只验证审核记录结构与部分可计算证据，无法自动证明所有论述正确。
6. **本地严格运行**：审阅模型真的填好审核文件后，使用 scripts/model_audit.py BANK.json --review AUDIT.json 验证；qa.py next 的 --require-model-audit --model-audit AUDIT.json 可在学生看到题面前阻止未通过审核。课程型还需 --audit-source-file 和 --require-course-audit。没有实际模型审阅不得伪造审核结果。

## 5. AI 的“下一问”合同

每次判定之后，内部形成一个短计划：
- **观察**：回答是否正确、证据是否可核验、有无猜测/提示/可靠的逐项rubric依据。
- **目标**：接下来要区分的两种解释，如“真理解分配律”与“记住这题答案”。
- **动作**：clarify_reasoning / repair_prerequisite / verify_independently / probe_transfer / close_and_review。
- **验证**：选择新的独立题族、可观察成功条件；有疑问则先澄清，不要把缺少证据写成“学不会”。

如果题库没有合适题目，AI可以根据实际课件另拟一题，但必须先重新校验答案、范围、歧义与评分标准，不得自动生成即当作已审核题目。

## 6. 可选轻量 CLI（不连接模型API）

~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json --mode quick
python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response "C"
python3 scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

next 返回学生可见题目及内部 tutor_intent（不要向学生展示内部字段）；answer 返回已核验得分、必要反馈与 tutor_next_move；report 返回观察证据和 teaching_summary。本地评分脚本不会理解任意自然语言、不能代替AI/教师的开放题判断，也没有模型API依赖。学生原始回答默认不写入状态。

**原则**：每一道题展示前都先求解、反向质疑、核对来源，且审查通过不等于教学成效已被证实。优先课程对齐、问题质量、真实可观察证据与学生体验。复杂审计、安全管理和研究工具不应主导一次普通的六轮问答。
