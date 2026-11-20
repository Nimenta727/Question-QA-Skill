# 2026-11-20 — v0.8.0 版本、打包白名单与三平台不可变发行

## 本次修改
- VERSION、SKILL元数据及六环境GitHub测试/三系统Release工作流同步升级为0.8.0；避免提前触发不完整发行包。
- build_release.py在解压校验时强制包含scripts/appeals.py、scripts/reviewer_trial.py，防止出现“README声称支持申诉/研究，但正式ZIP缺少模块”。
- .gitignore新增备份目录、.bak/.lock、个人导出及真实双审阅试验的本地工作文件屏蔽，合成计划仍可在examples/发行包公开。
- 保留Linux/Windows/macOS × Python3.9/3.12矩阵、预发行三平台验收、完整单测与SHA256压缩包解压测试；只有尚未存在的v0.8.0 tag可首次创建并绑定通过测试的main SHA，禁止重写之前的正式Release。

## 下一步
1. 等候GitHub Actions 6组回归与独立Release流水线完成后读取真实结果，发现失败需提交修复并附routine。
2. 核对发布tag精确commit、正式ZIP三个附件和SHA256，不能先声称发布成功。
3. 后续如开展真人双审阅实验，必须先完成机构与适用学生/监护许可，禁用未授权数据收集。
