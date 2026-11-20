# 2026-11-20 — v0.9.0 CLI 外置安全策略与受保护状态恢复

## 修改内容
- audit-init同时生成独立HMAC外置 .audit-policy，绑定登记簿、审计密钥ID和状态元数据；audit-verify、audit-checkpoint以及申诉开启/结案均检查外置策略存在及HMAC真实性。
- 防止直接删除state.audit字段导致新安全模式自动降级到旧版--reviewer-confirmed；只删JSON字段会触发缺少审计元数据错误，不能修改评分。
- 受保护的state-recover额外要求--acknowledge-audit-rollback和--audit-key-file，先检查待恢复快照里的HMAC签名链及登记簿绑定，绝不恢复未经签名的旧状态；外部checkpoint仍可发现已签名旧链回滚。
- 受保护数据删除需要明确确认；删除受管文件时同步删除本地audit-policy，但外部凭据、审计密钥和独立收据保持原样，避免误导用户以为已安全擦除。
- state-check只检查策略和状态元数据是否一致，不持密钥时明确audit_cryptographic_verified=false，避免把“文件能读”误报为审计验签通过。

## 下一步
1. 加入只删掉audit字段、篡改策略MAC、恢复到启用审计前快照的回归。
2. 执行Linux/macOS/Windows各Python3.9/3.12真实测试。
3. 文档说明安全凭据能力与真人教师身份严格不同，外部checkpoint与安全模式不可随意降级。
