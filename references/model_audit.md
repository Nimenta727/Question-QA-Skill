# Strict item audit / 严格审题（按需加载）

**什么时候读？** DEEP深度命题、题目正确性存疑、正式题库审核；日常QUICK先按SKILL.md中的简短审题门槛执行。

## 两阶段模型审题
**阶段1：盲解。** 审核模型只接触学生题面、选项、实际教材和目标知识；**不要给标准答案、作者解析或评分rubric**。要求其独立求解，找多解、反例、缺失条件、别的合理解释和来源疑点，保存首轮结论。没有独立模型则明确为同模型自审。

**阶段2：反向审查。** 再看作者答案/rubric，与首轮结果对照，逐题确认九项，各项必须有具体证据，不能只填“看起来正确”：
1. source_scope：课件真实原文/章节与考核范围。
2. independent_solution：独立求解与必要前提。
3. answer_and_equivalents：答案、等价形式、多解；单选必须唯一。
4. ambiguity_and_conditions：变量域、单位、时间、定义、歧义。
5. options_or_rubric：**每个**错误选项的排除理由，或**每条**开放题rubric与替代解法。
6. diagnostic_value：能否区别理解与猜测/记忆。
7. cognitive_alignment：任务实际要求的认知层次与难度。
8. fairness_and_accessibility：超纲、偏怪、不必要语言或背景偏差。
9. novelty：是否仅换数字/表述，没有增加独立证据。

**任一失败、不确定或无法核对 → 不出题，先修订再重审。** 不能虚构老师课件，也不能因为同一模型写了两个角色名就宣称真正独立审阅。

## Full版离线审核（仅在实际需要且已有人/模型填写审阅文件时）
~~~bash
python scripts/model_audit.py BANK.json --template audit.json --source-file COURSE.txt --author-id author
# 由真正另外一次审核模型调用完成盲解和逐项审核后：
python scripts/model_audit.py BANK.json --review audit.json --source-file COURSE.txt --require-course
python scripts/qa.py next BANK.json --state .qa-state.json --require-model-audit --model-audit audit.json --audit-source-file COURSE.txt --require-course-audit
~~~
无真实课程文件只允许明确标注通用练习，不可宣称课程已核对。题库/来源一变，SHA256失配必须重审。审核表默认全部未通过；程序**不自行调用LLM**，只核对结构、文件哈希、逐字引文及少量客观答案，不能证明每条语义判断都真。官方高风险考试仍需合格人类审阅。
