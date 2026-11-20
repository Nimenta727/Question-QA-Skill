# v0.9.0 复核者凭据与HMAC审计使用说明

本工具提供离线凭据持有检查、管理员撤销、HMAC申诉记录及外部检查点。它**不能证明审阅者的现实姓名、教师资格、学校授权、独立盲评或判分正确**。

## 1. 建立机构本地审阅凭据

将下方 PRIVATE_DIR 换成仓库之外、仅授权者能访问的私有目录。注册表、管理员凭据、教师凭据及审计密钥绝不可提交GitHub。

    python scripts/reviewer_credentials.py init --registry PRIVATE_DIR/reviewers.json --admin-token-output PRIVATE_DIR/admin.token
    python scripts/reviewer_credentials.py enroll --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --reviewer-id teacher_01 --token-output PRIVATE_DIR/teacher_01.token
    python scripts/reviewer_credentials.py check --registry PRIVATE_DIR/reviewers.json --reviewer-id teacher_01 --token-file PRIVATE_DIR/teacher_01.token

管理员与审阅者各有高熵独立凭据；注册表仅保存带盐的 PBKDF2-HMAC-SHA256 验证值。POSIX系统拒绝组/公共可读的秘密文件；Windows需要额外设置系统ACL。

撤销某一凭据（只能阻止未来的复核，不能撤销已经发生的审计记录）：

    python scripts/reviewer_credentials.py revoke --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --reviewer-id teacher_01

## 2. 保护学习状态并记录申诉

先创建普通学习状态，且其中不能已经存在申诉；历史申诉无法事后认证。

    python scripts/qa.py audit-init --state .qa-state.json --registry PRIVATE_DIR/reviewers.json --admin-token-file PRIVATE_DIR/admin.token --audit-key-output PRIVATE_DIR/audit.key

启用后记录保护标记，普通的 --reviewer-confirmed 自我声明不再足以结案；必须提供有效审阅者密钥、注册表与独立审计密钥。

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason possible_key_error --audit-key-file PRIVATE_DIR/audit.key
    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason key_verified --new-score 1 --registry PRIVATE_DIR/reviewers.json --reviewer-id teacher_01 --reviewer-token-file PRIVATE_DIR/teacher_01.token --audit-key-file PRIVATE_DIR/audit.key

主观题已有逐项评分时，必须用 --criterion-scores 提供完整更正评分向量，不能直接覆写不一致的总分。真实审阅者仍必须亲自核对答卷与rubric。

## 3. 审计验证和外部检查点

    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key
    python scripts/qa.py audit-checkpoint --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key --output PRIVATE_DIR/checkpoint-0001.json
    python scripts/qa.py audit-verify --state .qa-state.json --audit-key-file PRIVATE_DIR/audit.key --checkpoint PRIVATE_DIR/checkpoint-0001.json

每一次申诉开启/结案会按顺序和前一MAC使用HMAC-SHA256认证，可检查记录被事后修改或乱序。若审计密钥泄露，攻击者可能重新计算MAC；如果**没有在学习状态以外、由独立人员保管可信检查点**，不能保证发现整份状态连同审计一起回滚或删除。

每个检查点对应特定审计版本；后续操作应产生新的检查点，旧检查点要独立保留。此处HMAC是共享秘密认证，并不是第三方非否认数字签名。

已保护状态的回滚需要额外 --acknowledge-audit-rollback 与审计密钥；删除需要 --acknowledge-audit-deletion。它们是可明确授权的本地操作，不能说记录在任何情况下都绝对无法修改或删除。

## 真实研究边界
没有开展真实学生或教师试验。本地密钥持有不代表现实身份、专业水平、机构批准与学生/监护人同意。开展真人研究必须遵守 docs/REVIEW_TRIAL.zh-CN.md 的授权约束，使用 docs/REFERENCE_PILOT.zh-CN.md 的独立专家参照评分工具。
