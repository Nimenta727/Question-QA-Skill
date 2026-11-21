# Real-model validation matrix — v1.2.1 handoff

**Status: NOT RUN.** This is an execution checklist for future *actual* model calls, independent expert labels and, only if duly authorized, learner studies. No score or pass claim is implied by listing a case.

[中文版本](REAL_MODEL_TESTS.zh-CN.md) · [Protocol and denominators](QUALITY_VALIDATION.md) · [Test status ledger](TEST_STATUS.md) · [Blank results template](validation/REPORT_TEMPLATE.md)

## Scope, prerequisites and evidence

- Freeze an approved source list: licensed course/text version, section/page locator, exact claim, intended skill and prerequisites. If permission is missing, use plainly labeled **generic, synthetic** materials; never invent an instructor citation.
- Create independent item *families* (different task/representation, not only changed numbers). For factual exam-style questions, label the full set of defensible correct answers and every disqualifying flaw.
- Separate **author** and **reviewer** execution. Blind solve before reviewer sees author's key. Log model and version, prompt, settings/seed where available, source hash, bank hash, decision, audit reasoning, repair and second audit. Self-review must not be counted as independent model review.
- Obtain two blinded qualified human labels where possible and adjudicate disagreements. Split development/tuning and final holdout by **course/concept/item family** (and by learner if authorized) before opening final results. Existing FORGET-SE/ASSISTments2015 held-out data are **not new untouched holdouts**.
- Put only synthetic or approved aggregate results in this public repository. Learner data and potentially copyrighted instructor materials must remain under institution-approved handling and consent policies.

## Required validation cases

| ID | What must actually be exercised | Independent evidence/primary measure | Current status |
| --- | --- | --- | --- |
| RM-01 | Generate questions from an actually read C/programming lesson; include source references | Independent answer correctness; source traceability; expert judgments | **NOT RUN** |
| RM-02 | Generate questions from at least one *non-programming* discipline; avoid copying programming-specific structure | Knowledge and cognitive alignment; quality across domains | **NOT RUN** |
| RM-03 | Audit known wrong keys, hidden second valid options and equivalent short answers | Defect recall, false negatives, defect-type breakdown | **NOT RUN** |
| RM-04 | Audit missing assumptions, ambiguity, invalid distractors or incomplete open rubrics | Defect recall; analysis of every option/criterion | **NOT RUN** |
| RM-05 | Audit fabricated/out-of-scope citations, wrong page and source changes | Verified quotation/scope; fail-closed provenance; stale-hash rejection | **NOT RUN** |
| RM-06 | Audit intentionally *valid* controls and near-duplicate item families | Specificity / false-positive rate; meaningful novelty | **NOT RUN** |
| RM-07 | Present unknown-cause error, guessed/hinted correct and partial-credit responses | Reviewer-supported next-question target; no invented misconception/mastery | **NOT RUN** |
| RM-08 | Present explained success, transfer success, ambiguous valid response, exhaustion and stop request | Targeted transfer/boundary check; safe stop; fair alternatives | **NOT RUN** |
| RM-09 | Compare frozen adaptive vs fixed-sequence policy on the same authorized cases | Expert-rated information gain *proxy* and unnecessary-repeat rate; report limitations | **NOT RUN** |
| RM-10 | Measure Core vs Full hosting conditions under matched source/model/prompt | Real prompt/completion tokens, model calls, median and p95 latency, memory/compute where measurable | **NOT RUN** |
| RM-11 | Run permissioned delayed checks across independent sessions/dates | Delayed outcome vs initial guesses and history-only baselines | **NOT RUN** |
| RM-12 | Obtain expert review of accessibility/fairness and rubric-equivalence disagreements | Per-group counts only if lawful and sufficient data; adjudication rate | **NOT RUN** |

## Operational steps and outputs

1. **Plan and preregister:** define sampling, sample-size rationale, labels, target metrics, confidence-interval method and provisional gates **before** the holdout. A small pilot may diagnose failures but cannot certify population-wide accuracy.
2. **Gold set:** produce synthetic and/or authorized independently reviewed cases, including valid controls; document blind-label process. Record disagreements before adjudication, not only the final merged label.
3. **Freeze runtime:** record exact Skill commit, model names/versions, loading mode, settings, source excerpt, reviewer separation and any allowed tools. The offline CLI alone is not a model run.
4. **Author–review–repair:** capture first-stage blind solve, second-stage adversarial critique, decisions, source hashes, repairs and re-review. Treat every unresolved key/source issue as a failure to approve.
5. **Tutor episodes:** replay the same consented/synthetic reasoning transcripts against adaptive and fixed control policies, blind raters to condition where feasible. Neither replay alone nor grading accuracy proves real learner improvement.
6. **Analyze:** report counts (TP/FP/FN/TN), per-category misses, independent-rater agreement and uncertainty intervals, workload/latency/tokens. Distinguish correctness, diagnosis and *causal learning gain*—only a proper prospective design can assess the last.
7. **Publish safely:** fill the [results template](validation/REPORT_TEMPLATE.md) with exact eligible denominators, date, commit, model, reviewer status, failed gates and source-permission note. Publish *aggregate* results, not private submissions.

### Stop/acceptance policy

A test item with a known material answer ambiguity, false citation, second correct option, unreviewed rubric or unresolved reviewer dispute **must not be approved for students**. For a future version-level quality claim, acceptance thresholds and statistical uncertainty must be preregistered; the project currently has **no certified semantic accuracy or learning-gain threshold passed**. An engineering CI green check remains separate from an empirically verified success.

## Existing evidence to preserve

- The v1.2.0 distribution was released with cross-platform CI, deterministic ZIP/SHA256 and extraction tests; v1.2.1 needs its own run and published release verification.
- Legacy descriptive diagnosis index did not demonstrate superiority to simple history baselines; see [FORGET-SE](VALIDATION.md) and [ASSISTments2015](VALIDATION_ASSIST2015.md).
- **Do not relabel prior tests as results for RM-01–RM-12.**

## After-test reporting (does not run the study)

Once actual Skill runs and independently adjudicated labels are collected, present privacy-minimal records through the [Full report generator](SKILL_EVAL_REPORT.md). Synthetic reports are **software demonstrations** and do not alter RM-01–RM-12 **NOT RUN** labels.
