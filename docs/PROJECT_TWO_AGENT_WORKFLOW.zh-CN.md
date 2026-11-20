# 项目研发双智能体工作规范（Agent A 开发 → Agent B 审计并决定下一步）

> 本协议是**改进 Question-QA-Skill 这个 GitHub 项目**，不是让学生做题时用两个模型来回出题。开发智能体不能给自己的代码签“独立审计通过”。

## 角色与权限

| 角色 | 职责 | 不得做 |
|---|---|---|
| **Agent A / feature-builder** | 依据已确认需求写代码、完善测试、兼容修复、写docs/routine日志、提交开发分支PR | 把自己的测试与总结当作独立审核、直接合并、决定下一开发优先级 |
| **Agent B / quality-auditor** | 从实际Diff与需求开始独立检查、重现错误、运行测试、判断风险、发布PR审查并确定**唯一最值得做的下一项任务** | 修改同一个被审查的功能代码后再自评、忽略重要失败、自己决定合并 |
| **维护者/控制层** | 把B反馈交给A、确认独立审核存在、合并与发行决策 | 在未核实的审核/CI记录上声称已验证成功 |

## 每轮交替的工作协议

**0. 选择需求与验收条件。** 首轮来源为用户实际目标，之后优先使用B的最后一份明确结论。功能默认优先命题可信度、真正有用的追问与学生诊断解释，避免身份/运营平台膨胀。A在动代码前写范围与完成标准。

**1. A实施。** 在专用分支完成最小可测试变更。每个含GitHub修改的commit都在同一个commit新增独立的 \`docs/routine/YYYY-MM-DD-内容简介.md\`，写本次改动、理由、已执行测试、问题和下一步。

**2. A移交。** PR中写出改动目标、文件、验收标准、实际CI、尚未测试的情况、已知风险、请求B验证的具体假设。任何失败不得标通过。

**3. B独立审计。** 必须在另一Agent会话运行（或由真实的另一位审阅者检查）。从代码Diff、数据契约、真实测试输出、课程/学生安全要求重新审查，不依赖A的“已通过”描述。寻找至少一个容易忽略的边界：错答案、例题换数字、题库升级、历史兼容、UTF-8/Windows、未授权数据外传等。

**4. B作出审计决策。** 一次PR Review报告包含：审核对象HEAD SHA，\`BLOCKED / REVISE / ACCEPTABLE_FOR_REVIEW\`，带文件路径与重现方式的缺陷、真实跑过的测试、遗漏范围、**下一优先任务**（理由、验收条件、优先级）。没有证据不能标已通过。

**5. A修复并重新移交。** B若阻断，A修复并在新commit加入新的routine日志；B审查新HEAD。禁止拿旧SHA的通过意见替代新审计。

**6. 维护者合并。** 新SHA的CI和真正独立复核满足后，才由有权限的维护者决定合并。模型审阅本身不证明功能正确，关键教育测评仍可要求真人专业复核。**即使CI通过，也不能把没有发生的B会话或PR review当成已经完成。**

## 实际启用两套独立 Agent

仓库内提供GitHub Copilot自定义Agent配置：
- \`.github/agents/feature-builder.agent.md\`：编码与测试。
- \`.github/agents/quality-auditor.agent.md\`：只读调查、审查决定和下一轮规划。

启用Github Copilot cloud agent后，可以分别在**独立会话**选择这两个配置。GitHub Copilot代码审阅可在PR请求，但默认评论不等于强制批准；组织/仓库的分支规则、实际身份及Copilot授权需由有权限的维护者配置。这些GitHub文件本身不会自动创建后台任务，也不能证明两个模型已经实际运行。

在当前ChatGPT GitHub连接只具备仓库读写、PR和Review动作，而没有创建真正独立Copilot会话的动作时，助手可先准备分支/PR、执行**明确标注的同会话预审**，但不应谎称获得独立 Agent B 验收。

## B的审核决策格式

    Review subject: <PR URL / exact HEAD SHA>
    Outcome: BLOCKED | REVISE | ACCEPTABLE_FOR_REVIEW
    Confirmed observations: [path / line / evidence]
    Tests actually run: [command, platform, result]
    Not verified: [...]
    Critical risks: [...]
    Agent A changes required: [...]
    Next selected task: [one task, why, acceptance tests, scope]
    Reviewer execution: [separate agent session | provisional same-session review]

日志存入\`docs/routine/\`；审计报告建议作为独立PR Review/评论保留在对应HEAD上。**禁止在README、VERSION或Release备注中把“已定义双智能体”写成“实际已自动完成双Agent审计”。**
