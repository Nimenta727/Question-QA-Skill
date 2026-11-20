# v0.8.0 学习数据保留、导出与删除

本项目默认仅在本地保存学习事件和评分数值；虽然不保存答卷原文，知识点、分数、答题时间及申诉历史依然可能是敏感学习记录。

## 多版本恢复
所有状态写入都在操作系统本地排他锁中进行。除原有state.json.bak之外，新增state.json.snapshots/，保存上次有效状态的快照，**最多保留5个**。快照包含完整历史，必须像原文件一样保护。锁文件state.json.lock是长期持久的锁路径，即使清理数据也不删除它，以免并发程序形成两套锁。

    python scripts/qa.py state-snapshots --state .qa-state.json
    python scripts/qa.py state-recover --state .qa-state.json --snapshot SNAPSHOT_ID --confirm

不传--snapshot时按旧方式从.bak恢复。恢复不是合并，可能丢失恢复目标之后所有完成的操作；若恢复前当前状态有效，程序会额外保存当前快照。损坏快照不允许恢复。

## 数据导出
默认只导出各知识点次数、已观测平均成绩和申诉汇总（仍然可能敏感）：

    python scripts/qa.py state-export --state .qa-state.json --output qa-export-summary.json

私人完整导出包含历史、时间戳、事件ID和申诉审计，须明确双重确认：

    python scripts/qa.py state-export --state .qa-state.json --output qa-export-private.json --include-private --confirm-private

程序**不会覆盖已经存在的输出文件**，也拒绝将导出写入原state、.bak、.lock或快照目录。私人导出与答卷原文件应放在权限受控、最好加密的位置。

## 删除
只删除程序受管的本地state、.bak和最多5份滚动快照：

    python scripts/qa.py state-delete --state .qa-state.json --confirm-delete DELETE-LOCAL

删除之后state.json.lock可能仍存在，内容只是系统锁位不是学生资料；**普通文件删除不能保证物理安全擦除**，也不会删除已导出的副本、手机备份、云同步历史、终端日志或其他程序的缓存。删除之前应确认是否仍需履行学校记录留存要求。

## 数据处理限制
不接入第三方学生数据库、不自动上传学生历史、不宣称跨网络盘分布式事务。真实研究和多学习者共享环境应由负责机构确定数据留存期限、访问控制、知情同意和删除请求处理；此CLI不能代替机构数据治理。
