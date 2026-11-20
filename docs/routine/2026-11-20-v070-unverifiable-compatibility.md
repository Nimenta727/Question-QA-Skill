# 2026-11-20 — 安全数学判分与旧评分API兼容 / Unverifiable-answer contract

## 本次改动
- GitHub旧版测试直接调用grade(short, "seven")，要求得到(0,method)元组；新增数学自动验证最初在不可解析语义输入上直接抛异常，不兼容旧库调用。
- 调整 grade 仅负责返回0与math_equivalence_unverified标记；真正的CLI handle_answer才阻止将“无法验证”记为错误答案，并保留pending供人工独立审核。旧API测试可以继续获取数值结果，但新CLI仍阻止误判学生。
- answer_equivalence仅允许明确声明在short题，拒绝manual/single意外放宽自动评分。
- 测试修复：多重圆括号不会增加AST深度，改用深层加法树验证递归限制，确保确实覆盖危险输入而非误测。

## 下一步规划
1. 完整跨系统回归，确认旧接口不受破坏且无法解析的自然语言答案不被误判并提交。
2. 进一步验证Windows本地锁、备份与学生记录隐私。
3. 补协议文档与正式版 v0.7.0 发行。
