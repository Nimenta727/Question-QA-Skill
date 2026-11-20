# 2026-11-21 — 研发双智能体纠偏：Agent A开发与Agent B功能审计及决策

## 本次更改
- 澄清双智能体是对Question-QA-Skill**项目的研发分工**，不是为学生出题额外调用两个模型。新增GitHub Copilot自定义Agent配置：feature-builder负责实现/测试/文档，quality-auditor在独立执行会话中审Diff、复测缺陷、记录阻断/修订决策并只选下一项研发任务。
- 新增根目录AGENTS.md、GitHub Copilot全局指令、PR模板、中英文研发交接说明、PR格式及dated docs/routine校验GitHub Actions。CI只校验交接格式/日志，**不冒充真正独立Agent审计或批准合并**。
- 撤回上一轮误实现的scripts/dual_agent.py和tests/test_dual_agent.py：该代码针对Skill内部命题/审题模型，不属于用户要求的项目研发团队，不让它混入默认功能范围。
- 中英文README和ROADMAP简述角色、优先级和实际权限限制，保留题目质量审计功能scripts/model_audit.py（它是Skill本身原有需求的一部分）。
- 采用feature branch + PR作为之后代码修改的默认路径；每个GitHub变更commit都须同提交新增docs/routine日志。若GitHub Copilot尚未配置/实际调用，不能宣称两个Agent已真正运行。

## 已完成验证
- 已检查GitHub官方自定义Agent文件格式和独立PR审阅入口；确认项目之前没有.github/agents配置。
- 该提交还需PR触发后验证新增handoff CI和已有6平台回归。

## 下一步优先事项
1. 独立Agent B真实审查此PR的角色隔离和代码删除是否安全，或由被授权的独立审阅者审查；当前同一ChatGPT会话的预审不能算独立Agent B。
2. 审阅合格并有维护者批准后合并，使角色配置在默认分支可供GitHub Copilot选择。
3. 下轮由Agent B针对真实课程题目检验审题漏检/假通过、有效追问和误诊风险，提交明确可执行的P0任务给Agent A。
