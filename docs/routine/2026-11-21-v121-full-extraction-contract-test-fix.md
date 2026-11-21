# 2026-11-21｜v1.2.1 Full发行解压回归测试阻断修复

## 真实失败证据
- 合并版本 ff856e4425df0a992c8dd79cd04b9698f9cee0be 的发行工作流 `44864920651` 中，Ubuntu/macOS/Windows三个发行门禁全部通过，Core/Full构建与SHA256通过。
- 但新加入 `tests/test_release_contract.py` 在全新解压的 **Full** ZIP 里试图读取 `.github/workflows/release.yml`，而发行包按既有隐私/精简允许名单**本就不包含** `.github`。
- 最终 Full 解压回归运行 253 项，出现 1 个 FileNotFoundError；package失败，publish被跳过，**v1.2.1未发布**。

## 实际修复
- 调整 `test_release_workflow_checks_and_links`：开发仓库中仍严格检查实际GitHub Actions版本、校验和、不可变发布条件；在全新解压Full ZIP中检查发行说明及打包器存在，确认 `.github` **确实未被泄漏**，不再读取不存在的开发配置。
- 保留已有Core/Full ZIP允许名单、SHA256、全部单测与平台矩阵；未降低真实代码覆盖或放开私密文件入包。
- 此修改只涉及测试用例和本次routine记录，不改变任一学生命题、评分、诊断规则。

## 下一步
1. 完整重新运行 PR 六系统/解释器组合，确认仓库原地测试通过。
2. 合并修复后重新跑发布门禁、Core/Full 解压烟测及 SHA256，以真实Release v1.2.1作为成功依据。
3. 将独立真实模型测试继续保持 NOT RUN，后续按RM-01~RM-12进行真实评估。
