# 2026-11-20 — Windows 中文JSON控制台编码兼容 / Cross-platform Unicode output fix

## 本次改动
- GitHub Actions 在 Windows 2025 Python3.9/3.12 上发现 CLI 输出中文题干时发生 'charmap' codec can't encode 错误，Ubuntu/macOS 均通过。
- 将 scripts/qa.py 的所有标准输出JSON改为ensure_ascii=True（Unicode安全的ASCII转义），JSON消费者解析后仍能得到完整中文原文。原始学习状态写入仍使用UTF-8原文，不改变任何题库、评分、诊断算法或历史数据格式。
- 保留详细的六平台测试矩阵作为正式发布门槛；不能仅通过设置CI编码环境变量掩盖真实用户Windows默认终端会遇到的问题。

## 下一步规划
1. 检查全部6个OS/Python测试组合恢复成功。
2. 确认 v0.6.0 GitHub Actions release job 才能进入签名tag发布。
3. 将Unicode差异和修正纳入发行说明与长期回归测试。
