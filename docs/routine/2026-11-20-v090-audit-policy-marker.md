# 2026-11-20 — 防止仅删除审计字段导致静默降级 / Signed Audit Policy Marker

## 修改内容
- 新增与学习状态相邻、独立于状态JSON的 .audit-policy 文件，包含registry_id、audit_key_id及由独立密钥验证的HMAC，初次启用安全模式时以不可覆盖方式生成。
- 审阅与校验命令会同时验证状态中的HMAC审计链和外置策略标记，从而检测有人只将state.audit字段删除来伪装成未认证旧状态的情况。
- 明确该标记仍在同一本地文件系统里：有权限删除**两份文件**的攻击者仍可能绕过；必须另行保存外部checkpoint收据，不能宣称物理/密码学不可篡改。
- 本地数据删除如经显式授权应清理策略标记，但不能清除外部密钥和已独立保存的收据。

## 下一步
1. 将qa.py的audit-init/appeal-open/resolve/audit-verify/state-recover/delete接入标记存在检查。
2. 加入模拟恶意剥离audit字段、修改策略、外部收据回滚的回归用例。
3. 完整运行三平台测试，更新安全使用说明。
