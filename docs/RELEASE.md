# Release engineering / 发行与完整性说明

## What is officially shipped
- Version: 0.6.0; Agent Skill root contains SKILL.md.
- Archive: question-qa-skill-0.6.0.zip, plus SHA256SUMS.txt.
- A reproducible SHA256 manifest is embedded as manifest.json.
- GitHub CI verifies the bank, runs full unit tests, builds the archive, checks file hashes, extracts it into a fresh directory and performs command-line smoke tests including dashboard generation.

## Security and scope
- Only files from an explicit allowlist are released (SKILL, READMEs, LICENSE, VERSION, CHANGELOG, references, scripts, examples, docs and tests).
- .env, Git metadata, private state files, research-data, cached files, raw student text, and external downloaded datasets are not distributed.
- No external online dependencies, model APIs, built-in browser extension or automatic LLM scoring is required.
- The publicly shipped demo history is synthetic and intentionally has no real learner identifying fields.
- Only author-approved/checked response reviews may use the criterion scoring tool. For semantic equivalence, a reviewer must explicitly authorize the override with a rationale.
- No validated predictive advantage or mastery probability is claimed by the release.

## Installation
See docs/INSTALL.zh-CN.md or docs/INSTALL.md. Release sources are MIT licensed; public FORGET-SE research inputs are separately licensed upstream (CC BY 4.0) and are not redistributed.

## Publishing and reproducibility
The release workflow builds the package from main and (if GitHub Actions has contents:write permission) creates v0.6.0 on GitHub Releases after all tests and smoke checks pass. If repository policy blocks publication, the validated ZIP is still uploaded as a workflow artifact and the release must be published by a repository maintainer with suitable permission. Never claim the release exists without checking the result.

Rebuild and verify:

    python3 scripts/build_release.py --output dist
    python3 scripts/build_release.py --verify dist/question-qa-skill-0.6.0.zip

Compare the ZIP digest to SHA256SUMS.txt. The ZIP has a deterministic directory structure and frozen metadata timestamps, allowing byte-for-byte repeat builds from the same Git revision.

## Post-release next steps
1. Independently review question-bank quality and semantic-equivalence scoring for more subjects.
2. Collect consent-based, privacy-preserving, independently labeled learning sequences for diagnosis calibration; keep the test set untouched.
3. Extend dashboard with optional export of aggregate-only summaries (not student raw text) and accessibility testing.
4. Consider optional, separately validated BKT/IRT only after robust real-data comparisons.


## v0.6.0 additional gate
The CI invokes the question-quality audit for the example bank and requires zero **hard errors** in schema/duplicate/numeric witness checks. It does NOT auto-certify the example bank's curriculum correctness: professional review remains required before a real exam. ASSISTments2015 is evaluated separately from FORGET-SE; no student-level rows enter release assets.


## v0.6.0 immutable release contract
The release workflow now includes Ubuntu/Windows/macOS Python3.12 full regression tests and ZIP verification before a separate Ubuntu reproducible build, SHA256 validation and clean-extraction smoke test. The publish job is the only part granted contents:write and checks that the successfully tested commit still equals the current main HEAD. It creates a lightweight v0.6.0 Git tag and Release only if neither exists. A later main commit triggers unversioned CI artifacts, NEVER an in-place replacement of v0.6.0 release assets. Pre-existing tags without a corresponding Release are treated as an error requiring human investigation. Updating source code after publication requires a new version number and tag.
