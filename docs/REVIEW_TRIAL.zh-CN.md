# v0.8.0 经授权的双审阅者试验执行协议与软件界限

**当前完成：研究计划准备、匿名任务随机分配、首轮评分冻结与一致性统计的软件工作流。尚未取得真实学生授权或安排真人实验，本仓库没有真实学生答卷。** 只有合成案例可以直接运行，无权自行启动现实中的学生数据收集。

## 实际试验前必须由学校/负责人完成
- 明确研究用途、适用的机构审查/伦理要求、教师和学生知情同意，以及对未成年学生适用的监护许可。没有这些，不能将study_type标为授权真实研究。
- 固定题库、样本纳入排除条件、rubric、独立审阅者要求、主要评价终点、争议仲裁和学生申诉流程。把原始答卷保存在授权的私有系统中，不把学生姓名、联系方式、答卷文本交给开源仓库。
- 真正安排两名不同且能胜任的审阅者，在首轮冻结前互相看不到评分。软件只能把A/B任务包分开，**无法证明组织上实现了盲法，也无法独立核实授权真实性**。

## 准备（生成A/B独立任务）
研究负责人维护一个不含真实身份和答卷的本地计划JSON：
    {
      "study_type":"synthetic",
      "authorized":false,
      "rubric_frozen":true,
      "case_ids_and_criterion_counts":[
        {"case_id":"anon-01","criteria":3},
        {"case_id":"anon-02","criteria":3}
      ]
    }

    python scripts/reviewer_trial.py prepare --plan examples/sample_trial_plan.json --output-dir trial-private-demo

创建本地 private-manifest.json、reviewer-A-tasks.json、reviewer-B-tasks.json；任务顺序独立随机化，仅包含匿名案例ID与维度数，不包含回答、分数和标准答案。对真实研究，study_type=authorized_real_self_declared且authorized必须为true，**这只是机构负责人在系统中的声明**，不是自动审查批准证明。

## 冻结（仲裁前）
实际两位审阅者先各自交出评分JSON，格式为：
    {"reviewer_slot":"A","cases":[{"case_id":"anon-01","scores":[1,0.5,0]}]}

必须恰好覆盖计划中每个匿名案例、每条固定rubric，分数只能为0、0.5、1。另一位审阅者使用reviewer_slot B，并独立提交，不允许首轮互看。

    python scripts/reviewer_trial.py freeze --manifest trial-private-demo/private-manifest.json --review-a trial-private-a.json --review-b trial-private-b.json --output trial-first-round-aggregate.json

结果有首轮已冻结标记、两份评分包的SHA256校验值、整体一致率、分歧、Kappa和置信区间，不携带案例ID或学生原文。Hash仅证明**此时提交的文件内容**，不能证明评分者是真人、身份不同、盲评或评判准确。冻结之后再由第三位审阅者依据事先约定的流程处理争议，记录申诉处理，但不应改写已冻结的首轮评分文件。

## 研究结果边界
主终点建议预注册为逐评分标准完全一致率与案例级Bootstrap置信区间；次终点包括加权Kappa、争议量与需要独立专家参照的错判率。必须同时报告群体规模、不同题型、未解决争议以及权限与数据治理范围。现阶段**没有真实实验结果**，不能拿合成数据证实课程效果或AI评分准确率。
