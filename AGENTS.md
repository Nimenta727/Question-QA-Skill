# Question-QA-Skill repository contributor / coding-agent instructions

**Project purpose:** a lightweight AI Skill that creates fair, source-grounded questions, asks ONE at a time, interprets observed learner evidence cautiously and adapts the next probe. The Skill is NOT primarily a grading administration platform.

## The two development agents are not the Skill's question-writing/reviewing submodels
- **Agent A (feature-builder)** writes project code, tests and documentation on a feature branch.
- **Agent B (quality-auditor)** reads the PR independently, tries to find defects, audits functionality and chooses the next P0/P1 development task. Agent B must not fix its own review target.
- The controller/maintainer routes the findings back to Agent A; critical or unverified issues block merge. There is no automatic feature expansion or automatic release.
- The repo agent definitions live in \`.github/agents/\`. They are *configuration*, not proof that two agents have actually run. Independent execution has to be observed as separate sessions/reviews. See \`docs/PROJECT_TWO_AGENT_WORKFLOW.zh-CN.md\`.

## Hard quality standards
- No invented real-world teacher materials, no claim of calibrated mastery probabilities, no automatic misdiagnosis from a single wrong answer.
- Do not allow independent answer key/rubric content into the student-facing prompt, or casually claim that a self-review is an independent model audit.
- Use Python standard library where practical; preserve Python 3.9 and 3.12 behavior, UTF-8 file IO and Windows paths. Run \`python -m unittest discover -s tests -v\`.
- In every GitHub modification commit add a uniquely named, dated \`docs/routine/\` entry: exact changes, tests, caveats and next step. Do not replace old logs.
- Prefer PRs and commit-scoped review. A changed PR head invalidates prior code-review conclusions.
- Do not disclose private student data, token files, model API keys or copyrighted lesson material.

## Release discipline
Never relabel an existing tag or overwrite immutable release files. User-facing claims of release, independent audit or multi-platform tests require actual evidence.
