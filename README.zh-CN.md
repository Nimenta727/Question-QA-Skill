# Question-QA-Skill｜深度出题与学习诊断

[English](README.md)

项目目标不是“多出几道题”，而是：**根据课程内容形成有深度、公允、能够诊断具体知识漏洞的题目，并以快问快答追踪学习进展。**

## 两种工作模式
- **深度命题 DEEP**：对齐教材/老师讲授的知识点，强调原理、过程、条件、边界、反例、迁移。独到不等于刁钻；题干必须给够条件，答案必须可核验。默认5题。
- **快问快答 QUICK**：默认6轮，一次只问一道题。答对则提高认知层级或换知识点；答错则追问前置概念；猜对时换表述确认。结束给出证据数量、薄弱点、未测内容和复习顺序。
- **本地诊断**：脚本负责题库验证、出题选择、客观题批改、人工评分记录、复习日期。没有外部 API 调用。它本身不替代大模型创作/查证题目。

## 用法
把本项目作为兼容 Agent Skills 规范的 Skill 安装到 AI 助手中，然后直接说：

> 根据这节课的教材出5道深度题，禁止超纲或偏题，解析在交卷后给。

> 对“函数”的定义与应用做6轮快问快答，一次只提一个问题，最后给我知识点诊断。

本地演示（Python 3.9+，零第三方依赖）：

~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json --mode quick
python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C --confidence sure
python3 scripts/qa.py report --state .qa-state.json
python3 -m unittest discover -s tests -v
~~~

开放题须对照 rubric 评分，并传入 --score 0/0.5/1 和 --reason；本地不会假装自动理解任意自然语言表达。选择/填空题的客观评分则完全离线运行。

## 为什么不会轻易给出“已掌握”
每个知识点 × 能力层次，至少需要**3次答题证据且涉及2个不同题目**才能获得初步判断；否则显示“证据不足”。即时表现、信心和答题速度不能被当成能力的确定证明；状态是用于制定下一轮练习的参考，而非标准化测评分数。

## 低 Token 设计
入口 SKILL.md 紧凑；按任务只加载命题/诊断/相应学科规则。运行脚本在本地评分与汇总，避免每轮让模型重新阅读题库和长历史。无需多 Agent 调度或额外模型调用。

## 文件说明
SKILL.md（主协议）、references/（按需规则）、scripts/qa.py（本地评分状态）、examples/（演示题库）、docs/FORMAT.md（数据格式）、docs/RESEARCH.md（学术依据）、docs/routine/（逐次更新记录）、tests/（测试）。

## 注意
如果教材、试题原文或老师板书没有提供，不能声称“基于老师原题”。生成题目还需要在发布之前审校其公平性和唯一答案；脚本的 JSON 校验不等于学术事实查证。请把 .qa-state.json 保存在本地、不要提交到仓库。

MIT 许可证。后续规划见 docs/ROADMAP.md。
