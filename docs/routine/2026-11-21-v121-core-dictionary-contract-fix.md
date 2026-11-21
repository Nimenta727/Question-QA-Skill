# 2026-11-21｜发行契约测试Core文件映射检查修正

## 本次修改
- 新增的 `test_release_contract.py` 最初错误地把 `release.core_files()` 的字典键（字符串）当成 Path；改为直接对键名判定 `docs/` 前缀，防止AttributeError。
- 改动仅在测试代码，不降低文件允许名单约束，不涉及教学评分、正式发行脚本或真实模型测试。

## 下一步
- 由 GitHub CI 运行完整测试与Core/Full解压校验；若仍有问题，保留具体错误与修复记录。
- PR审阅通过后合并，核对 Release v1.2.1 附件真实存在。
