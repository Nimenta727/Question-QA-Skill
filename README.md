# Question-QA-Skill — Rigorous questions and adaptive learning checks

[简体中文](README.zh-CN.md)

> **A small Agent Skill that asks better questions, observes reasoning and chooses a useful follow-up.** It is not an examination administration system or a calibrated mastery predictor.

## Use directly in an AI conversation

Install as an Agent Skills-compatible skill or have your assistant read SKILL.md, then ask:

- "Give me a six-turn diagnostic on today's data structures lesson. Ask one question at a time and adapt to my answer."
- "I confuse stacks and queues. Start with one question, then probe the exact step I may be missing."
- "Create five deep but fair questions anchored in the instructor's slides. Do not show answers until I submit."
- "Try another representation instead of repeating the same exercise."

QUICK defaults to six one-at-a-time probes. DEEP defaults to five independently checked, scope-aligned questions. The student may stop at any point.

## What the tutor does after an answer

| Observed response | Next pedagogical move |
|---|---|
| Incorrect, cause unknown | Clarify the reasoning or test a prerequisite; **do not invent a misconception** |
| Correct but guessed or helped | Verify independently in a distinct item family, without hints |
| Correct with a sound explanation | Try transfer, an application or a boundary case |
| Partly correct on an explicit rubric | Target one missing criterion instead of demanding a full redo |
| No suitable question remains | Author and validate a new, source-faithful variant before asking |

The short primary workflow lives in [SKILL.md](SKILL.md), with specific adaptive tutoring guidance in [references/tutoring.md](references/tutoring.md) and deep question quality standards in [references/authoring.md](references/authoring.md).

## Optional offline helper, no model API or external dependencies

Python 3.9+:

~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python3 scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python3 scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

next now returns the student-safe question plus an internal tutor_intent; answer returns evidence-grounded feedback plus a tutor_next_move; report supplies a teaching_summary of observed coverage and unresolved evidence. The assistant should translate internal plans into short conversational feedback and exactly one next question—not print the internal JSON at the learner.

The local scorer does not automatically understand arbitrary natural-language responses. Open responses require a reviewed rubric; ambiguous or equivalent answers require clarification or careful review, not a silent zero. The example algebra bank is synthetic and does not claim to represent anyone's actual course material.

## Scientific and privacy limits

A correct answer, repeated near-duplicate or same-day streak is not proof of durable learning. The existing evidence index is descriptive, **not** a calibrated mastery probability; two earlier external studies did not demonstrate reliable predictive improvement over simpler historical baselines. Behavior tests verify the software chooses the intended tutoring branches but do **not** establish high-quality LLM question generation or improved student learning. See [pedagogical review rubric](docs/TEACHING_EVALUATION.md) and [evidence](docs/VALIDATION.md).

Historical tools for double review, correction appeals, data lifecycle, tamper-evident local audits, research preparation and dashboards are preserved but **not required** for ordinary tutoring. See [optional operations](references/operations.md) and [changelog](CHANGELOG.md). MIT licensed, offline by default; protect any real learner data appropriately.
