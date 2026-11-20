# 2026-11-20 — v0.9.0 发行包必须包含研究与审核安全模块

## 本次修改
- scripts/build_release.py 的发行包校验白名单，要求新版本包含 reviewer_pilot.py 专家参照分析器、reviewer_credentials.py 本地持证验证器和 audit_ledger.py 申诉审计链。
- 防止CI通过、但用户从固定版本ZIP下载时缺少核心研究/凭据/审计模块。模块输入只能来自私有目录，ZIP只包括源码/合成示例，不允许把真实学生答案、专家评分包或身份秘密打包。
- SHA256 manifest、确定性ZIP、首次独立GitTag不可覆盖的既有验收机制保持不变。

## 下一步
1. 把三项必需模块与v0.9.0版本号及发行workflow同步。
2. 在Linux、Windows、macOS分别运行完整回归和全新解压ZIP测试。
3. 发布前再次确认文档没有声称软件能证明真人身份/授权或专家参照必然正确。
