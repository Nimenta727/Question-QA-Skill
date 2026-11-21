# 严格审题与证据门禁｜当前 v1.2.0

[深度命题规则](../references/authoring.md) · [模型执行协议](../references/model_audit.md) · [下一阶段验证方案](QUALITY_VALIDATION.zh-CN.md)

**所有新题、修改后的题以及追问题**都需要先独立求解、主动找错，确认无未解决关键问题后才能展示给学生。没有真正独立的审核过程，不能声称“已由独立审核模型确认”。

## 两阶段审题

1. **先盲解：** 审阅者获得学生题面、选项和已经实际核对的课程资料，**隐藏命题者答案与评分细则**；独立解答并寻找不同合法答案、漏条件、多解、反例、来源不符及歧义，保留首轮证据。
2. **再逆向审查：** 打开作者标准答案，对每个选项或 rubric 条目逐一质疑，同时核实原文引用、范围、认知层次、公平性和题族独立性。修改题面或答案后必须重新审题。

每题九项必查：`source_scope` 来源与范围、`independent_solution` 独立解答、`answer_and_equivalents` 等价及多解、`ambiguity_and_conditions` 条件与歧义、`options_or_rubric` 逐项干扰项或评分细则、`diagnostic_value` 诊断价值、`cognitive_alignment` 认知层次、`fairness_and_accessibility` 公平与可及性、`novelty` 题族独立性。任何关键项 **fail、uncertain、证据不足或未解决风险都必须拦截**，修订后重新审。

## Full 版离线门禁（不自动调用模型）

~~~bash
python scripts/model_audit.py BANK.json --template audit.json --source-file COURSE.txt --author-id author-agent
# 必须由实际独立审核者先盲解并填写审阅记录
python scripts/model_audit.py BANK.json --review audit.json --source-file COURSE.txt --require-course
python scripts/qa.py next BANK.json --state .qa-state.json --require-model-audit --model-audit audit.json --audit-source-file COURSE.txt --require-course-audit
~~~

`COURSE.txt` 必须来自有权使用并实际读取的 UTF-8 教材内容，保留可追溯出处。验证器检查题库与来源 SHA256、引文存在、记录结构、有限客观答案一致性以及未处理风险；修改题库或来源会使旧审核失效。没有真实课件时只允许标注 `general_practice` 通用练习，不能伪造老师课件出处。

**不能混淆的边界：** SHA256 只能证明文件字节匹配；作者/审核者 ID 是自我声明，不能证明独立身份；填写完整的 JSON 仍可能有错误推理。同一模型自审必须如实说明，高风险正式考试还需具备资质的独立真人审核。
