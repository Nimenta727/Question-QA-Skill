# v0.9.0 复核者本地凭据与防篡改申诉审计

本版本实现**本地凭据认证、HMAC链完整性核对、可独立留存的签名式收据**。它们可以检测一部分未经授权的评分更改，但不能将用户输入的姓名验证为真实教师，也不提供受监管的数字签名或无法被删除的账本。

## 1. 可信登记簿与受控审阅者

从仓库根目录执行，在私有目录中创建管理员和单独审阅者的凭据（示例路径均为本地文件）：

    python scripts/reviewer_credentials.py init --registry .qa-reviewers.json --admin-token-output .qa-admin.token
    python scripts/reviewer_credentials.py enroll --registry .qa-reviewers.json --admin-token-file .qa-admin.token --reviewer-id teacher-A --token-output .qa-teacher-A.token
    python scripts/reviewer_credentials.py check --registry .qa-reviewers.json --reviewer-id teacher-A --token-file .qa-teacher-A.token

需要撤销本地授权：

    python scripts/reviewer_credentials.py revoke --registry .qa-reviewers.json --admin-token-file .qa-admin.token --reviewer-id teacher-A

管理员必须在**外部流程**核实谁持有凭据及其专业资格。registry中的标识与口令证明只说明“持有登记过的秘密”，不等于实名、法定教师资格、真实独立审阅或盲法证明。凭据是随机高熵值，以PBKDF2-HMAC-SHA256加盐验证；不打印明文口令、也不会放入学生学习状态。密码文件建议使用单独、受OS权限保护的文件夹（POSIX校验0600；Windows需额外核查ACL）。凭据绝不可提交GitHub。

## 2. 给一个尚无历史申诉的本地学习状态开启保护

先正常使用 qa.py next/answer 创建本地state，再执行：

    python scripts/qa.py audit-init --state .qa-state.json --registry .qa-reviewers.json --admin-token-file .qa-admin.token --audit-key-output .qa-audit-key.hex

这会在本地生成随机32字节审计密钥，保存在**与state独立**的密钥文件；同时生成state.audit字段和同目录的 state.json.audit-policy 外置HMAC策略标记。**旧状态已有申诉时不允许事后盖上“已认证”的签章**，必须使用新的申诉账本或由负责机构另行制定迁移流程。

打开申诉：

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason rubric_dispute --audit-key-file .qa-audit-key.hex

确认独立审阅、纠正成绩：

    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason rubric_rechecked --new-score 1 --registry .qa-reviewers.json --reviewer-id teacher-A --reviewer-token-file .qa-teacher-A.token --audit-key-file .qa-audit-key.hex

如果原答案有 rubric criterion_scores，必须按原有标准提供 --criterion-scores 完整新分数数组；不能凭总分随意覆盖。受保护模式必须同时持有有效审阅者凭据和审计密钥，**单独加--reviewer-confirmed不再足以结案**。失效/撤销的凭据被拒绝。

没有开启保护的旧state仍可沿用v0.8的自声明流程，但这类记录应显示为self_declared_not_authenticated，不能称为经过凭据验证。

## 3. 验证HMAC链并独立保存校验收据

    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file .qa-audit-key.hex
    python scripts/qa.py audit-checkpoint --state .qa-state.json --audit-key-file .qa-audit-key.hex --output /另一个受控存储位置/checkpoint.json
    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file .qa-audit-key.hex --checkpoint /另一个受控存储位置/checkpoint.json

第一条校验每次申诉的递增序列、上一条签名及当前有效分数是否和审计一致。**仅有本地HMAC链无法检测整份state被替换为更旧但本来就合法的状态**；第三条可使用外部留存的收据检查“这份数据是否仍是之前的同一版本”。生成新收据不会覆盖已有文件。建议把收据和密钥分开存放，由独立负责人保管；不要把同一个checkpoint一起回滚。

已保护的状态使用state-recover时，必须额外提供 --acknowledge-audit-rollback 和 --audit-key-file。恢复的目标必须保留合法的同一审计注册簿绑定；若旧版本与外部checkpoint不一致，后续校验会失败。已保护数据删除还需额外的 --acknowledge-audit-deletion；删除本地数据不会删除外部收据或审计密钥。

## 4. 必须明示的安全限制

- 本地管理员登记簿是信任根，能修改登记簿并持有管理凭据的人可重新授权身份；程序无法核验真实世界的姓名、教职或机构权限。
- 若攻击者拿到审计密钥，HMAC不能再作为对其的防伪证明；若删除整个状态、.audit-policy及全部外部收据，也无法从已删除的数据恢复证据。
- HMAC账本覆盖**由申诉产生的记录和相应评分**，并非对全题库、全部原始答案或所有从未申诉过的成绩做签名。
- state-check只确认文件/策略格式一致，不等于完成密码学验签。必须运行audit-verify。
- 此处是单机离线防篡改检测与能力式本地授权，不是具有可信时间戳、远程见证、公证/不可更改存储的审计系统。对于正式考试，仍需要机构权限管理和独立申诉机制。
