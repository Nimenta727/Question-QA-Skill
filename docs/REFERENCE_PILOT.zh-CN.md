# v0.9.0 独立专家参照评分比较 / 软件验证流程

**状态：仅完成工具与合成回归；尚未执行经过机构批准的真实学生评分实验。** 本报告衡量的是与一个*外部提供的参照评分*是否一致，**不直接证明评分正确、学习进步或算法公平**。

## 为什么需要这个步骤
两位审阅者可能彼此完全一致，却对同一个问题给出同样错误的分数。仅有一致率和 Cohen Kappa 不能检测这类共同偏差。因此 v0.9.0 在已冻结的两份独立首轮评分之外，增加一个分开获得的专家参考评分，计算不同审阅者与参照答案的差异。

## 真实研究开始之前
- 取得学校/教育机构对研究目的、数据权限和必要伦理程序的许可；对未成年参与者取得适用的学生/监护人同意。
- 预先固定题目、原始课程材料、评分维度、主要统计量、样本范围与排除条件；安排真正的两位互相不知道首轮结果的审阅者，并有专业且与他们独立的参照评分小组。
- 将答卷原文与案例对照表保存在有权限控制的外部私有位置；仅在本地私有环境处理匿名 case_id 和评分数组。
- 每份评分0、0.5、1；不要在查看首轮结果后悄悄改专家答案来“提高准确率”。

## 软件执行流程
1. 先使用 scripts/reviewer_trial.py prepare/freeze，生成 private-manifest.json、评分 A/B 包和 first_round_frozen 汇总；首轮冻结文件必须存放在不会被后来覆盖的受控目录。
2. 另行准备专家参考JSON：

    {"expert_reference_self_declared":true,"cases":[
      {"case_id":"anon-001","scores":[1,0.5,0]},
      {"case_id":"anon-002","scores":[0,1]}
    ]}

case_id 及每题评分数量必须与最初注册的任务一致，不允许缺项或重复。该 true 只是提交者声明，**并未对真人资格、独立性或数学正确性进行认证**。

3. 运行（所有路径替换成受保护的实际本地文件）：

    python scripts/reviewer_pilot.py --manifest private-manifest.json --frozen first-round-aggregate.json --review-a reviewer-A-scores.json --review-b reviewer-B-scores.json --expert expert-reference.json --output pilot-aggregate.json --bootstraps 200

程序核对 A/B 包 SHA256 与冻结时内容一致，再输出只含汇总的统计结果，且不覆盖同名文件。不能验证外部冻结报告本身没有被持有写入权限的人替换，因此需要通过独立文件权限、备份或签名保管首轮冻结结果。

## 结果解释
- reviewer_a/b_expert_reference_agreement：评分者与专家参照在每条rubric上完全一致的比例。
- reviewer_a/b_reference_mae：相对专家参照的平均绝对分数偏差。
- reviewer_interagreement：两位评分者彼此的一致率。
- consensus_given_expert_reference_agreement：**双方一致的条目**中也与参照评分一致的比例。
- consensus_agreed_but_reference_disagreed：双方评分一致、但均与专家参照不同的条目数；这个指标直接检验“两人一致也可能一起错”。
- case_bootstrap_a_minus_b_reference_agreement_ci95：按完整答卷案例为聚类单位进行重抽样所得的 A 减 B 参照一致率区间，不表示个体学生成绩可信区间。

**不能把“与专家参照一致”直接命名为真正准确率**：专家参考也可能存在错误。外部研究负责人须独立确认参照制作过程、盲法、数据治理和参与者权利。

## 安全与限制
- 输出不包括匿名案例ID、学生原文、姓名或单个案例的分数；但私有输入文件、路径和专家参照仍须保密。
- SHA256仅锁定提供给程序的评分包内容；如果冻结报告与评分包被有权限者一起改写，则程序无法独立发现，需要外部可信检查点。
- 合成测试只说明工具运行逻辑和隐私边界，**并不是实际人类实验的证据**。


## 八例合成演示（无真人数据）

下面三个评分文件与现有 examples/sample_trial_plan.json 完全配套：sample_trial_reviewer_A.json、sample_trial_reviewer_B.json、sample_trial_expert_reference.json。均为人工编造的学习例子，不是学生实际作答或老师评分。

    python scripts/reviewer_trial.py prepare --plan examples/sample_trial_plan.json --output-dir trial-private-demo
    python scripts/reviewer_trial.py freeze --manifest trial-private-demo/private-manifest.json --review-a examples/sample_trial_reviewer_A.json --review-b examples/sample_trial_reviewer_B.json --output trial-private-demo/frozen.json
    python scripts/reviewer_pilot.py --manifest trial-private-demo/private-manifest.json --frozen trial-private-demo/frozen.json --review-a examples/sample_trial_reviewer_A.json --review-b examples/sample_trial_reviewer_B.json --expert examples/sample_trial_expert_reference.json --output trial-private-demo/pilot-aggregate.json

这组样例刻意安排了“二人一致但仍偏离参照”的评分。输出统计量仅可解释为流程和数据结构的演示，不能用来证明AI判分准确或师生已经参与真实研究。
