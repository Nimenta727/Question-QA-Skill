# Question-QA-Skill v1.2.0｜正式发行与验证

[返回首页](../README.zh-CN.md) · [文档索引](INDEX.zh-CN.md) · [发行历史](archive/RELEASE_PRE_V1_2.md)

## 发行文件

- **Core**：\`question-qa-skill-core-1.2.0.zip\`，仅含短\`SKILL.md\`、4份按需参考、README、VERSION、LICENSE、SHA256 manifest；日常Agent Skill安装推荐。
- **Full**：\`question-qa-skill-1.2.0.zip\`，保留所有离线Python脚本、评估工具、演示例子、测试、中英文文档、研发日志和历史报告；只在需要复杂工具时使用。
- **SHA256SUMS.txt**：包含Core、Full和演示看板三个发行附件的SHA256摘要。
- **demo-dashboard.html**：仅基于合成样例资料的离线演示看板。

## 可重复构建

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.0.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.0.zip
python -m unittest discover -s tests -v
~~~

两包均具有固定ZIP时间戳、确定性路径顺序和\`manifest.json\`逐文件SHA256记录。Core严格限制只能有预定8个实质文件，不能夹带测试/源码/隐私文件；Full必须含重要评分、状态、模型审核模块。

正式GitHub Actions在三个系统中运行发行门禁，另在Linux、macOS、Windows × Python3.9/3.12进行全量回归，并且将两个包全新解压再次核验：Full重跑所有测试，Core检查文件结构和主SKILL上下文预算。只有实际测试通过且Git Tag/Release不存在时才创建新版本，不修改旧Tag或附件。

## Token、审核与隐私

Core默认仅读取SKILL，参考内容需要时才加载；ZIP文件字节数不是模型可计费Token数。严审包括独立求解、答案与等价性、课件来源和九项教学质量检查，但**离线验证器不调用真实LLM，也不证明模型每条判断都正确**；正式考试需专业人工复核。未经授权的课件原文、学生作答、审核凭据/密钥和私人审稿包不能随发行文件公开。

过去的发行与安装长文档已移到\`docs/archive/\`，不再作为日常加载入口，但历史实现和Git提交保持可追溯。
