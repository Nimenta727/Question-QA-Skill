# 真实评测专区（Full 专属）

**状态：三项全部 NOT RUN（未执行）。** 此处集中存放真实模型评测的协议、空白清单与后续经授权的汇总证据，不放学生答案或未授权课程全文。

| 专项 | 协议 | 核心问题 | 状态 |
| --- | --- | --- | --- |
| 真实课程命题质量 | [course_quality.md](course_quality.md) | 真正读取获许可课件后，题目正确、可追溯、公平吗？ | **未执行** |
| 独立审题漏检与误报 | [audit_detection.md](audit_detection.md) | 审题模型真正发现错误原因，同时不会乱拦正确题吗？ | **未执行** |
| 自适应追问 vs 固定题序 | [adaptive_baseline.md](adaptive_baseline.md) | 同样的学生推理和模型预算下，自适应追问的信息价值更高吗？ | **未执行** |

[English](README.md) · [空白运行元数据](run_manifest.template.json) · [结果存放规则](results/README.md) · [Full 精简报告](../SKILL_EVAL_REPORT.zh-CN.md)

**执行顺序：** 确认课程授权与合法使用范围 → 冻结题族、对照题和预注册指标 → 独立专家先标注正确答案/缺陷 → 真实模型加载 Skill 完成测试 → 盲评与分歧裁决 → 按分子/分母统计 → 生成脱敏的离线 HTML。

**严格区分：** 合成样例只能验证软件；离线追问重放只能比较策略选择，不能证明真实学习收益。Core 不包含此专区。
