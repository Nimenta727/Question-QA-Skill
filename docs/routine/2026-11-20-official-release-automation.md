# 2026-11-20 — GitHub Actions 自动化 v0.4.0 发行 / Official release automation

## 改动 / Changes
- 新增 .github/workflows/release.yml：Push main 或手动执行时，先校验 Skill 元数据与 VERSION，然后运行所有单元测试。
- 在全新 runner 环境中生成可复现 ZIP 与内含 SHA256 清单；生成基于合成学生状态的离线预览看板，并生成外部 SHA256SUMS.txt。
- 解压实际发行 ZIP 到全新临时目录，重新验证题库、运行完整回归测试并生成英文看板；只要失败便阻止发布。
- 上传 ZIP、校验文件和演示看板的 GitHub Actions artifact（保留30天）；在 GitHub Actions 有仓库写权限时自动发布 v0.4.0 GitHub Release。
- Release URL 和运行结果需要等待 GitHub Actions 验证后再对外声明，不会声称尚未生成的发行已经成功。

## 下一步 / Next
1. 检查 Actions 测试、ZIP 校验、解压 smoke test 和 GitHub Release 创建状态；按日志修复。
2. 将正式发行链接纳入 README/CHANGELOG 并记录发行版本对应的 commit。
3. 后续迭代继续分离形成性学生证据反馈与未标定的潜在掌握概率。
