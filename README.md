# Question-QA-Skill — Rigorous questions and adaptive formative tutoring

[简体中文](README.zh-CN.md) · [Documentation index](docs/INDEX.md) · [Changelog](CHANGELOG.md)

**Purpose:** Ask a small number of accurate, source-grounded questions; inspect the learner's observed reasoning; choose one informative follow-up at a time. A correct response is not proof of long-term mastery.

## Choose the package

| Edition | Contents | Recommended for |
|---|---|---|
| **Core — lightweight (recommended)** \`question-qa-skill-core-1.2.0.zip\` | Short SKILL.md + four **on-demand** teaching references, no scripts/tests/research history | Everyday AI conversation, lowest default context |
| **Full** \`question-qa-skill-1.2.0.zip\` | Same pedagogical guidance plus offline Python CLI, source-bound review gate, tests, bilingual docs and history | Local banks, learning records, tooling or development |

Both archives have SHA256 manifests. Archive byte size is **not** equal to inference token usage; host Skill loading and source/question context determine actual usage. Read only SKILL.md by default, then the relevant reference. See [token budget and design](docs/TOKEN_BUDGET.md).

## Get started

1. Obtain either ZIP and SHA256SUMS.txt from [Releases](https://github.com/Nimenta727/Question-QA-Skill/releases).
2. Verify the archive checksum, extract and register the folder with an Agent Skills-compatible assistant (or explicitly ask your assistant to read SKILL.md).
3. Provide the actual course materials and ask: "Test my understanding with one question at a time, then choose each follow-up from my observed reasoning. Do not show the answer before I respond."

Alternative prompts: "Create five rigorous but fair course-aligned questions; withhold keys until submission." / "Use at most six questions to find my C pointer reasoning gaps."

## Teaching and audit commitments

- **QUICK:** wrong but cause unknown → clarify reasoning; guessed or hinted correct → new independent item family; partial credit → one missing criterion; justified success → transfer/boundary probe.
- **DEEP:** select specific curriculum claims; verify solutions, equivalents, cognitive alignment, fair grading and scope.
- **Pre-question audit:** independently solve before comparing the draft key; check second answers, counterexamples, source citations, distractors/rubrics and unresolved risks. A failed or uncertain question is revised or withheld. Same-model self-review is not independent review.
- **Scientific limits:** heuristic indices are not calibrated mastery probabilities; passing synthetic regressions is not evidence of improved learning or actual LLM semantic accuracy. High-stakes exams require qualified human review.

On-demand detailed guides: \`references/tutoring.md\`, \`references/authoring.md\`, \`references/model_audit.md\`.

## Full edition: optional offline CLI

Python 3.9+, no pip dependency and no automatic model API calls:

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py next examples/sample_bank.json --state .qa-state.json
python scripts/qa.py answer examples/sample_bank.json --state .qa-state.json --response C
python scripts/qa.py report --state .qa-state.json --bank examples/sample_bank.json
~~~

\`scripts/model_audit.py\` checks the structure, source/hash binding and certain objective answer consistency of **an actual reviewer-produced record**; it does not run an LLM or prove semantic correctness. See [install guide](docs/INSTALL.md) and [model audit](docs/MODEL_AUDIT.md).

## Project status

The Skill has software regression coverage, but its performance on real curriculum questions, diagnostic accuracy and learner outcomes **still need independent empirical assessment**. A separate project-development two-agent PR does not require two extra models for each learner interaction, and unperformed independent reviews are not claimed.

MIT licensed. Keep actual learner records, unauthorized lesson excerpts and reviewer secrets out of public repositories.
