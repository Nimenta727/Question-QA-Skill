# 命题质量审查 / v0.5.0

设计目标：区分“程序能证明的形式与数值一致性”和“必须由独立审阅者确认的教育质量”。**通过静态检测不等于答案真实、没有歧义、没有超纲或绝对公平。**

## 本地使用（Python3.9+，零依赖）

从项目根目录运行：

    python3 scripts/qa.py validate examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --output quality-audit.json

输出 JSON 只含题目ID、风险代码、严重程度、计数、题库SHA256。不输出标准答案、学生答题、题干，也不触发外部 API。

### 可自动验证
- 基础 JSON 结构、单选选项与唯一答案键、非空解析/来源/评分标准（通过原有 qa.py）。
- 精确重复题干、较长题干的高相似度重复提示、跨知识点复用题族、重复开放题评分规则、可疑过短解释及异常来源锚点。
- 可选的数值题见证。给题库的单选/简答字段添加 verification，格式：

    "verification": {"kind": "arithmetic", "expression": "(19-4)/3"}

该表达式只支持有界的整数/小数与加减乘除，通过 AST+Fraction 精确计算，检查数值是否等于正确选项或简答答案；也排查与正确选项数值等价的干扰项。**不是通用数学证明器**：不能执行代码或函数，也不能证明题干里的真实前提、量纲、答案推导或命题公平。没有证明字段时保持“未提供确定性见证”的信息标记。

### 需要人工/Agent独立审阅

    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json

创建对应当前题库字节 SHA256 的模板，全部检查项初始为 false。请按源教材或验证过的知识确定每道题的：
- answer_verified：答案、适用条件和合理其他答案。
- source_verified：题目声称的来源确实存在且指向正确知识。
- scope_checked：契合课程目标、没有引入未经教授的前提。
- ambiguity_checked：有足够条件、措辞明确，单选不存在多解。
- fairness_checked：不以语言、文化偏见或冷门技巧伪装深度。
- rubric_checked：每个评分维度确实能够区分应得分与不应得分的回答。
- reviewer：可追责的实际审阅者代号或身份；limitations：遗留问题。

审阅结束后：

    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

只有题库哈希一致、每个项目都已确认且没有硬错误时，严格模式才通过。任何修改题目都使先前审核记录失效。**审核是对审阅工作有记录，不是加密签名，也不意味着审阅者本身一定正确。**

## 结果解释与发布门槛

error：不允许作为已通过题库发布；warning：必须查阅并记录风险决定；info：仅为未支持或需了解的情况。若没有独立审核，默认状态是 review_required，**不是通过审查**。

建议命题流程：对照教学目标 → 出题与独立解题 → 自动质量审查 → 教师或另一个审核代理对照教材检查 → 严格审核门槛 → 发布给学生。对数学证明题、复杂文字题、事实题，应由有相应专业能力的人确认。不能让同一个模型的自我肯定冒充独立证据。

## 限制
- 近重复识别只是文本相似启发式，不能发现所有改写题或所有同题族。
- 当前 deterministic witness 仅覆盖简单有理数算术，不验证方程唯一根、向量/几何证明或自然语言语义。
- 审核记录不能证明实际审阅者已阅读教材。当前系统无数字签名和双盲一致性度量。
- 本工具审查题目质量，不代替学生诊断精度/公平性验证。学生评分另见 docs/INSTALL.zh-CN.md。


## v1.1 模型语义审题补充
question_quality.py负责静态错误与算术见证，仍然不能理解整道题。新脚本model_audit.py要求另一轮真实模型审核产生逐题九项的实质依据，并用课件引文、文件SHA256、独立答案、全部干扰项或rubric分析作为门槛，失败则停止发布题目。详细见 docs/MODEL_AUDIT.zh-CN.md。程序不会主动调用LLM，也不能证明每个模型理由都是真的；正式考试需真人专业复核。
