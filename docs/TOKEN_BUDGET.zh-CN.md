# Token预算与结构设计｜v1.2.1

## 主要优化

| 项目 | 上一稳定版 | 本版（按需配置） |
|---|---:|---:|
| 默认 \`SKILL.md\` 长度 | 约4018字符 | 约1965字符（约减51%） |
| \`references/model_audit.md\` | 约6127字符 | 约1306字符（按需加载） |
| \`references/authoring.md\` | 带历史版本说明 | 短执行规则（只在DEEP使用） |
| 默认安装目录 | 完整ZIP含源码/测试/历史文档 | Core仅8个实质文件+manifest |
| 旧完整版本 | 保留 | Full仍可完整使用 |

**说明**：以上字符量是仓库文件的Unicode字符近似，不是精确模型Token。不同模型Tokenizer、Skill宿主行为、聊天历史及用户上传文件会影响真实Token成本。压缩包体积也不等于模型实际上下文长度；是否真的省Token取决于只按需读取相关文件。

## 模型执行时应遵守的上下文规则

1. 默认仅载入 \`SKILL.md\`，而不是同时读取README、测试、文档、示例题库和全部references。
2. QUICK一般不需要每轮再次加载tutoring.md；只有不知如何追问时读一次。DEEP需要时读authoring.md，数学/其他学科才定位subjects.md具体段落。
3. 严格审题的**短硬门槛就在SKILL**：独立解答→找反例及等价答案→检查来源、干扰项、认知层次和公平性→未解风险拒绝展示；复杂多解、正式审核记录才读model_audit.md。
4. 教材只读取与本轮命题目标有关的章节/片段，不反复复制整份PDF；真实来源要核对，不能推测看过未读取的页码。
5. 学生输出保持“一句实质性反馈 + 一道下一问”；内部记录只保留必要证据，避免打印长JSON和反复复述题库。
6. 适当提前结束，不能为了凑满六题追加无价值的问题；不得用节省Token做借口跳过核对题目答案和安全条件。

## Full何时必要？

只有需要持久进度、离线题库验证、JSON严格门禁、研究评阅及开发测试时才安装完整版；Full的源码、119+开发日志和研究资料仅用于开发者，不应默认加入模型上下文。

## 如何验证

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.1.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.1.zip
python -m unittest discover -s tests -v
~~~

测试只验证允许名单、构建复现性、上下文字符上限和包完整性，不保证任何模型真实节省了某个固定百分比的付费Token。

## 真实仍需测量的性能

**RM-10 尚未执行。** 必须在相同模型、宿主、课件和任务条件下记录实际输入/输出 Token、模型调用次数、中位与P95延迟以及可得的内存数据，不能只用ZIP大小或字符压缩率宣称成本改善。参见 [真实模型测试矩阵](REAL_MODEL_TESTS.zh-CN.md) 和 [验证状态台账](TEST_STATUS.zh-CN.md)。
