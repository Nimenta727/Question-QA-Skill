# 2026-11-21 — 严格模型审题完整打包与隐私边界

## 本次修改
- scripts/build_release.py新增必需清单：正式ZIP必须有scripts/model_audit.py、references/model_audit.md、docs/MODEL_AUDIT中英文，否则校验失败，避免发行包只有宣传而没有严格审题实现。
- 对examples目录新增敏感命名排除：实际审核包、课件来源抽取文字、独立审阅包等私有工作文件不能因误放到examples而随ZIP发布；历史合成演示例子不受影响。
- .gitignore排除实际审核记录与课程文本片段的常用文件名；references/operations.md索引新的严格审题工具（实际审题属于核心，凭据/管理才是按需）。
- tests/test_skill_contract.py核实模型审题脚本及协议同时存在于仓库和发行选取清单。

## 下一步
1. 经六平台CI和完整重新解压验收，确保没有新导入或兼容错误。
2. 统一1.1.0元数据并发布不同于v1.0.0的新Tag和新ZIP。
3. 真正独立模型审题的准确率需要专门真人标准题及外部验证，不应把合成模板通过当成已使用模型。
