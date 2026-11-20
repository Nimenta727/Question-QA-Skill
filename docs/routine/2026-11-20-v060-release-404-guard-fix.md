# 2026-11-20 — 不可变Tag判断的404边界修复 / Release guard 404 correction

## 本次改动
- 新版三平台发布流程已通过Ubuntu/Windows/macOS回归与解压验证，但publish步骤将GitHub API 404返回中的字符串null判断为“非空Tag SHA”，误判当前不存在的v0.6.0标签已经存在，阻止发布。
- .github/workflows/release.yml 改为直接以gh api请求的成功/失败HTTP状态判断Tag是否存在，而不解析可能为null的JSON字段。Tag真实存在时依然拒绝覆盖，Release存在时跳过发布。
- 不修改课程内容、学习状态、评分算法和数据；只是修复新发行门槛的API错误处理。

## 下一步规划
1. 重新运行本次提交的跨平台门槛和真实发布流程。
2. 检查v0.6.0 Tag SHA与对应Release目标提交一一匹配，三个发行附件存在。
3. 对发行后后续提交保持“tag不可覆盖”并按版本管理下一迭代。
