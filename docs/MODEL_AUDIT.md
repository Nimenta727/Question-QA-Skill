# v1.1.0 strict model-based audit for questions

Every question should undergo independent solving, adversarial answer criticism and source/scope verification before presentation. The required nine checks are source_scope, independent_solution, answer_and_equivalents, ambiguity_and_conditions, options_or_rubric, diagnostic_value, cognitive_alignment, fairness_and_accessibility and novelty. A failed, uncertain, missing or unjustified check blocks the item; all three wrong choices (or every rubric criterion) must be assessed separately.

The reviewing model must first solve without seeing the author's proposed answer, then compare the key and seek counterexamples, hidden assumptions, multiple correct answers, invalid source claims, misleading distractors and superficial repeated variants.

Optional offline evidence-packet gate:

    python3 scripts/model_audit.py BANK.json --template audit.json --source-file COURSE.txt --author-id author-agent
    python3 scripts/model_audit.py BANK.json --review audit.json --source-file COURSE.txt --require-course
    python3 scripts/qa.py next BANK.json --state .qa-state.json --require-model-audit --model-audit audit.json --audit-source-file COURSE.txt --require-course-audit

The first command creates an unapproved template; a real separate model review must fill it. The verifier checks bank/source hashes, quotation presence, evidence completeness, selected objective answer agreement and unresolved issues. The script does not itself invoke an LLM or prove correctness, reviewer identity, or actual independent work. A review can be marked complete for informal practice but not certified for official high-stakes examination without independent qualified human verification.

If the course is unavailable, questions may be explicitly labeled as general practice rather than falsely attributed to real lesson material. Read references/model_audit.md for the full two-stage protocol.
