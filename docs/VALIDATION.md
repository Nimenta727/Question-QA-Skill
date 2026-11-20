# External validation of formative diagnosis (2026-11-20)

**Result: the v0.2 descriptive index has not established a predictive advantage over simple history baselines. No calibrated BKT/IRT model is included.** [中文报告](VALIDATION.zh-CN.md).

## Research data and protocol
Source: [FORGET-SE](https://github.com/alyssa-sha/FORGET-SE), upstream CC BY 4.0 with declared participant consent. Pinned upstream commit: `012f4ca56155140f5e5017dd336e4f9a5c5f249c`. Of 10,873 weekly quiz records, 729 have fractional scores. The external final-exam table has 186 rows; 18 repeated anonymized IDs give conflicting exam results. We **excluded all such IDs** rather than selecting a row arbitrarily, leaving 150 usable students.

Deterministic learner-disjoint SHA256 split (seed 2026): 84 training, 36 validation, 30 test. There are 279 eligible student–concept final-exam outcomes in test. Training-student exam labels alone provide global and per-concept priors. Evaluation is association with **independent exam correctness**, not ground-truth latent mastery. Historical response-based scores use weekly observations only.

The de-identified `log_id` is used as an ordering variable, never a real calendar date; item cognitive levels are unknown. Therefore this dataset **cannot validate delayed retention or higher-order mastery**, and zero `tentatively_strong` decisions are not a measure of accuracy.

## Held-out test results

| Method | Pooled AUC | Within-concept macro AUC |
|---|---:|---:|
| Global prior | 0.5000 | 0.5000 |
| Concept prior | 0.7572 | 0.5000 |
| Entire quiz history mean | 0.6998 | 0.5509 |
| Last three quiz scores | 0.7352 | 0.5538 |
| **v0.2 evidence index** | **0.5149** | **0.5535** |

Learner-clustered bootstrap (200 repetitions) 95% intervals for v0.2 index minus full quiz-history mean: **pooled AUC [-0.2396, -0.1377]**, **within-concept macro AUC [-0.0116, +0.0155]**. No demonstrated incremental gain.

Validation pooled AUC: global 0.5000, concept prior 0.7736, quiz mean 0.7203, recent three 0.7509, index 0.5351. Within-concept validation macro AUC: quiz mean 0.5680, recent three 0.5909, index 0.5830.

v0.2 index is not a calibrated probability: its Brier/log-loss/ECE is intentionally not presented as probability evidence.

## Reproduce and interpret
[Successful pinned GitHub Actions run](https://github.com/Nimenta727/Question-QA-Skill/actions/runs/44743252876) downloads verified upstream Git blobs and retains raw data only in runner temporary storage. Only aggregate JSON is uploaded (14-day retention).

```bash
python3 scripts/evaluate_forget_se.py --weekly /path/forget_se.csv --exam /path/exam.csv --seed 2026 --bootstraps 200
python3 scripts/evaluate.py /path/answers.csv --format generic
```

Generic CSV required fields: `learner_id,concept_id,item_id,correct` (0/1); optional `order,answered_at,family,level,type,difficulty,confidence,hint_used`. Missing timestamps must be missing for all rows rather than mixed. An ASSISTments09 adapter is also supported; use an official corrected collapsed extract, not duplicated per-skill rows.

**Limits:** exam responses are external criteria, not latent mastery truth; historical exposure logs cannot establish causal gains from an adaptive question policy. These outcomes are not necessarily representative of school subjects or other cohorts. Do not tune thresholds on this held-out test split. Next, gather independently reviewed item families/cognitive levels, genuine delayed checks and another consented cohort; pre-register evidence gates and future-error benchmarks; explore BKT/IRT only after adequate calibration data and repeatable comparisons justify the added complexity.


## Second independent study
A separate mathematics practice-data next-response study is now available at [VALIDATION_ASSIST2015.md](VALIDATION_ASSIST2015.md) / [中文版](VALIDATION_ASSIST2015.zh-CN.md). Its held-out test AUC for v0.2 index was 0.620, versus 0.710 for simple smoothed learner history. The study and original FORGET-SE external final-exam study measure different targets; their AUCs must not be compared as though the task were identical. Neither validates true latent mastery labels or adaptive question-choice causal effects.
