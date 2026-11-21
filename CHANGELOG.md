# Changelog / 当前版本与历史定位

本文件描述**当前维护版本**。更早版本的完整设计说明、实现变更和旧发行页，使用 [Git Tags](https://github.com/Nimenta727/Question-QA-Skill/tags)、[Git History](https://github.com/Nimenta727/Question-QA-Skill/commits/main/) 和正式 GitHub Releases 追溯；不再把大段历史方案当作当前文档。

## v1.2.0 — 2026-11-21

- Core / Full 双配置发行：轻量 Agent Skill 与完整的离线 Python 研发工具分离，四份参考按需加载，降低默认上下文负担。
- 保留 QUICK 一题一问、DEEP 课件对齐命题、逐题独立求解与九维严格审题、疑点阻断及来源验证。
- Core 的 `SKILL.md` 文本字符量相对上一发行基线减少约 51%；此数字**不是**精确 Token 节省率。
- 包构建采用确定性 ZIP、`manifest.json` 逐文件摘要及外部 `SHA256SUMS.txt`；v1.2.0 正式 Release 与跨平台测试于 2026-11-21 成功完成。
- 离线诊断、答题跟进、严格审题记录门禁、状态管理与研发工具保持原有兼容入口；它们**不自动调用模型**、也不宣称已验证学习效果。

## 2026-11-21 — Main 文档与代码说明整理（发行后）

- README、安装页、文档目录、架构、诊断、审题、发行、路线图和评测计划围绕当前真实能力重写，消除混杂的历史版本叙述。
- 过时的独立旧发行长文和旧安装档案从当前工作树移除；Git 提交历史和旧版本标签继续提供追溯。
- 同步代码模块文档字符串与文档导航回归测试；保留所有课程证据与外部验证负面结果，**不虚构实证收益或独立审计结果**。

[Current documentation](docs/INDEX.md) · [中文导航](docs/INDEX.zh-CN.md) · [Next-stage evidence gates](docs/QUALITY_VALIDATION.md)
