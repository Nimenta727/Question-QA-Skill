# 2026-11-21｜v1.2.2 精简报告发行契约与导航回归

## 修改内容
- 发行契约加入：报告脚本、合成fixture、双语指南必须属于Full所选文件且脚本列在FULL_REQUIRED；Core allowlist不得包含报表工具/样本。
- 源码检验发行workflow的合成面板附件名 `skill-eval-demo.html` 和现有不可变Tag、SHA256、全新解压流程；Full压缩包内不要求存在.gitHub源码。
- 文档导航覆盖双语报告指南与v1.2.2说明，同时保留v1.2.1历史发行说明可追溯的检查。
- Core/Full打包回归确认新脚本和样例在Full中而非Core；任何真实模型指标仍需要独立评测，合成fixture不产生真实结果。

## 下一步
1. 运行Linux/macOS/Windows × Python3.9/3.12六组合CI及完整发行解压测试。
2. 修复任何失败，附加新的docs/routine根因与下一步记录。
3. 审阅PR、合并后核对v1.2.2 Tag、五种实际附件、SHA256与报告“合成演示”标记。
