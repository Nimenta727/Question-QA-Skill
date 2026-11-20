# Question-QA-Skill repository-wide Copilot instructions

The repository's primary goal is question quality and adaptive educational diagnosis, not a multi-user school administration platform. Default changes should make a source-faithful, auditable one-question-at-a-time learning loop better without increasing student-context complexity.

There are TWO PROJECT DEVELOPMENT roles:
- \`.github/agents/feature-builder.agent.md\`: implementation, tests, docs, PR.
- \`.github/agents/quality-auditor.agent.md\`: independently investigate code and tests in a PR, report defects and decide ONE next priority. It does NOT implement a fix or self-approve.

For code review: validate requirements against the actual diff; cite specific files and reproducible issues. Challenge false claims of semantic certainty, curriculum validity and learner mastery. Be attentive to Python 3.9/3.12, UTF-8 cross-platform behavior, offline-first constraints, source provenance and release exclusions.

On EVERY GitHub modification include an appropriately dated \`docs/routine/\` changelog with exact changes, tests/limitations and next steps. Do not alter prior version tags/releases. Do not claim that writing agent profile files means two agents were actually invoked.
