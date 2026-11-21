# Question-QA-Skill — 轻量核心包 / Lightweight Core

这是适合直接安装到 Agent Skills 兼容助手的**低上下文开销**版本。默认只需加载 \`SKILL.md\`；根据用户意图才读取 \`references/\` 中的对应文件。目录不含Python、历史研究、CI测试或学生数据。

## 使用
把这个文件夹注册为你的助手的 Skill，或请它读取 \`SKILL.md\`，然后输入：

- “根据我提供的课件考考我，一次只问一道题，回答后决定下一问。”
- “根据课程内容生成五道有深度但公平的题，交卷前不显示答案。”

**按需文件**：QUICK 追问阅读 \`references/tutoring.md\`；DEEP 深度命题阅读 \`references/authoring.md\`；具体审题争议才阅读 \`references/model_audit.md\`；不同学科的特殊规则阅读 \`references/subjects.md\`。

## 版本区别
- **Core（本包）**：几份短提示和按需文档，无需Python，不自动调用外部模型API。
- **Full（完整包）**：另一个 \`question-qa-skill-1.2.0.zip\`，包含离线题库、脚本、自动测试、研究记录、全部文档和开发日志。需要运行 \`scripts/qa.py\`、严格审题JSON门禁或历史功能时使用 Full。

严审指令不是“已由独立模型审核”的证明。若只有一个模型，必须明确标为自审。实际课件不可虚构；猜对不等于长期掌握；官方高风险考试仍需专业人员核验。正式使用前需要针对实际课程材料验证出题与诊断效果。

MIT 许可证。此目录仅保留学生学习所必需的核心指令，所有人都可在完整项目中查看历史实现和测试。
