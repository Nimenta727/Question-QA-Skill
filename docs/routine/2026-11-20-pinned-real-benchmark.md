# 2026-11-20 — 固定数据版本的真实验证工作流 / Pinned real-data workflow

## 本次修改 / Changes
- 新增 .github/workflows/benchmark-forget-se.yml：在源脚本或工作流更新时、或手动 workflow_dispatch 时，执行一次外部效标分析。
- 固定 FORGET-SE 上游 commit 012f4ca56155140f5e5017dd336e4f9a5c5f249c；校验官方源文件的 Git blob SHA；避免静默换数据。
- 使用 GitHub runner 临时目录读取原始数据；仅上传无个人ID的聚合JSON结果（保留14天），并在执行日志打印核心指标。
- 不收集私有账号、真实身份或学生原始答案；原始研究来源/许可：https://github.com/alyssa-sha/FORGET-SE（CC BY 4.0）。

## 下一步 / Next steps
1. 审核 CI 外部下载与真实数据评测是否成功。
2. 用固定 commit/seed/数据范围写出可复现结果与缺陷。
3. 先修复数据及验证问题，再决定是否需要额外的 BKT/IRT 实验。
