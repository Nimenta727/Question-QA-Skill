# Installation — Question-QA-Skill v1.2.0

[Home](../README.md) · [Documentation index](INDEX.md)

## Core: recommended for the smallest default model context

Download \`question-qa-skill-core-1.2.0.zip\` and \`SHA256SUMS.txt\` from the official GitHub release. Verify, extract, and install/register the extracted directory with an Agent Skills host (or ask the assistant to read SKILL.md).

Only SKILL.md needs to be in normal initial context. Read \`references/tutoring.md\` for deeper QUICK strategies, \`references/authoring.md\` for DEEP questions, \`references/model_audit.md\` for difficult question verification and \`references/subjects.md\` only for the relevant discipline. Do **not** pre-load all source files or research history.

## Full: optional offline Python toolkit

Download \`question-qa-skill-1.2.0.zip\`, extract and use Python 3.9+ (no pip dependencies):

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

Use \`py -3\` on Windows where appropriate. The sample question bank and history are synthetic demonstrations, not a real instructor's curriculum or human student study.

The full archive includes a strict optional \`scripts/model_audit.py\` packet gate: it validates evidence **already written by a genuine reviewer model**, rather than running any LLM. Use [model audit instructions](MODEL_AUDIT.md) when you need it. Legacy review, appeals, cryptographic local audit and research utilities are indexed in [documentation index](INDEX.md).

## Verification and privacy

The downloadable SHA256SUMS.txt authenticates each released ZIP against the published digest; inside each ZIP, manifest.json enumerates file hashes. Packaging CI tests both and runs the full suite on a fresh Full extraction. Do not publish private learner histories, reviewer credentials or unauthorized course text. For older commands consult \`archive/INSTALL_PRE_V1_2.md\`, which is historical rather than recommended.
