# 安装与使用｜Question-QA-Skill v1.2.0

[返回首页](../README.zh-CN.md) · [完整文档目录](INDEX.zh-CN.md)

## 1. 推荐：直接使用 Core 轻量版

从 GitHub Releases 取得 \`question-qa-skill-core-1.2.0.zip\` 和 \`SHA256SUMS.txt\`，验证下载文件，再解压。将解压目录注册为 Agent Skills 兼容助手的Skill，或让助手读取 \`SKILL.md\`。

**默认不要一次性读取整个ZIP。** Core目录仅有 SKILL.md、4个按需参考、README、VERSION、LICENSE及校验manifest。一般聊天只读SKILL；QUICK复杂追问才读tutoring.md，DEEP命题读authoring.md，严格审题争议读model_audit.md，跨学科差异读subjects.md。

示例：\`根据我的老师课件，一次问一道C语言指针题，根据答题推理决定下一问，六轮结束时总结已证实和未证实的理解。\`

## 2. Full 完整版：离线题库与验证

下载 \`question-qa-skill-1.2.0.zip\`。Python 3.9+，无需安装第三方依赖。进入解压根目录：

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

Windows可用 \`py -3\` 代替 \`python\`。演示题库与记录是合成数据，不是实际教师课件或真人实验。

Full还有 \`scripts/model_audit.py\` 严格模型审核记录的离线门禁，需要实际审核模型先独立作答并填审阅证据，程序本身**不调用LLM**；可参照 [模型审题](MODEL_AUDIT.zh-CN.md)。真实课程来源须核对，无真实资料只能按“通用练习”处理。其他命令按需查 [高级功能目录](INDEX.zh-CN.md)。

## 3. 核对发布包与安全边界

每个ZIP内含带SHA256摘要的 \`manifest.json\`，GitHub发行附件的 \`SHA256SUMS.txt\` 又对整个ZIP做SHA256验证；Full和Core都通过压缩包解压测试。

不要将本地学生记录、真实课程源全文、审核者凭据、密钥或申诉文件放入公开项目。正式教育评估与正式考试需专业人工确认。旧版安装及命令开发历史保存在 \`archive/INSTALL_PRE_V1_2.zh-CN.md\`，并不代表v1.2的当前默认步骤。
