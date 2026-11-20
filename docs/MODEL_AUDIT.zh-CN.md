# v1.1.0 模型严格审题

目标是让AI对每道题进行独立求解、主动找错和课程来源核对，而不是“所有检查项勾选通过”。

## 必查九项
1. 课程来源与适用范围：教材真实出处、逐字引文、有没有超出实际课件。
2. 独立解答：先隐藏命题者答案，审阅模型独立推导、计算和寻找反例。
3. 答案与等价形式：找第二个正确选项、其他合法解法或合理表达。
4. 歧义与条件：定义域、单位、量纲、边界、前提是否完整。
5. 干扰项或rubric：单选三个错误选项逐个说明错误及区分力；开放题每条rubric独立审查。
6. 诊断价值：是否能区分真正理解与猜对/重复记忆。
7. 认知层次：题目标注的理解、分析或迁移是否真实要求该层推理。
8. 公平性：偏怪、误导性语言、无关文化背景或隐含先修要求。
9. 题族独立性：避免换数字、改写题干却不增加新证据。

任何关键项 fail/uncertain 或证据不足，都不能向学生声称已核验。修改后需要重新审计。

## 两阶段审阅
第一阶段：审核模型只看到实际课件、学生题面和选项，隐藏命题者答案与rubric结论。它先自行解题，枚举等价解、反例和边界条件；结果应在打开标准答案前保存。

第二阶段：打开命题者答案、解析和评分细则，逐题质疑，并填写每项具体审查理由、课程引文、独立答案、干扰项解释和遗留风险。不要凭泛泛“这道题很好”就通过。

## 离线工具（真正审核由AI执行）

    python3 scripts/qa.py validate BANK.json
    python3 scripts/question_quality.py BANK.json
    python3 scripts/model_audit.py BANK.json --template audit.json --source-file COURSE.txt --author-id author-agent

模板初始全部为未审核。交给真实另一次运行的模型执行独立复核并填写后：

    python3 scripts/model_audit.py BANK.json --review audit.json --source-file COURSE.txt --require-course
    python3 scripts/qa.py next BANK.json --state .qa-state.json --require-model-audit --model-audit audit.json --audit-source-file COURSE.txt --require-course-audit

课程source文件应从已读取的课件中提取授权的UTF-8文本，保留页码等定位。来源摘要和题库内容通过SHA256绑定；题目或来源一旦变化旧审核失效。无课件只能按general_practice处理，不能冒称老师的课程题。

CLI并没有自动调用语言模型。只有Agent真的执行过审题才能形成真实模型审阅记录。两个不同审核ID只是自我声明，不是独立身份证明；同一模型自查也不等于外部独立审核。正式考试、成绩认定仍需有专业能力的真人核验。仅有形状完整的审计JSON，不证明里面的推理正确。

完整执行指令参见 references/model_audit.md。
