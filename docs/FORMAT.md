# Question bank / 题库格式 v1

UTF-8 JSON, one file per unit or subject (examples/sample_bank.json). Generate with an assistant, validate locally. The CLI DOES NOT make model calls or invent questions: its role is deterministic selection, grading, and recordkeeping.

Bank root: version (integer 1), subject (nonempty string), items (nonempty array).
Per item required: id (globally unique within a bank), concept (stable knowledge-point ID), level (recall/understand/apply/analyze/transfer), difficulty (1/2/3), type (single/short/manual), stem, claim, evidence, explanation, source (nonempty strings).
- single: options array of four distinct, nonempty strings and answer A/B/C/D.
- short: answer string and optional aliases string array. Only exact normalized matches are scored. Semantic equivalence must be added explicitly as an alias.
- manual: rubric array of nonempty criteria; result is entered by instructor/AI *after* rubric evaluation (score 0/0.5/1 plus reason).

The "claim" expresses intended mastery and "evidence" describes what the response demonstrates; "source" is a source anchor. Use traceable identifiers e.g. lesson-03:p12 or original-example:topic; DO NOT forge references. The answer and explanation are never returned by the 'next' command.

Limitations:
- The current CLI does not independently verify generated claims, ambiguous wording, multi-correct answers, or pedagogical fairness. The authoring audit is mandatory.
- The state file is bound to a byte-for-byte SHA-256 bank digest for the pending question. Changing a bank while pending requires restoring the original or running reset-pending (discard that unanswered prompt, without credit).
- State reports cover answered concept × level only; absence from a report means untested, not "mastered".
- Use separate state files per learner. Store no names or raw response text; keep state private and out of Git.
- Concurrent writes to one state path are not supported; use serialized sessions.
