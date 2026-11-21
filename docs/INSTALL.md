# Install and verify v1.2.1

[Home](../README.md) · [Documentation](INDEX.md) · [Official release](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.1)

## Core — recommended for conversational study
1. Download `question-qa-skill-core-1.2.1.zip` and `SHA256SUMS.txt` from the **published** v1.2.1 release.
2. Compare the ZIP's SHA256 with the value in the checksum file using your operating system's SHA256 utility.
3. Extract and register the Core folder in an Agent Skills-compatible host, or ask the assistant to read its `SKILL.md`.
4. Load **only SKILL** initially; consult `references/tutoring.md`, `references/authoring.md`, `references/model_audit.md` or `references/subjects.md` only when needed.

Ask: “Use my supplied C-language lesson to test understanding one question at a time, then probe the reasoning behind each answer.” If the source was not provided or verified, the questions are generic practice.

## Full — optional offline Python toolkit
Download `question-qa-skill-1.2.1.zip`. Python 3.9+; no third-party packages.

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

On Windows, `py -3` may replace `python`. The example data is synthetic. See [model-review evidence](MODEL_AUDIT.md) for optional strict gating: **no model is called by the CLI**, and a schema pass does not certify independent reasoning.

## Package, privacy and historical versions
Each ZIP contains `manifest.json` listing file SHA256 digests; `SHA256SUMS.txt` checks the entire downloaded archive. See [release procedure](RELEASE.md) for deterministic build commands and tests. Do not commit learner state, private course excerpts, reviewer identity credentials or audit secrets.

Old installation instructions remain retrievable via [Git tags](https://github.com/Nimenta727/Question-QA-Skill/tags) and [repository history](https://github.com/Nimenta727/Question-QA-Skill/commits/main/), rather than active documentation files.
