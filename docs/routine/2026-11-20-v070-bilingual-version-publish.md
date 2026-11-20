# 2026-11-20 — v0.7.0 发布整合与双语资料同步

## 本次改动
- VERSION、SKILL、README中英文、CHANGELOG、FORMAT、ROADMAP、INSTALL/RELEASE升级至v0.7.0，按历史版本保留v0.6记录。
- 增加docs/MATH_EQUIVALENCE、STATE_SAFETY、REVIEWER_STUDY中英文使用说明，含数学支持范围、并发本地锁、上次快照恢复、审阅者统计的真实性边界及正式研究建议。
- 新增合成双评阅案例 examples/sample_reviewer_study.json，包含评分分歧和第三方仲裁后分数，不含真实学生作答或身份。
- tests.yml和release.yml版本由0.6.0更新为0.7.0，继续六矩阵回归、三系统发行门槛、不可变GitTag和SHA256解压验证。
- build_release.py 强制要求发行ZIP内带数学、安全状态和双评阅研究三个新模块。gitignore排除默认本地bak/lock和私有审阅实验文件。
- 修正数学资源限制测试：原4次999999999相乘只有约120位，小于预设的128位上限；改为6次乘法，确实验证128位边界。

## 下一步规划
1. 执行三系统两版本CI及真实发布，检查状态锁在Windows/msvcrt环境下的完整行为。
2. 核对v0.7.0版本Tag SHA和正式发行ZIP，防止错误地覆盖v0.6.0。
3. 后续应邀请实际教师开展经过学校或研究伦理授权的盲评、一致性与错误率验证；目前只是工具与合成数据，不冒称人类实验已完成。
