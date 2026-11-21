# Strict question review — current v1.2.0

[Quick authoring rules](../references/authoring.md) · [Review instructions](../references/model_audit.md) · [Evidence validation plan](QUALITY_VALIDATION.md)

Every **new or modified** learner-facing item should undergo independent solving and adversarial criticism **before it is shown**. The protocol also applies to adaptive follow-ups. No result is “independently audited” unless an actual separate reviewing run took place.

## Two-stage review

1. **Blind independent solve:** reviewer sees the real prompt, options and permitted course source but **not** the author's answer or rubric. Independently solve; identify equivalent answers, missing restrictions, source mismatches, counterexamples and doubts. Preserve this stage's evidence before revealing the proposed key.
2. **Adversarial comparison:** compare with the author's key and grade criteria; challenge every option or rubric criterion, verify scope/quotes and document concrete reasons. After any edit, repeat the full review rather than reusing a stale approval.

All nine checks require specific evidence: `source_scope`, `independent_solution`, `answer_and_equivalents`, `ambiguity_and_conditions`, `options_or_rubric`, `diagnostic_value`, `cognitive_alignment`, `fairness_and_accessibility` and `novelty`. **Fail, uncertain, missing justification, unverified source or unresolved risk => withhold and repair.**

## Full-only offline gate (does not run an LLM)

~~~bash
python scripts/model_audit.py BANK.json --template audit.json --source-file COURSE.txt --author-id author-agent
# A genuinely separate reviewer must fill the template after blind solving.
python scripts/model_audit.py BANK.json --review audit.json --source-file COURSE.txt --require-course
python scripts/qa.py next BANK.json --state .qa-state.json --require-model-audit --model-audit audit.json --audit-source-file COURSE.txt --require-course-audit
~~~

`COURSE.txt` is a permitted, actually verified UTF-8 excerpt with traceable source locations. The code binds bank/source SHA256, checks supplied quote presence, expected record completeness, limited objective answer agreement and unresolved issues. A changed bank or source invalidates the existing record. With no accessible course source, label it `general_practice`, not “teacher-aligned.”

**Boundaries:** hashes authenticate bytes, not citations' meaning. Author/reviewer IDs are self-declared and do not certify distinct identities or independent reasoning. A syntactically complete audit JSON can still contain incorrect reasoning. An LLM self-review must be disclosed as self-review; official or high-stakes assessments require qualified independent human review.
