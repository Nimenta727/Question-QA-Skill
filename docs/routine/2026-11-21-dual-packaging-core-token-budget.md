# 2026-11-21 — 双发行包与核心Token预算保护

## 本次修改
- 保留 \`scripts/build_release.py\` 原默认行为：完整 \`question-qa-skill-VERSION.zip\` 继续包含所有离线Python、测试、演示数据、完整中英文文档、历史研究和开发日志。
- 新增 \`--profile core\` 和 \`--all\`：构建 \`question-qa-skill-core-VERSION.zip\`，使用**严格路径允许名单**只装SKILL.md、LICENSE、VERSION、精简的Core README以及4份按需参考（命题、追问、严格审题、学科策略）。
- 单独为Core提供不依赖开发工具的安装与使用说明；核心包内**没有脚本、原题解析库、测试、学生数据、开发研究记录**，模型默认只需读取SKILL，复杂说明按需读取。
- Full/Core均采用固定ZIP时间戳、文件SHA256 manifest、确定性顺序；校验器按实际ZIP根目录区分profile并拒绝路径穿越、哈希失配和Core多余文件。
- Core主Skill上下文建立字符预算上限（不冒称准确Tokenizer token数），增设独立的完整性、复现性、防串包、防篡改、压缩体积与文件树测试。
- 原版CLI和旧Full打包入口继续可用，主Skill提示长度将于下一提交压缩以满足上限。

## 下一步
1. 合并精简SKILL和双语安装文档，确认其在Core不依赖scripts/docs存在，同时保持Full功能路径。
2. 在CI中实际构建两种包、校验SHA256、全新解压验收；平台测试不能代替真实学习效果实测。
3. 最后统一发行版本号与正式附件列表，并保留所有旧版本tag。
