# 2026-11-20 — 验证协议边界测试 / Causal evaluation regression

## 本次改动 / Changes
- 新增 tests/test_evaluate.py：测试学生隔离划分、滚动预测无法看到当前答案、概念独立、AUC/Brier/ECE计算、bootstrap、重复行、输入异常、ASSISTments过滤与隐私。
- 修正 scripts/evaluate.py 的两项评估安全细节：移除无效的空循环；混合有时间戳与无时间戳的数据不再允许以补造日期参与间隔复测判断。
- 测试数据均为代码生成的合成数据，仅用于检查评测协议，不用于证明诊断预测精度。

## 下一步 / Next steps
1. 运行 CI 并修复失败。
2. 更新双语实验手册，明确真实数据的输入、授权、数据导出与暂未验证项。
3. 再评估是否具备可靠开展 BKT/IRT 标定的证据。
