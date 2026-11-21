# 2026-11-21｜代码契约说明、文档导航回归与旧文清理（阶段三）

## 修改内容
- 更新 `scripts/qa.py`、`scripts/tutor_core.py`、`scripts/model_audit.py`、`scripts/diagnosis.py` 与 `scripts/build_release.py` 的模块级文档字符串，明确无自动LLM调用、无经验证掌握率、审计JSON不是独立语义证明，以及旧文档应通过Git历史追溯；没有修改任何运行逻辑。
- 重构 `tests/test_docs_navigation.py`：验证当前中英文首页、安装、发行、架构、诊断、审题和质量评测文档的相对链接，以及Core/Full和能力限制说明。
- 更新 Core 包用的 `docs/CORE_PACKAGE.md` 和当前 `docs/RELEASE_NOTES_v1.2.0.md`，区分已经发布的不可变ZIP与后续main文档维护。
- 从当前工作树删除 `docs/archive/` 三份旧安装/发行长文，及 `docs/RELEASE_NOTES_v0.4.0.md` 至 `v1.1.0.md` 八份旧版本单独文档；旧内容**未篡改Git历史或旧Tag/Release**。所有既有 `docs/routine/` 记录保留。

## 验证与风险
- 删除仅限现行树中不再使用的旧文档；没有移除统计研究结果、正式评测限制、测试代码或用户数据安全工具。
- 导航测试、打包测试及跨平台CI需要在整个整理PR运行后确认通过，不提前宣称完成。
- 若其他工作流或外部消费者依赖旧文件路径，应通过 Git 指定历史提交/Tag 获取，不再把旧版本放回当前默认文档。

## 下一步
1. 运行CI及完整代码审阅，检查失效链接、Core预算、当前文档和README一致性。
2. 通过独立项目审计后合并整理PR；如测试失败，修复并记录新的routine。
3. 在下一开发周期建设真实命题缺陷集、审核漏检/误报指标和自适应诊断对照评测。
