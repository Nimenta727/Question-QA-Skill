# 2026-11-20 — v0.6 诊断三引擎职责分离 / Evidence, prediction, adaptive choice

## 本次改动
- 新增 scripts/evidence_engine.py：基于现有保守诊断规则输出独立证据题族、跨日、多认知层次、较高认知层次有效作答、风险信号和证据缺口；显式标明非概率/非预测。
- 新增 scripts/prediction_engine.py：只从历史得分计算固定平滑均分 baseline，与证据充分性完全分离；并明确这不是经过数据校准的掌握概率，没有在真实保留测试集上调参。
- 新增 scripts/adaptive_engine.py：保留 v0.2 已有选题策略，不改现有优先级公式，但为每道自动选取的题目记录覆盖、错题后跟进、不确信确认、独立题族等理由代码，标注并非随机对照试验证实的收益。
- qa.py 的 next 输出 selection 解释且 pending 保存相同解释以支持稳定重复查询；answer 和 report 新增 evidence_profile/prediction_baseline，继续保留旧 status/rate 兼容既有 API。
- 本次完全不修改已经用两份独立真实测试集评估过的 v0.2 指数，保证历史复现有效，不将两组测试集用于新参数调优。

## 下一步规划
1. 添加对“零历史/证据不足/近期错误/不确定猜测/无答案泄漏”的单元与端到端测试。
2. 新增双语说明，解释并行三引擎职责与统计限制。
3. 加入 Windows 和 macOS CI 验收；通过独立新版本发行工作流输出可核验包。
