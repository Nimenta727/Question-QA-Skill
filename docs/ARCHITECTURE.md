# Current architecture — Question-QA-Skill v1.2.1

[Documentation](INDEX.md) · [中文首页](../README.zh-CN.md) · [Validation plan](QUALITY_VALIDATION.md)

## 1. Two layers, not two required learner-facing models

**Agent Skill (Core):** `SKILL.md` sets the contract for QUICK (one question, observe answer and reasoning, choose one follow-up) and DEEP (source-aligned deeper questions). Four `references/` files are read **only on demand**. A conversational assistant can use Core without Python, a database, a model API client or dedicated hosting.

**Optional offline toolkit (Full):** Python standard-library modules support a persisted question bank, deterministic grading/record handling, auditable prompt guidance, export/review tools, research scripts and packaging. They do **not** understand arbitrary free-text reasoning, generate new questions, call an LLM, or certify independent semantic review. Project-development builder/reviewer agents are a separate GitHub governance workflow, not a requirement for QUICK.

## 2. Live conversational teaching flow

~~~text
Course material actually read -> scoped knowledge claim -> draft item
-> blind solve and adversarial review -> show one safe question
-> learner response and reasoning -> verify grade or ask clarification
-> targeted follow-up in an independent family -> cautious summary / stop
~~~

- **Source scope:** never invent an instructor quote or page. Unavailable course material means general practice, clearly labeled.
- **Question gate:** derive the answer independently, check equivalent answers, assumptions, second correct choices, all distractors/rubric criteria, cognitive demand, fairness and novelty. Stop/revise if a material risk is unresolved.
- **Decision:** wrong with unknown cause => request reasoning/prerequisite; uncertain or assisted success => independent recheck; partial score => missing criterion; justified success => boundary or transfer. Do not diagnose a misconception solely from a wrong response.
- **Completion:** stop when asked, at the selected budget, or when no verified useful item is available. Report observed evidence and untested areas, not lifetime mastery.

## 3. Actual Full module responsibilities

| Layer | Files | What is and is not established |
| --- | --- | --- |
| CLI / bank / events | `scripts/qa.py` | Validates bank schema and runs deterministic local workflows; no model-generated keys or semantic free-text grading |
| Pedagogical next move | `scripts/tutor_core.py` | Maps already-recorded evidence to compact follow-up intents; cannot independently assess a student's prose |
| Descriptive evidence | `scripts/diagnosis.py`, `scripts/evidence_engine.py` | Historical heuristic scores/coverage; not a calibrated probability of knowledge |
| History baseline / routing | `scripts/prediction_engine.py`, `scripts/adaptive_engine.py` | Comparison baseline and rule-based selection, not validated information gain or causal teaching benefit |
| Question checks | `scripts/question_quality.py`, `scripts/model_audit.py` | Static checks plus verification of reviewer-produced JSON/source digests; not a running independent reviewer |
| Corrections / local integrity | `scripts/appeals.py`, `scripts/state_store.py`, `scripts/audit_ledger.py` | Optional evidence changes, transactional state and local audit mechanisms; not institutional identity certification |
| Evaluation / packages | `scripts/evaluate*.py`, `scripts/build_release.py` | Historical external-data comparisons and deterministic release builds; not live mastery measurement |

The shipped Skill/CLI API is deliberately **not** rewritten as a new platform. Existing versioned state and score semantics remain as implemented; see [diagnosis details](DIAGNOSIS.md) and the software tests.

## 4. Evidence boundaries

- Passing unit, package and cross-platform CI tests supports code behavior and reproducibility, not whether authored questions are actually correct in every subject.
- A JSON record passing `model_audit.py` is not proof that an independent reviewer solved the problem or that its explanation is accurate.
- The legacy descriptive index failed to demonstrate a consistent predictive gain over simple history baselines in the independent datasets already evaluated. [Results](VALIDATION.md)
- Only a suitably approved independent educator/expert protocol can support strong educational claims or official assessment use. [Preregistered evaluation design](QUALITY_VALIDATION.md)

## 5. Cost and data policy

Read `SKILL.md` first, then one relevant `references/` file, and only the necessary source excerpt. Do not stream the Full development history into each tutoring context. Keep private student responses, identities, credentials and unauthorized teaching material outside public commits and release artifacts.

For prior implementations and superseded architecture narratives, consult [Git tags](https://github.com/Nimenta727/Question-QA-Skill/tags) rather than treating older design notes as current.

## Real-model validation handoff (not completed)

Actual curriculum-grounded author accuracy, independent audit miss and false-alarm rates, diagnostic follow-up correctness, fixed-sequence comparisons, billed tokens, delayed retention and fairness have **not** been validated by offline Python or CI. See [RM-01–RM-12 matrix](REAL_MODEL_TESTS.md) and [status ledger](TEST_STATUS.md); the evidence requirements must be satisfied before making performance claims.
