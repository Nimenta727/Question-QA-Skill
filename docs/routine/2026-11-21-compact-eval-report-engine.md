# 2026-11-21 — Compact post-run Skill evaluation report engine (phase 1)

## Actual changes
- Add the optional Full-only stdlib CLI `scripts/skill_eval_report.py` to render a **single-page, progressive-disclosure HTML report** from explicitly provided evaluation records. It **does not run an LLM** or fabricate results.
- Strict allowlisted, size-bounded input schema; reject unexpected fields (including raw student/question text), duplicate case IDs, inconsistent source/reference modes, invalid grader decisions and impossible metrics. Escape all displayed identifiers and use no network assets or JavaScript.
- Report 3 task-specific measures at most, explicit numerators/denominators and conditional Wilson intervals (only for >=5 distinct-family observations); no master-probability estimate. Show top failure cases and <=4 issue-category bars, with full details and observed token/latency metadata hidden behind native disclosure.
- Synthetic demo evidence is labeled clearly; actual model runs with only self-grading have metrics suppressed. Expert review is always described as **declared**, not independently authenticated.

## Verification and next steps
1. Add synthetic fixture, thorough parser/summary/HTML/escaping tests and usage docs in a second commit with its own routine record.
2. Integrate the optional report in Full distribution and release smoke tests without adding it to the compact Core package.
3. Confirm tests and diff in an independent PR; release a versioned artifact only after checks. Actual model/educator RM-01–RM-12 studies remain NOT RUN.

## Additional checks in clean branch
- Earlier v1.2.1 release correction was already resolved by independent PR #5; duplicate PR #6 was closed. The feature is replayed cleanly from released main without merging the obsolete fix branch.
- Escaped literal CSS percent signs in Python %-formatted HTML templates and suppressed failure-case interpretations without independent reference labels.
