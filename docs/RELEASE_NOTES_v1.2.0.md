# Question-QA-Skill v1.2.0 — Lightweight Core & Full release

## 重点：真正适合日常聊天的轻量发行

Users now choose between:
- **Core:** \`question-qa-skill-core-1.2.0.zip\` — one compact SKILL.md, four on-demand references, a tiny README, VERSION, LICENSE and a SHA256 manifest. No runtime scripts, tests, real user data or historical research files.
- **Full:** \`question-qa-skill-1.2.0.zip\` — the existing complete offline Python toolkit and every historical document/test/example, still reproducible and checksum-verified.

The primary Skill file is approximately **1,965 characters**, down from ~4,018 (~51% fewer characters). Detailed model audit guidance shrank from ~6,127 to ~1,306 characters, loaded only when needed. These are **source text measurements, not exact tokenizer counts or guaranteed token-billing savings**.

## Documentation and release quality
- Updated bilingual README and installation guides to current version and two-package choices.
- Created \`docs/INDEX.md\` / \`docs/INDEX.zh-CN.md\`, \`docs/TOKEN_BUDGET.md\` / .zh-CN.md for progressive disclosure and context sizing.
- Archived previous lengthy installation and release instructions under \`docs/archive/\`; earlier releases and Git history remain unchanged.
- Both packages are built deterministically and independently verified with SHA256 manifests. Release checksums cover both ZIPs and the demo dashboard. CI verifies the Core file allowlist and context budget, and repeats the test suite in an extracted Full archive across supported platforms.

## Scope and limitations
This release improves deployment and prompt organization, **not** learner-model parameters or measured educational results. Strict course-source, independent solution, alternative answers, ambiguity, distractor/rubric and uncertainty checks remain mandatory before presenting new questions. Full's offline \`model_audit.py\` validates a recorded model-review packet; it does not invoke a reviewer model or prove semantic correctness. Formal tests require qualified human review.

The separate two-agent **repository development** proposal is not bundled as a student-facing multi-agent question workflow. Its independent audit remains subject to its own PR and permissions.
