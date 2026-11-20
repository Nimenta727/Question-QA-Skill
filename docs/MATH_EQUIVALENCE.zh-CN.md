# v0.7.0 数学等价答案：范围、使用方式与判分边界

数学题常有不同但等价的表达，例如 7、14/2、3+4 或多项式 x+x 与 2*x。单纯字符串比较会误判。因此新增**需要命题者主动授权**的有界数学等价检测，默认仍使用精确匹配。

## 如何启用
仅短答题可附加字段。数值型：
    "answer_equivalence": {"kind": "rational"}

一至二变量多项式：
    "answer_equivalence": {"kind": "polynomial", "variables": ["x"]}

可用变量仅 x、y 或 [x,y]；使用标准Python式的 x**2 幂表达式；允许小数/整数、有理数、+、-、*、/，除法只能除以非零**常数**，幂次0–4。全部通过白名单AST与Fraction精确运算比较，不运行用户脚本、不使用eval，不访问网络。

## 可验证/不可验证的边界
- 有理数输入等价：7 == 14/2；0.5 == 1/2。单选题不自动启用数学覆盖，避免等价干扰项造成双答案键。
- 多项式恒等式：x**2-1 与 (x-1)*(x+1) 在允许语法内可核验。
- 表达式限长120字符，AST最多80节点，深度16、60项、8总次数、128位有理数分子分母，防止恶意输入资源爆炸。
- **不支持**自然语言、单位、根式、对数、三角函数、条件分段、变量分母、含参数定义域或代数方程的完整推导。这些情况下输入不可核验时CLI不会给错误成绩，而是保留待答状态并提示审阅。
- 旧题没有 answer_equivalence 字段时仍用完全相同的字符串规则。若是真正数学不等价但语法可核验，会记录0分；数学结果的正确性仍依赖出题时审核题干与预期表达式。
- 人工审阅通过 --review-equivalent 和 --reason 可以核查不属于受支持语法的等价答案。没有可靠审阅，不应跳过系统提示强制给分。

## 使用演示
    python scripts/qa.py validate examples/sample_bank.json
    python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
    python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response "14/2"

注意必须当前pending为启用数学等价的数值短答题（演示题库ALG-003）；若不是，应先练到这一题或使用只包含ALG-003的测试题库。正确判分返回 method=verified_math_equivalence。它证明的是允许范围内的**表达式相等**，不证明学生已经理解相关知识或解决了题干所有条件。
