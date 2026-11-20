# v0.8.0 学生评分申诉与纠错

本功能用于**记录申诉、审阅结果和纠错原因**，不是自动推翻老师的评分。CLI只能核查格式和约束，不能确认审阅者是否独立、是否有资格或是否真正核对了原始学生答案。

## 操作
1. 完成一次答题后，answer的JSON返回唯一event_id。早期没有ID的旧历史可用--event-index（从0开始）发起申诉，并只给选中的记录补ID。
2. 提交申诉，原因必须从possible_key_error、equivalent_answer、rubric_dispute、scoring_error、other中选一个，不保存学生姓名或自由文本留言。
3. 由真正独立的审阅者检查具体题干、答案、评分rubric和学生原答；完成核验后，使用--reviewer-confirmed声明已审阅（**只是声明，系统无法验证身份**）。
4. 如果维持原判，decision=uphold并将reason设为appeal_upheld。需要纠正的用decision=correct与具体纠错代码：key_verified、equivalence_reviewed、rubric_rechecked或scoring_corrected。

    python scripts/qa.py appeal-open --state .qa-state.json --event-id EVENT_ID --reason rubric_dispute
    python scripts/qa.py appeal-list --state .qa-state.json
    python scripts/qa.py appeal-resolve --state .qa-state.json --appeal-id APPEAL_ID --decision correct --reason rubric_rechecked --new-score 1 --reviewer-confirmed

**关于主观题**：若原有criterion_scores，则更正时必须传 --criterion-scores '[1,0.5,1]'，总分由维度平均得出；如同时提供--new-score，两者必须一致。选择/简答客观题纠错后只能是0或1分，不能给0.5。不允许修正为与当前相同的分数或在未结案时为同一答卷重复申诉。

纠错后原始历史的有效成绩更新，学习报告与后续选题使用新分数；申诉日志保留旧分、新分、处理时间、原因、审阅声明，不保留真实学生原答案、姓名、私有审阅意见。满分纠错会清掉旧的误区标记。

## 透明度和责任
- **不能证明外部独立审阅真的发生**，也没有教师账号认证或数字签名；重要测评需要学校的真正复核及申诉机制。
- 不允许自动据分数创建虚构的审阅声明。教师负责保护原始答卷及申诉材料。
- 纠错影响后续个性化学习建议，不代表诊断指数已获得统计标定。
- 旧事件索引依赖当时的历史位置，请在有event_id后优先使用唯一ID。


## v0.9.0 凭据验证和HMAC审计
启用本地受保护评分模式后，发起申诉需提供独立审计密钥；纠错结案必须同时持有效审阅者token、匹配的注册簿和审计密钥，旧版 --reviewer-confirmed 不能独自绕过保护。未启用的旧状态仍可运行但不应称为认证审阅。详细配置与防篡改边界见 docs/SECURITY_AUDIT.zh-CN.md。
