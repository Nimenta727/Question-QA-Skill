# Release engineering — v1.2.0 / 发行与完整性

[Documentation](INDEX.md) · [Token optimization](TOKEN_BUDGET.md) · [Historical release notes](archive/RELEASE_PRE_V1_2.md)

## Two supported artifacts

- **Core (recommended for normal Agent Skill installation):** \`question-qa-skill-core-1.2.0.zip\` contains a short SKILL, four on-demand references, an installation README, LICENSE, VERSION and manifest. No Python, tests, researcher notes, private learner data or external API.
- **Full (offline developer / teacher toolkit):** \`question-qa-skill-1.2.0.zip\` retains scripts, tests, references, bilingual docs, examples, dated development records and historical reports.

Both profiles are immutable, reproducibly sorted archives with frozen metadata timestamps. Every file has a digest in \`manifest.json\`; the separately released \`SHA256SUMS.txt\` authenticates the Core ZIP, Full ZIP and generated demo dashboard.

## Reproducible build and verification

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.0.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.0.zip
python -m unittest discover -s tests -v
~~~

Core verifies an exact eight-file allowlist and its SKILL character budget. Full verifies the required evaluator, audit and state modules. Validation rejects unsafe ZIP paths, duplicate entries, profile mismatches and SHA256 inconsistencies. The release workflow runs three-OS gates, builds both profiles, checks the digest list and tests a fresh Full extraction and a Core smoke test before creating an immutable new tag.

## Privacy / provenance boundaries

The public archive includes only synthetic example questions and student histories. Exclude raw learner submissions, private educational sources, reviewer registries/tokens, audit keys and actual review packets. A checksum validates *bytes*, not correctness of generated questions or genuine independent model review. Tests do not establish learning gains.

A GitHub Release is published only when the tested commit is still current main and the new tag does not exist; older tags/assets are never replaced. If publication permissions or independent review requirements cannot be met, retain the validated PR and CI artifacts rather than claiming a release exists.
