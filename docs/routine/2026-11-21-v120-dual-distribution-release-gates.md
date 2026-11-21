# 2026-11-21 — v1.2.0双包CI、完整解压验证与不可变发行

## 本次修改
- 所有源代码、Core/Full打包测试和中文/英文文档就位之后，统一更新VERSION、SKILL元数据到1.2.0，Core README也指向正确Full版本下载名称。
- GitHub Tests矩阵更改为三系统×Python3.9/3.12分别**同时构建Core和Full**并检查两包的SHA256 manifest，Full旧CLI及Python全部单测继续回归。
- 三OS正式发行门槛同样生成两包；GitHub Release的SHA256SUMS包含**Core ZIP、Full ZIP、HTML演示看板**三个附件的哈希。ZIP均执行分发完整性检查。
- Full在全新解压目录重新跑完整测试；Core在全新解压目录检测仅9个文件（8实质文件+manifest）、SKILL <=3500 Unicode字符、四份必要参考存在、没有scripts目录。
- 主分支Tag仍在版本匹配、测试通过、当前main SHA未改变且Tag/Release不存在情况下**仅创建一次**，保留旧版本不变。
- Core最小上下文不等于独立模型核验或真实学习结果；本次只发布静态Prompt与离线工具，没有增加学习过程中的第三方API调用。

## 下一步
1. 核对PR的6/6跨平台测试、两包文件树、文档断链和重复打包字节相等。
2. 修复任何失败后在同PR补新的routine日志，并重新运行全量回归。
3. 只在满足实际验收后进入main自动发行，核对tag SHA、ZIP大小/Hash、Release下载文件是否真实存在。
