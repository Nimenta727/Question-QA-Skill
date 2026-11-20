# 2026-11-21 — 修复Python独立CLI模型审计循环导入

## 本次修改
- GitHub CI指出新增模块的导入环：qa.py顶层导入model_audit.py，后者导入question_quality.py，再导入qa.py，独立运行Python脚本时产生partially initialized module错误。
- 将model_audit改为只在qa.py next真正指定--model-audit时延迟导入，保留包导入和独立脚本导入两种情形，普通qa.py/quality.py互不递归。
- 本修复不放松strict审核：只有已提供审阅包才加载审核器，审核失败仍阻止学生看到题面；旧CLI恢复正常。

## 下一步
1. 重新运行全平台CI与model_audit单测，确认循环依赖消失。
2. 完成审阅代理的独立审题指令文档，再进入正式v1.1版本验收。
