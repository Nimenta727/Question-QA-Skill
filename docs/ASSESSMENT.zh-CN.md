# v0.6.0 学生回答智能评估协议 / 双人独立审阅

本项目不直接调用大模型，也不会独立验证任意自然语言的语义正确性。教师或Agent须先审阅真实答卷，本地评分引擎负责检查评分结构、引用、意见分歧与仲裁，不会把未经证实的判断伪装成精确分数。

## 操作流程
1. 启动测试并通过 qa.py next 取得一道开放题。确认它的rubric正确且经过独立审校。
2. 两名不同审阅者分别审查真实学生答卷，依据每项rubric独立填写：score只能为0、0.5、1；quote必须是答卷里逐字出现的原文；evidence阐述为何支持该得分；feedback提供具体改进意见。
3. 汇集两个评估 JSON 到 reviews 数组，每条包含 reviewer_id、independent:true 及 judgments。两位审阅者名字必须不同，且系统会拒绝没有逐字证据引用的条目。
4. 二人若得分一致则直接汇总；若任一标准得分有分歧，必须提交第三位不同的 adjudicator_id 和 decisions，逐一决定有分歧的 criterion_index（从0开始）及 score、reason、quote。程序在争议没有解决前拒绝消费待答题，也不记录最终成绩。

命令形式：

    python scripts/qa.py answer BANK.json --state .qa-state.json --response-file STUDENT_ANSWER.txt --independent-reviews @reviews.json --adjudication @adjudication.json

完全一致时可以省略 --adjudication；若有分歧则必须提供。可参阅示例：
- examples/sample_student_answer.txt（合成答案）
- examples/sample_dual_review.json（两份有意分歧的合成审阅）
- examples/sample_adjudication.json（第三方合成仲裁）

注意：样例只适用于当前pending题为演示题库ALG-004时。绝不能照抄样例评判真实学生。程序返回逐项得分、双方分数、分歧位置、一致率和反馈。状态只储存最终数值评分、总体一致率与争议个数，不持久化原始答案、审阅者名字、引述或评语。

## 隐私与边界
--response-file 避免把原答卷写入Shell命令行历史和进程参数；但输入的本地文件仍由用户保护和管理，终端临时输出也可能包含引文。不要公开审阅JSON、真实学生原答卷或详细评分输出。

不同ID和independent:true是自声明，**不构成真实双盲身份认证**。字符串证据存在不代表它真实支持正确推理，两位审阅者也可能同时犯错。重要考试应提供专业复核、申诉与更正程序，不能用评分一致率作为教学有效性指标。
