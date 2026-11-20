# 2026-11-20 — v0.9 私有审阅者凭据和审计文件的发行保护

## 改动
- build_release.py增加examples目录的敏感文件名防护（private、token、credential、secret、audit-key、checkpoint、receipt、registry），避免私人审核/密钥副本被误放到示例文件夹后随离线ZIP发行；保留所有公开合成研究示例。
- 扩展.gitignore：本地审阅者注册簿、管理员/评阅者token、审计私钥、外置审计策略标记及签名式外部checkpoint均不会默认进入Git追踪。
- 已在代码里明确审阅者凭据和学生数据都应由用户本地保护；此过滤不是内容扫描器，仍要用机构访问权限控制，不能向examples放置真实学生资料。

## 下一步
1. VERSION、SKILL元数据和全部GitHub Actions中版本号统一到v0.9.0。
2. 校验实际ZIP的manifest与SHA256，确认credential模块和audit ledger存在，私有token/注册簿/收据不存在。
3. 以三OS/两Python完整测试为发行门槛；任何失败先修复再发布。
