# Independent evaluation workspace (Full only)

**Status: all three studies NOT RUN.** This directory contains protocols, an empty run manifest, and rules for publishing privacy-safe aggregate evidence. It contains **no fabricated real-course, model, or learner results**.

| Study | Protocol | Main endpoint |
| --- | --- | --- |
| Course-grounded question quality | [course_quality.md](course_quality.md) | Adjudicated sound, source-verifiable items |
| Independent auditing | [audit_detection.md](audit_detection.md) | True-defect detection, misses, false alarms |
| Adaptive vs fixed-order follow-ups | [adaptive_baseline.md](adaptive_baseline.md) | Paired blinded expert diagnostic-value rating |

[中文](README.zh-CN.md) · [Blank run manifest](run_manifest.template.json) · [Results policy](results/README.md) · [Report guide](../SKILL_EVAL_REPORT.md)

**Workflow:** license course inputs → freeze item families, gold labels and baseline → run a pinned model actually using the Skill → independent blind adjudication → calculate explicit numerators/denominators and disagreement → render sanitized aggregates with Full's offline HTML report.

Do not commit raw student answers, copyrighted teaching excerpts, identifying data, secrets or unauthorized transcripts. Offline replay cannot establish causal learning improvement; synthetic fixtures do not count as real tests.
