# Question-QA-Skill

**Source-grounded question writing · one-question-at-a-time diagnosis · evidence-first tutoring**

[简体中文](README.zh-CN.md) · [Documentation](docs/INDEX.md) · [v1.2.2 release / verification](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.2) · [Roadmap](docs/ROADMAP.md)

Question-QA-Skill helps an assistant ask fewer, better questions: ground each item in material actually supplied, verify its answer and alternatives, observe a learner's reasoning, and choose the next probe based on that evidence. **A correct answer does not establish durable mastery.** It is a reusable Agent Skill, not a hosted education platform or an automatically calibrated diagnostic model.

## Choose a distribution

| Edition | Intended use | Contents |
| --- | --- | --- |
| **Core** (recommended) — `question-qa-skill-core-1.2.2.zip` | Normal AI conversations with minimal initial context | `SKILL.md`, four on-demand references, minimal README, LICENSE, VERSION and manifest |
| **Full** — `question-qa-skill-1.2.2.zip` | Offline question banks, review evidence and developer workflows | Core guidance plus Python 3.9+ standard-library CLI, examples, tests, bilingual documentation and research records |

Both archives and `SHA256SUMS.txt` are available in the **published v1.2.2 GitHub Release**. Verify the downloaded checksums before extraction. The smallest package is not necessarily the cheapest model invocation: read **only `SKILL.md` by default**, and load a reference only when needed. [Installation](docs/INSTALL.md) · [Token policy](docs/TOKEN_BUDGET.md)

## Use the Skill

1. Install the Core directory in an Agent Skills-compatible host, or ask your assistant to read `SKILL.md`.
2. Supply course material you are allowed to use; specify subject, scope and goals.
3. Prompt: **“Ask me one course-grounded question at a time. After each answer, inspect my reasoning, give concise feedback and choose one informative follow-up. Withhold the answer until I respond.”**

**QUICK** defaults to up to six adaptive rounds, with a stop-on-request rule. **DEEP** creates a small set of answer-verified, course-aligned questions, separating learner-facing tasks from later solutions. Without accessible materials, the assistant must label its work **general practice**, not invent course sources. New or revised questions must be independently solved and challenged for ambiguity, alternatives, source mismatch, distractor/rubric defects, fairness and diagnostic value before presentation.

## After Skill testing: compact visual report (Full only)

After a model **actually uses this Skill** on a frozen, permissioned test set, an independent reviewer or evaluation harness may record the observed decisions. Full then renders a **small, offline HTML report** with three conditional, denominated metrics; one short defect-category visual; prioritized failures; and expandable evidence. The renderer **does not invoke a model** or authenticate reviewers.

[Method, schema and sources](docs/SKILL_EVAL_REPORT.md) · [RM-01–RM-12 still to run](docs/REAL_MODEL_TESTS.md). Preview with **synthetic-only** data:

~~~bash
python scripts/skill_eval_report.py examples/synthetic_skill_eval.json --output dist/skill-eval-demo.html --lang en
~~~

## Optional Full edition: offline CLI

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

The offline CLI **does not call an LLM**. `scripts/model_audit.py` verifies the structure and provenance of **an already-completed** model-review record; it does not perform or prove independent semantic review. [Review protocol](docs/MODEL_AUDIT.md) · [Architecture](docs/ARCHITECTURE.md)

## Real tests still required — not yet completed

These are **planned empirical tests**, not software regression tests or already-validated capabilities. The full [RM-01–RM-12 test matrix](docs/REAL_MODEL_TESTS.md), [status ledger](docs/TEST_STATUS.md) and [blank report](docs/validation/REPORT_TEMPLATE.md) define inputs, independent reference labels, metrics, denominators and reporting.

| Priority | Actual independent test still needed | Status |
| --- | --- | --- |
| P0 | C/programming **and non-programming** source-grounded question accuracy, citations and cognitive alignment | **NOT RUN** |
| P0 | Audit missed bad keys, second valid choices, ambiguity, fake citations and rubric defects; measure false alarms on sound items | **NOT RUN** |
| P0 | Evaluate guessed/hinted/partial/wrong responses and safe adaptive follow-ups against a frozen fixed-sequence baseline | **NOT RUN** |
| P1 | Measure real model input/output tokens, call count and latency under matched Core/Full conditions | **NOT RUN** |
| P1 | Authorized delayed retention, independent expert agreement, fairness and learner outcomes | **NOT RUN** |

**Release does not certify these items.** Failed cases and uncertainty must be reported with independent reference labels and eligible denominators. Real learner trials require suitable authorization and privacy safeguards.

## Evidence, limitations and development status

- **Verified engineering:** v1.2.2 Core/Full distribution and cross-platform regression workflow completed successfully on November 21, 2026. This is software verification, **not** teaching effectiveness.
- **Not validated as learning measurement:** published offline tests have not established an advantage of the legacy descriptive index over simple history-based baselines. Do not report heuristic scores as calibrated mastery probabilities or a single correct response as retention. [Research evidence](docs/VALIDATION.md)
- **Independent item quality still to test:** formal question-authoring accuracy, model-audit miss/false-alarm rates, diagnosis of real reasoning, and adaptive-versus-fixed follow-up benefit remain research priorities. [Evaluation plan](docs/QUALITY_VALIDATION.md)
- **Separate developer agents:** repository-builder and independent PR-auditor work is distinct from learner interactions; no two-model runtime requirement is implied. Actual reviewer evidence must be recorded before claiming independent review.

See the [documentation index](docs/INDEX.md) for the active guides and [Git history](https://github.com/Nimenta727/Question-QA-Skill/commits/main/) / [tags](https://github.com/Nimenta727/Question-QA-Skill/tags) for superseded designs. Dated changes remain in `docs/routine/`.

**License:** MIT. Do not commit private learner state, unauthorized course text, reviewer credentials or private audit packets. Official high-stakes assessments require qualified human review.
