# 验证状态台账｜当前发行与真实实验

[English](TEST_STATUS.md) · [12项实际测试矩阵](REAL_MODEL_TESTS.zh-CN.md) · [报告空模板](validation/REPORT_TEMPLATE.md)

**本次人工记录日期：2026-11-21。** 本页不是实时监控页面；引用“已通过”前，应核实 GitHub Actions 与 Releases 当前结果。

| 范围 | 已有的可核对证据 | 不能推断的结论 |
| --- | --- | --- |
| v1.2.0 正式发行 | [Tag与四类附件均已发布](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0) | 不等于命题/教学效果已证实 |
| 上次主分支文档重整 | [六平台组合测试已通过](https://github.com/Nimenta727/Question-QA-Skill/actions/runs/44864077661) | CI 不能证明语义正确或审阅身份独立 |
| v1.2.1 本次维护发行 | 需核对 [v1.2.1实际发行及附件](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.1) 与 [Actions](https://github.com/Nimenta727/Question-QA-Skill/actions/workflows/release.yml)；本页并非实时状态 | 只通过 PR 不能叫正式发行 |
| 真实模型命题及来源核验 | **未执行 RM-01、02、05** | 没有真实模型命题准确率 |
| 模型严格审题漏检、误报 | **未执行 RM-03、04、06** | 没有实际审核召回率/特异度 |
| 学生推理诊断与追问对照 | **未执行 RM-07、08、09** | 没有诊断策略优越性或学习因果增益 |
| Token和运行成本 | **未执行 RM-10** | 字符缩减/ZIP大小不是实际 Token 报告 |
| 延迟保持、公平与真实学生研究 | **未执行 RM-11、12** | 没有经过验证的长期掌握与教学公平效果 |

### 状态更新要求

完成实验后，应使用 [报告模板](validation/REPORT_TEMPLATE.md)，记录日期、精确代码提交、模型版本、独立评阅方式、每个指标的**分子/分母**、区间和失败项目。必须保留 **FAIL/UNCERTAIN**，不能因结果不好就删掉记录。禁止在公开仓库保存真实未成年学生回答、未经授权教师材料或审核凭证。

此前 [FORGET-SE](VALIDATION.zh-CN.md) 和 [ASSISTments2015](VALIDATION_ASSIST2015.zh-CN.md) 的外部评估有真实且不理想的比较结果，但**不代表本次 RM 测试已完成**。
