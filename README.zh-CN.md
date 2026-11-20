# Question-QA-Skill｜深度出题与学习诊断

[English](README.md)

项目目标不是“多出几道题”，而是：**根据课程内容形成有深度、公允、能够诊断具体知识漏洞的题目，并以快问快答追踪学习进展。**

## v0.4.0 已发行功能 / P2 完整升级

新增 **完全离线的中英文学习分析看板**（先修知识图谱、知识点覆盖、认知层次、误区、历史变化、逐项主观题评分、复习日期）和 **学生回答评估机制**。主观题必须先由教师或 Agent 核对真实回答，并按照每项 rubric 填写具体证据、部分分与改进建议；短答等价答案可以在审阅后纠正。不会把自由文本原文写入状态文件或看板。

一键生成合成演示看板：

    python3 scripts/dashboard.py examples/sample_bank.json --state examples/demo_state.json --output demo-dashboard.html --lang zh

正式 ZIP 发行包可复现构建并含 SHA256 文件清单。完整使用方法：[中文安装与评卷](docs/INSTALL.zh-CN.md) / [English guide](docs/INSTALL.md)；[发行与校验](docs/RELEASE.md)；[更新记录](CHANGELOG.md)。

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
诊断系统会检查**独立题族、不同日期、认知层次及高阶应用/迁移证据**：至少有多次独立回答才可能产生稳定的暂定判断，同题刷分和同一天连续正确不能直接证明掌握。即时表现、信心和答题速度不能被当成能力的确定证明；状态是用于制定下一轮练习的参考，而非标准化测评分数。

## v0.2｜诊断精度与可信度升级

- **独立题族**：同一道题的不同表述可共用 family 标识；同一天重复作答只采纳该题族最后一次结果，不会通过刷同题虚增证据。
- **知识点 × 认知层次**：分别展示理解、应用、分析和迁移的证据，不把基础记忆题答对等同于深度掌握。
- **延迟复测**：同一天连续答对不算长期保持；暂时较强的结论需要跨日期复测，但跨日期本身也不能保证长期记忆。
- **猜测和提示处理**：答对但猜测、借助提示，其证据权重更低；高信心答错标记为需要澄清的信号。
- **误区定位**：可按错误选项绑定经过人工/AI 审校的误区标签，避免凭一道错题编造心理或知识缺陷。
- **快问快答**：答错优先补先修/对比，猜对优先另一题型验证，确信答对则迁移或扩大覆盖，单次会话不重复原题。
- **上限和终止**：默认快问快答6题、深入测试5题，可设置1–20题；题库耗尽会明确结束。
- **分层报告**：输出当前表现、证据题数、独立题族、跨日期、认知层次、疑似误区以及未测知识点。

注意：rate 是工程上透明的形成性证据索引，**不是掌握概率，也不是标准化成绩**；真实预测精度需要收集经过授权和匿名化的答题数据后验证。

完整实现与局限：[诊断引擎说明](docs/DIAGNOSIS.md)。

## 低 Token 设计
入口 SKILL.md 紧凑；按任务只加载命题/诊断/相应学科规则。运行脚本在本地评分与汇总，避免每轮让模型重新阅读题库和长历史。无需多 Agent 调度或额外模型调用。

## 文件说明
SKILL.md（主协议）、references/（按需规则）、scripts/qa.py（本地评分状态）、examples/（演示题库）、docs/FORMAT.md（数据格式）、docs/RESEARCH.md（学术依据）、docs/routine/（逐次更新记录）、tests/（测试）。

## 注意
如果教材、试题原文或老师板书没有提供，不能声称“基于老师原题”。生成题目还需要在发布之前审校其公平性和唯一答案；脚本的 JSON 校验不等于学术事实查证。请把 .qa-state.json 保存在本地、不要提交到仓库。

MIT 许可证。后续规划见 docs/ROADMAP.md。离线构建：python3 scripts/build_release.py --output dist；其后运行 --verify 检查包中 SHA256。

## 真实数据验证（2026-11-20）

已实现基于 FORGET-SE 独立期末考试的可复现评测。在测试组30名学生、279项学生×知识点期末目标上，v0.2 诊断指数跨知识点 AUC 为 **0.515**，低于周测平均 **0.700** 和知识点先验 **0.757**；同知识点内部指数 AUC **0.554**，周测均分 **0.551**，差值区间包含零。**当前没有证实预测优势，暂不添加 BKT/IRT。** 这不否认形成性追问规则的设计价值，但尚不能宣称其测量效度。

详细依据与局限：[中文验证报告](docs/VALIDATION.zh-CN.md) / [English validation](docs/VALIDATION.md)；原始学生作答没有被提交到本仓库。


## v0.5.0｜命题质量验证与第二独立数据实测

新增离线命题检查器：检测重复/高度相似题、错误数字答案键、数值等价选项、主观题评分标准重复、异常来源锚点。数学自动验证只支持安全且范围明确的有理数四则运算，不声称解决所有代数/逻辑证明。来源、歧义、超纲、公平等必须由真正独立的教师或专业审阅者确认；可建立与题库SHA256绑定的审核模板。

    python3 scripts/question_quality.py examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json
    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

请不要直接把自动生成的模板改成“全部通过”；只有逐题核验后才可以填写。详见 [命题质量使用说明](docs/QUESTION_QUALITY.zh-CN.md)。

**第二份真实数据评测**：ASSISTments 2015 数学练习，测试集包含280名有效预测学习者、5728次下一题作答。v0.2诊断指数AUC **0.620**，低于简单历史成绩基线 **0.710**。当前无法证实指数具备预测优势，因此继续不加入 BKT/IRT。详见 [第二队列中文报告](docs/VALIDATION_ASSIST2015.zh-CN.md) / [英文](docs/VALIDATION_ASSIST2015.md)。这不同于此前 FORGET-SE 的期末考试预测任务，不能直接比较两个AUC大小。
