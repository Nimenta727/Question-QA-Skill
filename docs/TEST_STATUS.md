# Verification ledger — current release and pending empirical work

[中文](TEST_STATUS.zh-CN.md) · [Real-model matrix](REAL_MODEL_TESTS.md) · [Report template](validation/REPORT_TEMPLATE.md)

**Last manually recorded:** November 21, 2026. This is an honest status ledger, not a live monitor. Confirm the actual latest GitHub Actions and Release before reporting success.

| Area | Current evidence | What is *not* evidenced |
| --- | --- | --- |
| v1.2.0 publication | [Published tag and four assets](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.0) | No model correctness or teaching-effect proof |
| Main-branch docs consolidation | [Successful cross-platform workflow](https://github.com/Nimenta727/Question-QA-Skill/actions/runs/44864077661) | CI cannot validate independent review semantics |
| v1.2.1 maintenance release | Check the [live v1.2.1 release and assets](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.1) plus [Actions](https://github.com/Nimenta727/Question-QA-Skill/actions/workflows/release.yml) for publication evidence; this ledger is not live | Do not call it released solely because a PR passes |
| Actual model question writing and source grounding | **NOT RUN:** RM-01, RM-02, RM-05 | No verified authored-item accuracy |
| Adversarial reviewer defect detection and valid-item acceptance | **NOT RUN:** RM-03, RM-04, RM-06 | No measured recall/specificity/miss rate |
| Student response reasoning and adaptive comparisons | **NOT RUN:** RM-07, RM-08, RM-09 | No proven diagnostic advantage or causal learning benefit |
| Runtime/Token efficiency | **NOT RUN:** RM-10 | Character/ZIP reductions are not billed-token measurements |
| Genuine retention, fairness and learner trials | **NOT RUN:** RM-11, RM-12 | No certified durable mastery or fair learning effect |

### Updating the ledger

An auditor should replace a **NOT RUN** label only with a dated report using the [blank report template](validation/REPORT_TEMPLATE.md), exact commit and run identifier, real model configuration, evaluator identity class (without personal secrets), denominator and uncertainty intervals. Record **FAIL/UNCERTAIN** results instead of removing them. Do not store real learner submissions or permission-restricted course excerpts in this public repository.

The legacy [FORGET-SE](VALIDATION.md) and [ASSISTments2015](VALIDATION_ASSIST2015.md) evaluations are real comparisons with negative/limited evidence; they **do not** count as completed RM tests.
