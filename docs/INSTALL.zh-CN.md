# Question-QA-Skill v0.8.0 安装与使用

## v1.0.0 核心使用入口（优先阅读）

普通学生快问快答与老师课件深度命题，请直接安装主 SKILL.md 或让AI读取该文件，参照 README.zh-CN.md 和 references/tutoring.md。**不需要**为一次六轮练习安装或配置审阅者管理员、审计密钥、学生数据库。

命令行脚本只是可选的离线辅助；运行 qa.py next 取得题面及内部 tutor_intent，答后 qa.py answer 取得 tutor_next_move，qa.py report 取得 teaching_summary。AI应自行将内部计划转换为简洁反馈和下一道问题。旧安全/申诉/真实实验模块保留于 references/operations.md 的按需索引。


本项目是能够被兼容 Agent Skills 协议的助手读取的 Skill，同时包含独立的离线 Python CLI。Python 3.9+，无需额外 pip 依赖，支持 Windows、macOS 和 Linux。

## 安装

1. 在 GitHub Releases 下载 question-qa-skill-0.8.0.zip 和 SHA256SUMS.txt。
2. 使用系统自带工具核对 SHA256，再解压 ZIP。
3. 将解压后的整个目录注册或复制至你的 Agent 所支持的 Skill 路径（各宿主路径不同；不是安装 Python 扩展）。
4. 也可直接使用命令行。进入解压后的目录，执行：

    python3 scripts/qa.py validate examples/sample_bank.json

Windows 上若没有 python3 命令，可以换用 py -3。

## 学生答题与追踪（快问快答）

    python3 scripts/qa.py start examples/sample_bank.json --state .qa-state.json --mode quick --limit 6
    python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json
    python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C --confidence unsure
    python3 scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json

每次 next 只暴露题干、选项及编号；answer 才核对答案并给解释。未交卷前不要把包含标准答案的 JSON 题库直接展示给学生。

## 主观题评分（逐项审阅）

主观题必须由教师或 Agent **先检查真实学生作答，并按题目的每条 rubric 对照证据**。程序不会自己判断任意自然语言答案语义是否正确。

    python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json

对出现的主观题，按照它的 rubric 创建自己的 review.json，例如 examples/sample_review.json（**仅演示格式，切勿直接拿演示分数评真实学生**）。该 JSON 数组每条必须包含 score（只能为 0、0.5、1）、evidence（观察到的具体作答证据）、feedback（下一步建议），顺序与 rubric 相同。审阅后运行：

    python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response "学生实际回答" --reason "逐项核验得分" --rubric-judgments @review.json

CLI 返回综合得分、每条标准的证据与反馈、已达标项、待改进项；本地学习状态只存放每项**数值分数**，不存储学生原文或评语。仍可用旧的 --score 0/0.5/1 --reason 对主观题手工给出粗粒度分数。

对于短答题，与标准答案字符串不一致但审阅者确认数学/语义等价时，可以用 --review-equivalent --reason "等价性理由" 重新记录为正确，仅限待回答的短答题，选择题不可覆盖。

**隐私注意**：命令行中的原始回答可能留在本机终端历史或系统进程信息中；不要在命令行参数里输入学生姓名、联系方式等身份信息。可以使用匿名的学习状态文件并保持本地保存。

## 离线 HTML 学习看板

真实记录：

    python3 scripts/dashboard.py examples/sample_bank.json --state .qa-state.json --output learning-dashboard.html --lang zh

无个人数据的演示记录：

    python3 scripts/dashboard.py examples/sample_bank.json --state examples/demo_state.json --output demo-dashboard.html --lang en

用浏览器打开生成的 HTML。页面自带深浅色适配、中英文切换和打印功能，展示知识图谱（有先修边才连线）、知识点证据、认知层次、已审核的错因、逐项评分和历史趋势。整页无需联网，没有第三方字体/CDN、学生原始回答或题库答案。

看板的得分、颜色、图表反映**已观察的作答情况**，并非经过标定的掌握概率或标准化考试成绩。

## 开发与离线发行检查

    python3 -m unittest discover -s tests -v
    python3 scripts/build_release.py --output dist
    python3 scripts/build_release.py --verify dist/question-qa-skill-0.8.0.zip

发行 ZIP 中的 manifest.json 对每个文件记录 SHA256，GitHub Actions 还会上传 SHA256SUMS.txt。参考 docs/RELEASE.md 和 CHANGELOG.md。

## 诊断可信度说明

公开 FORGET-SE 数据的首轮真实外部效标评测**尚未证明** v0.2 诊断指数优于简单历史成绩基线，因此这里不提供 BKT/IRT 模型，也不宣称能从少量回答准确读取潜在掌握状态。详见 docs/VALIDATION.zh-CN.md。


## 新增 v0.8.0 命题质量验证与真实数据复验

    python3 scripts/question_quality.py examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json
    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

上述审核文件**必须由独立审阅者逐题核实后填写**，不能让模型自动将所有风险项勾成通过。详情见 docs/QUESTION_QUALITY.zh-CN.md。独立真实数学数据的复验结果和可信度限制见 docs/VALIDATION_ASSIST2015.zh-CN.md。原始 ASSISTments 数据受原作者使用条款约束，项目不会将其打包或上传。


## v0.8.0 双人评分和强制仲裁
对待答的开放题，可使用 --response-file 私有答卷文件和 --independent-reviews @双人审阅文件。双方若有分数分歧，必须加上 --adjudication @第三方仲裁文件，否则不会消费未回答的题目。必须由审阅者独立检查真实回答，程序不会自行判断所有语义正确性。见 docs/ASSESSMENT.zh-CN.md 和 docs/ARCHITECTURE.md。


## v0.8.0 本地恢复/数学评分/一致率工具
仅短答题可由命题者选择启用有理数与有限多项式同值验证，未能安全识别的输入保留待答。详见 docs/MATH_EQUIVALENCE.zh-CN.md。
检查记录：python scripts/qa.py state-check --state .qa-state.json；从前一个快照明确回滚：python scripts/qa.py state-recover --state .qa-state.json --confirm。恢复有可能失去最后一次提交，相关文件应保持私有。详见 docs/STATE_SAFETY.zh-CN.md。
合成双评阅演示统计：python scripts/reviewer_study.py --input examples/sample_reviewer_study.json --output reviewer-study-aggregate.json。该示例不等于真实人类审阅研究，详见 docs/REVIEWER_STUDY.zh-CN.md。


## v0.8.0 申诉和数据管理
完成作答后保留event_id，使用 appeal-open --event-id ID --reason rubric_dispute 申请复核；只有真实独立审阅后才能用 appeal-resolve --reviewer-confirmed 更正分数。见 docs/APPEALS.zh-CN.md。

查看快照：state-snapshots；确认恢复：state-recover --snapshot ID --confirm。默认state-export只导出汇总，私人完整导出要--include-private --confirm-private。彻底解除本地受管文件需要 state-delete --confirm-delete DELETE-LOCAL，但不能保证云端副本或磁盘残留被安全擦除。见 docs/DATA_LIFECYCLE.zh-CN.md。真人双审阅研究必须另行取得合法授权，见 docs/REVIEW_TRIAL.zh-CN.md。


## v0.9.0 受保护申诉操作
先使用 scripts/reviewer_credentials.py 创建本地管理员和审阅者凭据并保护好秘密文件；学习状态尚无历史申诉时，可调用 qa.py audit-init 绑定注册表和独立审计密钥。之后申诉纠错必须提交有效审阅者token、登记簿及审计密钥，不能只声明“审核过”。使用 audit-verify 校验，建议将 audit-checkpoint 收据独立保存以检测合法旧快照回滚。详见 docs/SECURITY_AUDIT.zh-CN.md。凭据不等同于真实教职认证。


## v0.9.0 受保护评分、外部审计检查点及专家参照比较
本地管理员可通过 scripts/reviewer_credentials.py 登记、检查和撤销审阅者的能力凭据，调用 qa.py audit-init 对尚未出现申诉的学习状态启用保护模式。受保护状态的结案必须验证实际凭据，且可生成独立保管的 audit-checkpoint 用于发现审计回滚。详情见 docs/SECURE_REVIEW.zh-CN.md / docs/SECURITY_AUDIT.zh-CN.md。对研究样本，scripts/reviewer_pilot.py 可以把冻结的双审阅分数同另行获取的专家参照比较；docs/REFERENCE_PILOT.zh-CN.md 有八例完全合成演示，不代表真人实验已完成。
