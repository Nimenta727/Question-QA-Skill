# v0.7.0 学习记录并发、备份与恢复

旧版本用原子文件替换避免半写入，但两个同时启动的脚本仍可能读到同一旧状态并覆盖彼此。本版本为每个 state 文件增加系统原生排他锁，把 start/next/answer/report/reset-pending 与恢复操作的读-改-写包在同一事务里。

- Linux/macOS 用 fcntl.flock；Windows 使用 msvcrt.locking。加锁失败最多等待约8秒，超时给出state busy，而不是静默覆盖。
- 锁位于 STATE.lock，文件可能永久存在，**不要随意删除它**；锁本身会在持有进程退出时由系统释放。仅适用于本地文件系统，不能替代NFS、Dropbox、共享云同步等分布式锁。
- 提交新状态前校验原文件完整性，把**上一份已提交有效状态**原子写入 STATE.bak，再用同目录临时文件+fsync+os.replace写入新版本。若当前原文件损坏，拒绝把它覆盖进好的备份。
- 每份备份是之前一个版本，恢复会丢掉**最后一次成功操作**，这不是完整历史快照系统。输入state仍可能包含学习行为敏感信息，备份也要妥善保护。

## 查看、恢复
    python scripts/qa.py state-check --state .qa-state.json
    python scripts/qa.py state-recover --state .qa-state.json --confirm

state-check仅输出当前文件和上次备份是否完整、历史条数和哈希；不会输出学生原文。state-recover必须显式确认才将当前状态恢复为.bak内容，成功后保留.bak。建议在恢复前先备份/复制受损文件以便调查，但不要公开含学生数据的文件。

## 安全限制
- 本程序不进行云上传，不提供自动全局回滚、数据库事务或远程分布式一致性保证。
- 未通过独立文件系统断电验证或网络盘一致性验证，务必在本地可靠磁盘使用，避免同时通过外部编辑器修改状态文件。
- 默认状态文件及.bak/.lock应加入.gitignore，勿提交真实学生学习记录；可通过操作系统帐户权限或加密存储进一步保护。
