# Question-QA-Skill

**Source-grounded deep question authoring + evidence-based adaptive quick checks.**
**中文说明：** [README.zh-CN.md](README.zh-CN.md)

## What it does
- **DEEP**: generates original, rigorous, fair questions with objectives, source evidence, valid solutions, misconception-aware distractors and marking rubrics.
- **QUICK**: one question per exchange, adapting to wrong, uncertain and correct answers; finishes with an evidence-aware learning snapshot.
- **Offline companion**: no-dependency Python engine for validated JSON banks, deterministic item choice, objective grading, recorded rubric scores, local per-skill summaries and spaced-review suggestions.
- **Low-token design**: tiny SKILL.md entrypoint, mode-specific lazy references and locally computed statistics. No model calls are used by the CLI.

This is an **Agent Skill**, not a deployed website or a psychometrically calibrated CAT. An assistant authors questions; Python selects and scores validated items locally.

## Quick start
Use with an Agent Skills-compatible assistant by installing this repository as a skill, then ask:

- "按照这节课的材料，出5道深入但公允的题，重点考察推理与迁移。"
- "对一元一次方程进行6轮快问快答，每次只问我一道，并诊断薄弱点。"

Command-line demo (Python 3.9+, no dependencies):

~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json --mode quick
python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C --confidence sure
python3 scripts/qa.py report --state .qa-state.json
python3 -m unittest discover -s tests -v
~~~

The next command never returns answer keys; answer returns feedback after submission. For open responses use --score and --reason with the rubric. Sample questions are generated demonstrations, not official exam problems.

## Diagnosis v0.2: more defensible evidence

The CLI now tracks independent item families, different UTC dates, cognitive depth,
guessing, hints, confident errors, and reviewed misconception tags. The report
separates within-session performance from retained performance: strong evidence
requires independent questions, higher-order application and a later-day probe.

Adaptive selection responds to mistakes with easier/related probes, to guesses
with confirmation, and to successful answers with transfer or untested topics.
Questions are never repeated in one session. Every session has a limit and a
clear stop reason. These are lightweight heuristics rather than a calibrated
IRT/CAT/BKT implementation. See [diagnosis details](docs/DIAGNOSIS.md).

~~~bash
python3 scripts/qa.py start examples/sample_bank.json --mode quick --limit 6 --focus linear-equations
python3 scripts/qa.py next examples/sample_bank.json
python3 scripts/qa.py answer examples/sample_bank.json --response C --confidence guess
python3 scripts/qa.py report --bank examples/sample_bank.json
~~~

## v0.4.0 — visual analytics, student answers and offline release

A self-contained local bilingual HTML dashboard now shows knowledge prerequisites, observed cognitive-level scores, reviewer-tagged misconceptions, history, review prompts and rubric criterion scores. Generate a synthetic preview without personal learner data:

    python3 scripts/dashboard.py examples/sample_bank.json --state examples/demo_state.json --output demo-dashboard.html --lang en

Student free-form answers receive **reviewer-supported, criterion-by-criterion scoring** with evidence and actionable feedback. This validates the reviewer assessment structure and does not pretend to automatically understand all text. Short-answer semantic equivalence requires an explicit reviewed override; choice keys cannot be overridden.

A reproducible versioned ZIP with a SHA256 manifest, installation guides and unpacked-package smoke tests completes the P2 distribution workflow. See [English installation/assessment](docs/INSTALL.md), [中文版](docs/INSTALL.zh-CN.md), [release engineering](docs/RELEASE.md) and [changelog](CHANGELOG.md).

## Design constraints
Every item should be checked for provenance, deep but teachable reasoning, a unique or fully specified answer set, and fair framing. The tracker does **not** infer mastery from a single item. It shows insufficient_evidence until at least three observations from two unique item IDs per concept × cognitive level. Numeric indicators are rough formative signals, not calibrated probabilities.

## Layout
- SKILL.md — concise activation and operating protocol
- references/authoring.md — deep item quality and solution audit
- references/diagnosis.md — six-step quick-check logic
- references/subjects.md — discipline-specific question design
- scripts/qa.py — deterministic offline assessment state
- examples/sample_bank.json — self-contained algebra examples
- docs/FORMAT.md — bank format, scoring and limits
- docs/RESEARCH.md — research rationale and links
- docs/routine/ — dated changes and next-step plans
- tests/ — standard library unit/integration tests

## Privacy & token cost
State is written only to a path you choose and ignored by Git. Raw learner responses are not persisted. The assistant loads a mode reference only when relevant and uses the local engine where available. No API key, database or remote telemetry is required.

License: MIT. Contributions welcome; see docs/ROADMAP.md.

## Real-data validation (2026-11-20)

The repeatable FORGET-SE independent final-exam benchmark is implemented. On the held-out set (30 students, 279 student–concept exam outcomes), the current v0.2 evidence index gave **pooled AUC 0.515** versus historical quiz mean **0.700** and concept prior **0.757**. Its within-concept macro AUC was **0.554**, versus quiz mean **0.551**, with a learner-bootstrap difference interval spanning zero. **Predictive improvement is not established; no BKT/IRT model is deployed.** See [English validation report](docs/VALIDATION.md) / [中文报告](docs/VALIDATION.zh-CN.md).

Run your own local benchmark with `python3 scripts/evaluate.py /path/to/answers.csv`, or with publicly licensed FORGET-SE data via `python3 scripts/evaluate_forget_se.py --weekly /path/to/forget_se.csv --exam /path/to/exam.csv`. No raw personal response files are committed.


## v0.5.0 — independent item-quality audit and second real cohort
A new deterministic, offline question checker flags duplicate/near-duplicate stems, unsupported sources, inconsistent answer keys when an exact rational arithmetic witness exists, duplicate reviewer rubrics and other authoring risks. Source, pedagogical scope, ambiguity and fairness require genuinely independent item-by-item human or qualified Agent review; an all-false, bank-SHA256-bound form supports --strict publication gates.

    python3 scripts/question_quality.py examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json
    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

No source is automatically certified. The second **real** dataset evaluation uses ASSISTments 2015 mathematics learner practice (held-out 280 learners / 5,728 next-response outcomes). AUC was **0.620** for the v0.2 index versus **0.710** for simple learner history; no demonstrated predictive improvement, so no BKT/IRT model added. See [quality audit guide](docs/QUESTION_QUALITY.md) and [independent mathematics study](docs/VALIDATION_ASSIST2015.md) / [中文](docs/VALIDATION_ASSIST2015.zh-CN.md). The latest release retains the bilingual dashboard and student-response rubric review.


## v0.6.0 — independent review, explainable selection and verified cross-platform builds

A double-reviewer assessment contract is now available for manual questions. Two independently prepared rubric score packets (including exact quotations from the actual student response) are checked for agreement. Any scoring disagreement requires a third distinct adjudicator before the answer is recorded. Only numeric grade summaries enter local state; raw responses, reviewer identity and justification do not. Use --response-file to keep the raw answer out of shell history.

    python scripts/qa.py answer BANK.json --state .qa-state.json --response-file student_answer.txt --independent-reviews @reviewers.json --adjudication @arbitration.json

Adjudication is omitted only if all criterion scores agree. External teachers/Agents still have to actually review the answers; the CLI does not automatically understand arbitrary prose or prove the review is independent.

The diagnosis architecture separates observed evidence sufficiency, a fixed uncalibrated score-history baseline, and the same rule-based adaptive selection with traceable reason codes. Previously evaluated v0.2 weights are NOT tuned on either held-out test dataset. See docs/ARCHITECTURE.md and docs/ASSESSMENT.md.

Continuous integration now runs on Linux, Windows and macOS with Python 3.9/3.12. Official artifacts come from a SHA256-verified immutable Git-tagged release, never in-place updates of the existing release. See docs/RELEASE.md.


## v0.7.0 — math-equivalence, safe state and reviewer reliability
New optional answer_equivalence on explicitly numeric or polynomial short answers accepts equivalent expressions under a **strictly bounded exact algebraic subset**, not a general CAS or free-form language grader. Unverifiable answers remain pending for independent review.

New cross-platform local file locks guard the whole quiz-state transaction, saving the previous valid state atomically as STATE.bak. Use python scripts/qa.py state-check --state .qa-state.json, and for an explicit rollback python scripts/qa.py state-recover --state .qa-state.json --confirm. Backups contain study history, should remain private and may be one successful action behind.

A new private, aggregate-only scripts/reviewer_study.py reports two-reviewer agreement, quadratic weighted Cohen kappa, disagreement and uncertainty from **already-reviewed** rubric score pairs. It is not a real experiment; samples are synthetic and source type is self-declared. See [mathematical equivalence](docs/MATH_EQUIVALENCE.md), [state safety](docs/STATE_SAFETY.md) and [review study protocol](docs/REVIEWER_STUDY.md). Versioned GitHub releases remain immutable.
