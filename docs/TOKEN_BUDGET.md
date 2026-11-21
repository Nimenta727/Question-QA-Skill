# Token footprint and progressive disclosure — v1.2.0

The default \`SKILL.md\` was reduced from approximately **4,018 to 1,965 characters** (about **51% less prompt text**). The detailed review reference was shortened from roughly 6,127 to 1,306 characters. The **Core** ZIP now contains only eight substantive files plus a SHA256 manifest; the **Full** ZIP retains the entire offline toolkit and history.

These measurements are **character counts, not model token counts**. Actual tokens depend on the model tokenizer, Skill host loading strategy, conversation history and course content. A small ZIP does not automatically mean low inference cost.

## Progressive disclosure policy

1. Initially load SKILL.md only. Do not load READMEs, scripts, tests, all references or historical documentation.
2. For QUICK, optionally consult tutoring.md once if the next move is uncertain. For DEEP, consult authoring.md; read only the relevant subject paragraph in subjects.md.
3. Keep the strict audit gate in the primary Skill. On difficult correctness, ambiguity or verified source provenance questions, consult model_audit.md rather than reloading long protocols for every ordinary prompt.
4. Extract just the relevant, verifiable course sections; never invent page numbers or re-send complete instructor PDFs every turn.
5. Learner-facing response: concise substantiated feedback and **one** next question. Do not print full internal assessment JSON.
6. End early if useful information has been obtained or the student asks to stop. Do not sacrifice correctness or independent evidence to reduce token spend.

Full is only needed for persistent learning states, bank/schema checks, strict JSON-based audit gates, research and developer workflows.

Verify both release profiles using \`python scripts/build_release.py --all --output dist\`, \`--verify PATH\`, and \`python -m unittest discover -s tests -v\`. Those regressions establish structural controls, **not** a guaranteed billing reduction or measured educational improvement.
