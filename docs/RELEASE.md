# Release engineering and integrity — v1.2.1

[Documentation](INDEX.md) · [Published release](https://github.com/Nimenta727/Question-QA-Skill/releases/tag/v1.2.1) · [Token guidance](TOKEN_BUDGET.md)

**v1.2.1 maintenance publication:** release automation must pass the versioned cross-platform regression suite, reproducible ZIP and fresh-extraction smoke gates before creating an immutable tag. Verify the actual GitHub release assets before claiming the package is published. Expected attachments:

- `question-qa-skill-core-1.2.1.zip`: prompt-only Skill with four lazy references, README/LICENSE/VERSION and hash manifest.
- `question-qa-skill-1.2.1.zip`: compatible Python 3.9+ offline toolkit and documentation.
- `SHA256SUMS.txt`: SHA256 for both archives and `demo-dashboard.html`.
- `demo-dashboard.html`: synthetic offline example visualization, **not** demonstrated student effectiveness.

## Reproduce and verify

~~~bash
python scripts/build_release.py --all --output dist
python scripts/build_release.py --verify dist/question-qa-skill-core-1.2.1.zip
python scripts/build_release.py --verify dist/question-qa-skill-1.2.1.zip
python -m unittest discover -s tests -v
~~~

Fixed ZIP metadata/entry order, per-file `manifest.json` checksums and an explicit Core file allowlist are verified. Full requires its essential review, state and grading modules. Release CI tests both profiles on fresh extraction and requires passing gates; the previously published tag/assets are immutable.

For **downloads**, compare each archive's SHA256 against the release's separately supplied `SHA256SUMS.txt` before use. Checksums establish integrity of the released bytes, not the truth of the model's explanations, identity of the reviewer or real learning impact.

## Privacy and historical guidance

Never bundle real learner data, unauthorized course extracts, reviewer secrets or real audit packets. Do not force Python or long research history into normal Core conversations. Version-specific old guides and former release plans are available through [Git tags](https://github.com/Nimenta727/Question-QA-Skill/tags) and [Git history](https://github.com/Nimenta727/Question-QA-Skill/commits/main/), rather than active installation links. New main-branch documentation changes do **not** retroactively mutate the already published v1.2.1 release assets.

## Empirical testing remains separate from release CI

See the [12 real-model tests](REAL_MODEL_TESTS.md) and [verification ledger](TEST_STATUS.md). The release gates verify reproducibility, compatibility, integrity and code behavior—not independent semantic item accuracy, reviewer recall, calibrated mastery, or causal learning gains. Every RM case remains **NOT RUN** until evidence is linked.
