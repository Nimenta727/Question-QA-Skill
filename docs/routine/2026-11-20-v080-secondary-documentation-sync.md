# 2026-11-20 — v0.8.0 评分与数据规范相关文档同步

## 改动
- 更新FORMAT、ARCHITECTURE、DIAGNOSIS、ASSESSMENT中英文和INSTALL双语，覆盖新增event_id、状态申诉日志、复核纠错后模型报告、快照、导出和删除边界。
- 更新RELEASE文档，要求v0.8.0独立版本且不能混入私人学生状态、导出文件、真实审阅实验包。
- 文档明确复核身份、真人研究权限、诊断可信度均不能由格式检查器自动认证。

## 下一步
1. 同步SKILL、README和CHANGELOG的版本入口。
2. 在最后一个版本提交中升级VERSION与GitHub Actions流水线，防止提前发布不完整包。
3. 完成三平台Python3.9/3.12和全新解压发行检查。
