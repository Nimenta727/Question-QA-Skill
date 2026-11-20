# Two-agent PROJECT development protocol

This process governs development of the GitHub repository, **not** the student-facing author/reviewer model inside the Skill.

Agent A (\`.github/agents/feature-builder.agent.md\`) implements a single approved feature, tests it, commits a dated \`docs/routine/\` log with every modification, and opens a PR. It cannot approve its own work.

Agent B (\`.github/agents/quality-auditor.agent.md\`) runs in a **separate agent session**, investigates the diff independently, challenges functionality and claims, attempts to reproduce issues, and writes a commit-scoped PR review (BLOCKED / REVISE / ACCEPTABLE_FOR_REVIEW). It chooses exactly ONE next development priority and its observable acceptance criteria. It does not implement the reviewed feature or merge.

The controller relays requested changes to A and asks B to re-review the revised HEAD. A new commit invalidates the previous review. CI and human/maintainer decisions control merge and immutable releases. Synthetic tests cannot prove improved learning outcomes, and a model review does not establish a qualified human assessment.

GitHub Copilot supports repository custom agents under \`.github/agents/*.agent.md\`. Profiles alone do not start agent sessions; invoking truly independent sessions and configuring repository permissions / required reviews depends on the repository owner's Copilot entitlement and settings. In a ChatGPT session without an actual subagent invocation tool, a second pass must be labeled **provisional same-session review**, not independent Agent B execution.

See the Chinese protocol, \`docs/PROJECT_TWO_AGENT_WORKFLOW.zh-CN.md\`, for the full audit checklist and reporting template.
