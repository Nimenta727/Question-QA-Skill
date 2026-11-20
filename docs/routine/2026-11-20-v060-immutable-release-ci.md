# 2026-11-20 — 三操作系统质量门槛及不可变发行 / Cross-platform and immutable publishing

## 改动
- tests.yml 扩展到 Ubuntu24.04、Windows2025、macOS15 各 Python3.9 与3.12：每个组合都验题库、审计硬错误、跑全单测、构建可验证ZIP和看板。
- release.yml 先验证三个操作系统与 Python3.12，再独立构建SHA256发行包并从解压目录重新运行全测试。只有完成验证才进入发布任务。
- 仅当当前main SHA与通过验证的构建提交完全一致、版本tag和Release均不存在时，创建轻量Git tag并生成Release。已经存在的版本拒绝变更；后续main构建仅上传CI artifact。
- tag 已存在但 Release 缺失会失败，不会静默覆盖仓库tag。发布权限仅赋予publish任务，其他均只读。
- 用户获得的GitHub Release版本由Git tag不可变标记对应，修复版本必须升级VERSION及发布新tag。

## 下一步
1. 补v0.6.0版本文件、双语协议和演示后启动六个平台/版本组合CI。
2. 检查macOS/Windows/Ubuntu单测与文件路径差异并修复。
3. 对照新tag精确SHA及Release内容确认发布，后续只升版本不覆盖本版。
