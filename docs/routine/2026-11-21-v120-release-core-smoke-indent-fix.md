# 2026-11-21 — v1.2.0正式发行阻断原因及Core全新解压烟测缩进修复

## 本次修改
- 发行CI在main提交51862fb5362上：Ubuntu、Windows、macOS的发行前测试全部成功，Core与Full两个ZIP构建及各自SHA256校验也成功，但新增的Core解压烟测Python here-doc发生IndentationError，package失败，publish被自动阻止，v1.2.0尚未发布。
- 针对 .github/workflows/release.yml 中 \`with tempfile.TemporaryDirectory() as core_tmp:\` 的内部zip解压、文件计数/预算断言缩进进行精确修正，不降低测试要求、不跳过Core或Full的实际全新解压验收。
- 两发行包、版本号、公开文档和原本测试源码均保持不变，故已经独立验证的Core/Full构建内容不受此次工作流脚本修复影响。
- 此提交与修复日志同commit，保留可追踪的失败原因；任何后续发布成功结论必须基于本修复后的新CI与实际GitHub Release结果。

## 下一步规划
1. 再执行三个OS的release gate、双包SHA256、Full提取后全套单测、Core提取后文件允许名单/主SKILL预算检查。
2. 确认publish只在main HEAD等于已验证提交且v1.2.0 Tag不存在时真正创建Release。
3. 核对两个ZIP、SHA256SUMS.txt和HTML看板全部可下载，输出精确文件大小与真实测试数量。
