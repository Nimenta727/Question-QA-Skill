# 2026-11-20 — 中英文安装说明与人工评估演示 / Bilingual installation & samples

## 本次改动
- 新增 docs/INSTALL.zh-CN.md、docs/INSTALL.md、docs/RELEASE.md 和 docs/RELEASE_NOTES_v0.4.0.md，覆盖安装、Agent Skill 兼容、学生测评、主观评分、离线看板、离线构建与科学有效性限制。
- 新增 examples/sample_review.json 展示逐项 rubric 审阅的 JSON 结构，明确仅供格式学习、不应直接评判真实学生。
- 新增 examples/demo_state.json：完全合成的学习过程，具有知识点、误区、主观题多项分数及跨日期作答，便于一键生成图谱与历史看板。
- 所有样例无真实学生身份和原始回答；样例题库本身是教学演示，不是验证过的学校考试。

## 下一步
1. 完善仓库入口 README/SKILL 版本和调用说明。
2. 建立 zip 自动构建与解压 smoke test，然后尝试 GitHub Release。
3. 核对最终 Python3.9/3.12 CI 测试与下载安装文档的一致性。
