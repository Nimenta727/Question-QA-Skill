# Real-model evaluation report — BLANK TEMPLATE / 真实测试空报告

**This file is a template, NOT evidence that a test ran. Copy it into an appropriately authorized study folder and fill in after real execution. Never publish identifying learner data or unlicensed course material.**

## Reproducibility and authorization

- Study ID / test IDs (RM-01..RM-12):
- Date and researcher/reviewer role (no private identity data):
- Repository commit SHA and Skill distribution:
- Approved source identifier, permission statement and source hash:
- Dataset version, sampling rationale and frozen holdout manifest hash:
- Host, model provider, exact model version and prompt/references loaded:
- Temperature/seed if available; independent vs same-model reviewer:
- Number of human graders, blind labels and disagreement resolution:
- Baseline condition and prior frozen primary endpoint:
- Sample size / eligible observations and exclusions:
- Reviewer conflict and uncertainty notes:

## Raw decision count summary (aggregates ONLY)

| Measure | Numerator | Denominator | Value | Uncertainty interval | Decision/limitations |
| --- | ---: | ---: | ---: | ---: | --- |
| Audit sensitivity = detected defective / all labeled defective | — | — | NOT MEASURED | — | — |
| Audit specificity = accepted sound / all labeled sound | — | — | NOT MEASURED | — | — |
| False negative = defect passed / all defective | — | — | NOT MEASURED | — | — |
| False positive = sound blocked / all sound | — | — | NOT MEASURED | — | — |
| Source correctness = verified supported claims / checked claims | — | — | NOT MEASURED | — | — |
| Follow-up relevance = rater-supported targeted questions / evaluated episodes | — | — | NOT MEASURED | — | — |
| Correctness / fairness disagreements adjudicated | — | — | NOT MEASURED | — | — |
| Actual input/output tokens; calls; latency p50/p95 | — | — | NOT MEASURED | — | — |

## Audit and publication decision

- Exact known bad-item failures and affected families:
- Known good items incorrectly blocked:
- Any unresolved ambiguity, false source claim or unsafe item:
- Repair → re-review counts:
- Did the test follow a preregistered threshold? (yes/no and reference):
- Engineering CI result (link), separate from empirical results:
- Human reviewers' decision: **NOT REVIEWED / PASS / FAIL / UNCERTAIN**
- Can any quality claim be made? **NO until evidence, denominators and independent adjudication exist.**
- Future changes and next test:

For methodology and privacy requirements see [REAL_MODEL_TESTS](../REAL_MODEL_TESTS.md) and [QUALITY_VALIDATION](../QUALITY_VALIDATION.md).
