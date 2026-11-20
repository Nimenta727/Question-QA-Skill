# v0.8.0 authorized independent two-reviewer trial: preparation and freeze

**Current status: software for trial preparation, separate randomized assignment packets and first-round scoring freeze is implemented, but no real students, recruited reviewers or actual institutional authorization have been provided. No real-world human trial has been conducted.**

Before collecting any real student submissions, an institution or qualified study lead must verify appropriate ethics/permissions/consent (including guardian requirements where relevant), independently reviewed rubrics, qualified reviewer assignments, private answer storage, a predefined analysis plan, an adjudication process and a student appeal pathway.

The local study plan contains only study_type, authorized, rubric_frozen and case_ids_and_criterion_counts (opaque pseudonyms and rubric length). For real usage, set study_type=authorized_real_self_declared and authorized=true **only after genuine external verification**; this is still a self-declaration, not proof obtained by software. A synthetic plan with authorized=false can be tested immediately.

    python scripts/reviewer_trial.py prepare --plan examples/sample_trial_plan.json --output-dir trial-private-demo

The command creates a private manifest and two independently shuffled task packets for reviewer A and reviewer B containing only case identifiers and rubric counts. They do not expose the other reviewer’s scores, student responses or answer keys. Truly independent reviewers and private access to source answers must be arranged externally.

After both reviewers independently finish round-one assessment, create separate files:

    {"reviewer_slot":"A","cases":[{"case_id":"anon-01","scores":[1,0.5,0]}]}

The file must cover exactly the same set of cases and fixed rubric lengths as the prepared manifest; reviewer B uses slot B. Freeze only after both submit, and **before any third-party adjudication**:

    python scripts/reviewer_trial.py freeze --manifest trial-private-demo/private-manifest.json --review-a trial-private-a.json --review-b trial-private-b.json --output trial-first-round-aggregate.json

The result includes a first-round stage marker, SHA256 checksums of both structured review packets and aggregate agreement/uncertainty, never case IDs, raw student responses or reviewer personal details. Hash commitments are not timestamps signed by a trusted institution and cannot authenticate identity, independent work, consent or scoring correctness. Arrange separate expert validity checks and third-reviewer adjudication, and publish only permitted aggregate statistics.

No research participant data is collected or uploaded by these commands. Protect private plan, answer and rating files from release archives or public commits. Read docs/REVIEWER_STUDY.md for statistical cautions.


## v0.9.0: external expert-reference comparison after first-round freeze
Reviewer A/B agreement alone cannot detect shared grading mistakes. After freezing both independent first-round packets, obtain a separate, curriculum-grounded expert reference under appropriate authorization and compare each reviewer with that reference using scripts/reviewer_pilot.py. The analysis includes criterion-level reference agreement, absolute score differences, reviewer consensus that disagrees with the expert and a cluster-bootstrap interval.

See [REFERENCE_PILOT.md](REFERENCE_PILOT.md) for the exact private input contract and the limitations of the benchmark. The supplied expert reference, blindness, reviewer competence, consent and actual educational correctness must all be established independently; this software does not certify them.
