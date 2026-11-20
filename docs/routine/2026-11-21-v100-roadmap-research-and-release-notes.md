# 2026-11-21 — v1.0.0 教学优先路线图、接口合同及发行说明

## 本次修改
- CHANGELOG新增v1.0.0“回归AI教学核心”条目，明确本版核心是命题、已观察证据、独立追问、六轮停题及可解释的教学总结，不是新身份管理产品。
- ROADMAP重写为教学P0、独立实证P1、按需运维P2；旧路线与各版日志仍在Git历史、CHANGELOG和docs/routine中可追溯。
- FORMAT、ARCHITECTURE、DIAGNOSIS记录新tutor_intent/tutor_next_move/teaching_summary接口边界；references/authoring.md补独立命题变式的来源核验与评分标准验收。
- references/diagnosis.md作为轻量技术说明指向新的references/tutoring.md，避免旧版快问快答规则抢占主教学合同。
- 新增RELEASE_NOTES_v1.0.0.md，中英解释交付、研究局限、旧版数据诊断没有经过新模型标定、所有安全研究工具仍保留可用。

## 下一步规划
1. 完成六系统组合CI与发行包实际解压验收，确认测试包含教学场景回归。
2. VERSION、元数据、GitHub发布工作流仅在全部源码和文档就位后统一升级到1.0.0。
3. 日后组织独立真实课程的人类审阅和经过适用授权的学习效果验证，禁止以单测推导教育收益。
