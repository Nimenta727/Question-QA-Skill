# 2026-11-20 — CLI 接入诊断 v0.2 / Wire diagnostics to CLI

## 本次改动 / Changes
- 把 scripts/diagnosis.py 接入现有出题、答题和报告命令，保留原有客观题与 rubric 评分。
- 新增 start 会话与 --focus、--limit；题目用尽或达到题数上限明确停止。
- 题库格式增加可选题族、先修概念和选项误区标签；答题历史记录题族、认知层次、猜测、提示及错误类别，不记录原始回答。
- report 增加概念级与认知层次级证据及未测知识点支持。

## 下一步 / Next steps
1. 修复旧测试与新诊断门槛的不一致，并补充适配性测试。
2. 更新双语文档和示例。
3. GitHub Actions Python 3.9 / 3.12 验证。
