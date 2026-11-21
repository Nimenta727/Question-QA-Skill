# Compact post-Skill evaluation report (Full edition)

[中文](SKILL_EVAL_REPORT.zh-CN.md) · [Real-model cases](REAL_MODEL_TESTS.md) · [Status](TEST_STATUS.md)

**This is an offline report renderer, not a model runner or evidence of learning gain.** First, a real assistant loads the Skill and completes frozen test cases. Independently adjudicated item/response judgments and actual telemetry are then recorded in a privacy-minimal JSON file; only **after** testing does the Full CLI generate a static HTML report.

## Run an explicitly synthetic preview

~~~bash
python scripts/skill_eval_report.py examples/synthetic_skill_eval.json \
  --output dist/skill-eval-demo.html --lang en \
  --summary dist/skill-eval-demo-summary.json
~~~

The included fixture has **no model calls or real learner responses**. It is permanently labeled synthetic; its ratios cannot be called model accuracy. No third-party Python dependencies, CDN, JavaScript or network connection are required. Core remains a small prompt-only Skill, without this report generator.

## Minimal evidence-first UI

The default panel shows at most **three labeled metrics**: true-defect detection, sound-item acceptance and expert-targeted next-question agreement. Each has an exact numerator and denominator. For fewer than five labeled observations, no percentage is displayed. A 95% Wilson interval appears only with at least five observations from **distinct item families**; it is an approximate independence-based interval, not a confidence score for a student.

Below the metrics: prioritize harmful failure examples (bad item released, sound item falsely rejected, wrong reason for rejection, unresolved review or mistargeted follow-up). Use **one** compact chart of at most four defect categories. Further case IDs, latency/token coverage and provenance are available through collapsed details. No giant chart wall, no fabricated zeros for untested conditions, no mastery probability.

## Strict JSON contract

Input root has exactly `schema_version` (1), `run` and `cases`. Maximum 2 MB and 2,500 cases. Unknown fields are rejected, which helps prevent accidental inclusion of identifiable student answers, instructor excerpts and private prompts.

Required `run` strings: `id`, `mode` (`synthetic_demo` or `actual_model`), `reference` (`synthetic_labels` for demos; `expert_adjudicated`, `model_only`, `none` for actual runs), `model`, `commit`, `dataset`, `date`. These are declarations, not independent authentication of model/expert identities.

Each case requires `id`, `test_id` (RM-01…RM-12), `family` and `kind`:
- `audit`: `truth` = `defective` / `sound` / `unknown`, `decision` = `block` / `accept` / `uncertain`, optional categorized `defect`. A blocked defective case **must** include boolean `caught_actual_defect`. Only a block that **correctly identifies the expert-labeled real defect** (true) counts as detected. Blocking for an unrelated reason does not earn credit; accepting a sound item is correct acceptance.
- `tutoring`: `expected_action` and `selected_action` from `clarify`, `recheck`, `repair`, `transfer`, `stop` or null. A match counts only if the reference action is present.

Optional `input_tokens` / `output_tokens` are actually measured nonnegative integers; `latency_ms` is an actual finite nonnegative measurement. Missing values stay missing, with explicit coverage. P95 is withheld when fewer than 20 latency samples are provided. This schema stores no raw question/student text; HTML escapes all identifiers and has a strict local Content Security Policy.

`mode=actual_model` with reference `model_only` or `none` **suppresses quality rates** even if model-produced labels are present. `expert_adjudicated` enables declared-reference rates, but the script cannot prove that independent adjudication truly happened. Repeated-family CI is withheld. The output is not a human-subjects study or a statement about long-term mastery.

## Methodological references

- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific tests and appropriately designed graders.
- [Anthropic agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents): code/model/human graders, failure traces and realistic agent loops.
- [AERA/APA/NCME testing standards](https://www.apa.org/science/programs/testing/standards): validity, reliability and fairness limits.
- [NIST AI RMF Measure](https://airc.nist.gov/airmf-resources/playbook/measure/) and [NIST binomial intervals](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbici.htm): documented uncertainty and small-sample limits.
- [Google PAIR explainability](https://pair.withgoogle.com/guidebook-v2/chapter/explainability-trust/): progressive disclosure and properly calibrated trust.
- [Evidently reports and tests](https://docs-old.evidentlyai.com/user-guide/tests-and-reports/introduction): separating data quality and performance evidence. No Evidently dependency is used.

Real RM-01–RM-12 experiments still require genuine model runs and appropriate independent reference review. They remain **NOT RUN** in the current ledger.
