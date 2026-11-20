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
