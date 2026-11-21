# Skill 测试后精简报告面板（仅 Full 版）

[English](SKILL_EVAL_REPORT.md) · [真实模型测试矩阵](REAL_MODEL_TESTS.zh-CN.md) · [状态台账](TEST_STATUS.zh-CN.md)

**这是离线报告生成器，不会自动执行模型或证明教学效果。** 必须先由真实模型加载 Skill、完成冻结的测试案例，再由有权限的独立评阅流程登记参考标准和真实耗时/Token，最后才由 Full 工具根据脱敏 JSON 生成 HTML。没有执行的测试不能通过面板“变成已完成”。

## 合成演示（不是真实模型成绩）

~~~bash
python scripts/skill_eval_report.py examples/synthetic_skill_eval.json \
  --output dist/skill-eval-demo.html --lang zh \
  --summary dist/skill-eval-demo-summary.json
~~~

样例**完全合成，没有模型调用或真实学生答案**，页面持续明确标注合成演示。Python 3.9+ 标准库即可运行，无第三方包、联网脚本或外部样式；Core 不加载报表工具。

## 只显示有用的三个指标

默认最多显示：**真实缺陷识别率、正确题放行率、追问目标与专家标准一致率**。每项必须有分子和分母。少于 5 个合格样本不显示百分比；只有至少 5 条且全部来自不同题族时才给 Wilson 95% 二项比例近似区间。它**不是学生掌握程度的置信度**。

其下优先呈现错题被放行、好题误拦、拦截却没识别正确错误、待裁决和追问目标偏差。最多一张四类别的小型缺陷条形图，其余详情（仅用例编号、时延/Token 覆盖、来源与限制）通过折叠区域按需打开。不做一屏塞满所有图表的“驾驶舱”，也不把缺失测量显示成 0%。

## 输入数据的严格要求

根对象只能有 `schema_version`（整数 1）、`run`、`cases`，文件上限 2 MB、2500 条；多余字段直接拒绝，以免把姓名、学生原文或教师课件传给报表。

`run` 必填字符串：`id`、`mode`（`synthetic_demo` 合成、`actual_model` 真实模型）、`reference`（合成只能用 `synthetic_labels`；真实用 `expert_adjudicated`、`model_only` 或 `none`）、`model`、`commit`、`dataset`、`date`。审核身份仍是用户提交的声明，程序不能认证真实独立性。

每条 `case` 需要 `id`、`test_id`（RM-01～12）、`family` 题族和 `kind`：
- `audit`：`truth` 是 `defective` / `sound` / `unknown`，`decision` 是 `block` / `accept` / `uncertain`，可填写 `defect` 缺陷类别。**对缺陷题的拦截必须填写布尔 `caught_actual_defect`**。只有它为 true、即独立参考确认模型真正指出该缺陷，才计为检出；“乱拒绝但没找对错因”不计成功。好题须被正确放行。
- `tutoring`：`expected_action`、`selected_action` 取 `clarify`（澄清）、`recheck`（复测）、`repair`（补缺）、`transfer`（迁移）、`stop`（结束）或 null。只有真实参考动作存在且一致才计成功。

可选 `input_tokens`、`output_tokens`（实测非负整数）、`latency_ms`（实测非负有限值）；未测留空并注明覆盖数。少于20条时不报告P95时延。严禁记录原始学生答案、私人资料或课件全文。HTML 会转义用户标识，并限制页面网络/脚本资源。

`actual_model` 如果只有 `model_only` / `none`，即使模型自称“审核准确”也**不显示质量比例**。`expert_adjudicated` 只表示提交者声称已独立评阅，程序不能验证身份。同题族重复不报独立样本置信区间。任何报告都不能解释成终身掌握概率或因果学习收益。

## 参考的成熟评测思想

- [OpenAI 模型评测最佳实践](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：任务级真实评价与标准化打分。
- [Anthropic Agent 评测](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：代码、模型与人工评价分层和失败分析。
- [AERA/APA/NCME 教育测试标准](https://www.apa.org/science/programs/testing/standards)：效度、信度和公平。
- [NIST 测量框架](https://airc.nist.gov/airmf-resources/playbook/measure/) 及 [二项比例区间](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbici.htm)：样本量与不确定性。
- [Google PAIR 可解释性设计](https://pair.withgoogle.com/guidebook-v2/chapter/explainability-trust/)：渐进式呈现，不误导信任。
- [Evidently 报告体系](https://docs-old.evidentlyai.com/user-guide/tests-and-reports/introduction)：把数据质量、实际表现和监控分开。这里不引入其代码依赖。

下一阶段先按 [RM-01～RM-12](REAL_MODEL_TESTS.zh-CN.md) 真正运行测试并获得独立标准。**目前这些实验仍未执行**，合成报告仅用于检验面板本身。
