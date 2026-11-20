# 2026-11-20 — 双语评分手册、诊断架构及合成样例 / Examples and architecture

## 本次改动
- 新增 ASSESSMENT.zh-CN.md / ASSESSMENT.md，完整说明双人审核的JSON格式、学生原文证据的逐字校验、必须第三方仲裁的条件、隐私以及尚未真实验证的独立性。
- 新增 ARCHITECTURE.md，说明三个模块职责、算法未改动、历史基线未标定及已有两份真实数据测试无法验证的潜在掌握效果。
- 新增完全合成的 sample_student_answer.txt、sample_dual_review.json、sample_adjudication.json，示例两名审阅者在ALG-004一道标准上出现分歧、第三方依据rubric给出最终分数。
- 新增双语发行说明 RELEASE_NOTES_v0.6.0.md；实际源代码严格限制持久化数据只包括数值统计，不保存审阅者姓名、答卷原文或论证细节。

## 下一步规划
1. 核实示例在待答题ALG-004时可直接通过CLI的双人仲裁路径。
2. 运行全部六种OS/Python组合，修复跨平台问题。
3. 在所有发行检查通过后核对不可变tag的实际提交与Release资产SHA256。
