# Second independent real-world replication: ASSISTments 2015 (2026-11-20)

**Finding:** The v0.2 descriptive evidence index again fails to demonstrate a reliable gain over simple performance-history baselines on an independent mathematics dataset. This target is **causal next-response prediction**, not latent mastery truth or a separate final exam.

## Provenance and boundaries
Official [ASSISTments 2015 Skill Builder](https://sites.google.com/site/assistmentsdata/datasets/2015-assistments-skill-builder-data); comply with [data use terms](https://sites.google.com/site/assistmentsdata/termsofuseforusingdata) and never de-anonymize or redistribute records. Fixed public mirror [pyKT](https://github.com/pykt-team/pykt-toolkit), commit ccbaf37b07e3e7ff7b2415475b2faacb967d54ea; Git blob SHA1 f6b86c94e2a90316efd4bfd24655526919a817b0.

Raw source: 708,631 rows, 19,917 pseudonymous learners, 100 Skill Builder sequences. After deterministic lowest-SHA256 learner sampling (seed 2026, requested 1500 learners), 1495 learners contribute 50,540 eligible rows; 1818 sampled source rows were excluded for invalid/nonbinary values. Learner-disjoint split: 874 train, 330 validation, 291 test. The held-out test has 5,728 eligible forecasts from 280 learners.

The source has only user_id, log_id, sequence_id and correct. Critically there is **no question identity, real UTC calendar timestamp or independently validated cognitive level**. log_id is interpreted as chronology only and sequence_id as Skill Builder ID. To avoid fabricated independent items and spaced practice, all actions within a concept get one unknown family and one placeholder date. Consequently, no provisional-strong evidence decisions can be tested, and the heuristic index has limited information.

## Prespecified protocol
- Select learners deterministically independent of raw CSV row order; separate whole learners into train, validation, test using fixed SHA256 and seed.
- Fit global and concept baseline priors on train responses only.
- For each held-out learner, predict each next response from previous *same-concept* responses. Append target only **after** forecasting, not before.
- Compare global rate, training concept prevalence, smoothed learner concept history and the heuristic v0.2 index; report AUC and within-concept macro AUC, plus learner-clustered bootstrap uncertainty (100 replicates). Diagnostic index is not a calibrated probability.

## Results

| Method | Validation AUC, 6566 outcomes | Test AUC, 5728 outcomes |
|---|---:|---:|
| Global prior | 0.5000 | 0.5000 |
| Training concept prior | 0.6155 | 0.6606 |
| Smoothed learner history | **0.7061** | **0.7102** |
| v0.2 evidence index | 0.6197 | 0.6202 |

Within-concept macro AUC: validation history 0.5899 versus index 0.5888; test history 0.5741 versus index 0.5620. Index minus history pooled AUC 95% learner-bootstrap intervals: validation [-0.0992,-0.0723], test [-0.1003,-0.0736]. The within-concept macro differences have uncertainty spanning zero: validation [-0.0061,+0.0365], test [-0.0152,+0.0294].

Zero provisional-strong decisions were eligible: **not evidence of a 0% false-positive rate**, since independent item, delayed retention and higher-order evidence were unavailable.

## Not directly comparable to FORGET-SE
The FORGET-SE study predicted separate final-exam correctness from weekly history; ASSISTments 2015 predicts subsequent online practice responses. Different cohorts, disciplines, horizons, selection policies and observation schemas mean raw AUC levels should not be interpreted as cross-study improvement/degradation.

No student records or copyrighted data are redistributed. Reproduce privately:

    python3 scripts/evaluate_assist2015.py --input /path/to/2015_100_skill_builders_main_problems.csv --seed 2026 --max-learners 1500 --bootstraps 100 --output /path/to/aggregate-only.json

[Verified real-data workflow and aggregate artifact](https://github.com/Nimenta727/Question-QA-Skill/actions/runs/44752688312). Do not tune the index on this test cohort. Future work requires true item identities, reviewed cognitive taxonomy, genuine dates, and a new independent sample to quantify strong-label mistakes. Keep calibrated BKT/IRT out of the main path until justified by held-out comparisons.
