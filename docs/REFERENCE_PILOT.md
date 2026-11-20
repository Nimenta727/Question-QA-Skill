# v0.9.0 independent expert-reference evaluation protocol

**Status: implementation and synthetic regression only. No real human-student trial has been run.** This tool compares two frozen reviewers' ordinal rubric scores with a separately provided expert reference; it does not certify the correctness or independence of any human assessor.

## Why compare a separate reference?
High reviewer inter-rater agreement can conceal common mistakes. If both assessors grade the same response incorrectly, agreement statistics alone look excellent. Independently assembled expert-reference ratings can reveal such shared disagreements, provided the expert criteria themselves are valid.

## Before involving real participants
Obtain all required school/institution approvals, permissions and applicable student/guardian consent. Prespecify the items, rubric, participants, primary outcome, analysis plan and follow-up procedure. Freeze the two blinded A/B first-round review packets *before* revealing either peer judgments or the independent specialist reference. Keep the mapping to original student answers in a protected, institution-controlled store outside GitHub.

## Input and commands
First execute scripts/reviewer_trial.py prepare and freeze, saving the prepared private manifest, the two original reviewer A/B JSON files, and the first-round frozen summary in an independently protected location.

The separate expert reference uses exactly:

    {"expert_reference_self_declared":true,
     "cases":[{"case_id":"anon-001","scores":[1,0.5,0]}]}

Every case must match the pre-registered pseudonymous case IDs and per-case rubric length; no missing/duplicate cases or source student text is accepted.

Run:

    python scripts/reviewer_pilot.py --manifest PRIVATE_MANIFEST.json --frozen FROZEN_ROUND.json --review-a REVIEWER_A.json --review-b REVIEWER_B.json --expert EXPERT_REFERENCE.json --output AGGREGATE_ONLY.json --bootstraps 200

The tool checks that each first-round packet's SHA256 matches the frozen record. It does **not** establish the frozen record's own authenticity if an authorized file owner modified it along with the packets; retain an independently controlled archival copy or signature. Output is a new file only, never an overwrite.

## Aggregate measures
- Reviewer A/B agreement and mean absolute score difference relative to the supplied expert-reference rubric.
- Reviewer-to-reviewer exact agreement.
- Fraction of agreed-on rubric criteria also matching the expert reference.
- Count of criteria where both reviewers agree with one another but disagree with the expert reference (a direct warning against equating consensus with correctness).
- Case-cluster bootstrap 95% interval for A minus B reference agreement.

These are **reference agreement measures, not independently established grading accuracy**. Expert ratings may also be wrong. Human permissions, reviewer qualification, actual blind independence and educational effectiveness cannot be inferred from self-declared metadata or synthetic examples. Raw answers, case IDs, individual scores and personal identifiers are not exported.
