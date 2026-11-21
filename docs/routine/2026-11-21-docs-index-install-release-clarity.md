# 2026-11-21 — 重新整理中英文README、安装文档与版本化Docs索引

## 本次修改
- 重写README中英文首页，将“30秒安装→Core/Full选择→QUICK/DEEP→严格审题→科研局限”作为主要导航，减少旧平台维护功能对用户入口的干扰。
- 重写docs/INSTALL中英文与docs/RELEASE.md，修复首页仍写v0.8或v0.6历史版本的误导；新增docs/INDEX中英文按需导航及docs/TOKEN_BUDGET中英文明确上下文预算和按需加载建议。
- 将旧版INSTALL、RELEASE长篇历史说明完整存入docs/archive/中，保留过去的知识但不再让其出现在默认安装入口或模型日常上下文。
- 发行文件说明两ZIP结构、各自manifest和整体SHA256SUMS校验、完全解压验证及学生个人信息排除；提示字符数≠真实Tokenizer token数，软件回归≠教育效果实测。
- docs/ARCHITECTURE保留原文，后续补充两发行包分层图和Core/Full隔离规则。所有历史Git提交仍可追踪。

## 下一步
1. 检查新的本地Markdown链接、Core所有文件引用和版本说明不存在断链。
2. CI验证两种包及历史脚本兼容后，同步VERSION、正式ZIP名字、GitHub Actions发布附件。
3. 保留项目研发双智能体独立PR审阅限制；不把同会话检查当成外部Agent B审计。
