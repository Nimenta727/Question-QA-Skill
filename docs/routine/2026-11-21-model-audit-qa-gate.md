# 2026-11-21 — 对学生出题加入严格模型审计门禁

## 本次修改
- qa.py next新增可选严格参数 --require-model-audit --model-audit REVIEW.json [--audit-source-file COURSE.txt] [--require-course-audit]，调用model_audit.verify，审核表遗漏、题库SHA不符、来源无效、错答案/未处理问题时**在选题并展示前直接拒绝**。
- 模式明确区分：经模型审计后仅返回recorded_model_review_for_practice；既有不带审核参数的遗留CLI仍能使用，但标记not_checked_legacy_mode，绝不误称已验证。
- 核对通过才会继续选择/保持pending，重复next仍需同样的审核文件，题库变更会因SHA失配拒绝；学生可见question/options不包含审核者分析与标准答案。
- 用户要求AI严格审核时SKILL默认必须走审核流程，不依赖CLI的旧兼容开放模式。课程测试需提供实际资料并匹配引文，普通合成通识练习需显式标记，而非冒充教师教材。

## 下一步规划
1. 补充原bank与审核输出改变后的端到端回归，确保拒绝审核不消费出题状态。
2. 编写审阅模型“先独立解题、再对照命题者答案、专门挑刺”的明确指令。
3. 对真实课程资料审核仍需另行实际运行模型，程序检查不能独立证明教材内容为真。
