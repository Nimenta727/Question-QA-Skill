# Question-QA-Skill v1.1.0 — Model Question Audit / 模型逐题严格审查

Question correctness is the first gate for reliable adaptive tutoring. This release requires an independent-solution and adversarial-review step before the Skill presents newly generated or edited questions.

## Implemented
- Structured reviewing-model protocol: independently solve without author's key; then explicitly challenge the answer, alternatives, domain assumptions, curriculum/source alignment, three distractors OR all rubric criteria, cognitive level, diagnostic value, fairness and novelty.
- Offline no-dependency scripts/model_audit.py creates an **all-unapproved** model-review template; verifies exact bank/source SHA256, matching course quotes, recorded independent reviewer declaration, substantive reasons for all nine checks, correct selected objective answers, complete option/rubric analysis, static warning acknowledgment and no unresolved risks. Any fail/uncertain/missing evidence blocks the review.
- Optional enforced qa.py next gate: --require-model-audit --model-audit FILE [--audit-source-file COURSE.txt] [--require-course-audit]. No student-facing question is returned if a review is absent, stale or blocked. Existing calls remain backward compatible but explicitly marked not_checked_legacy_mode.
- A discovered alternative short answer that actual grading would reject must be added to the bank and re-audited. Course claims without supplied source cannot be laundered into generic practice; a model cannot label fabricated text as a verified teacher citation.
- Two-stage model review instructions now part of short core SKILL.md and references/model_audit.md, with bilingual guides and a concrete demo-bank self-critique that identifies diagnostic weaknesses rather than pretending everything passes.
- Synthetic adversarial tests on Linux/macOS/Windows, Python 3.9/3.12 and deterministic immutable SHA256 ZIP release checks. No private student answers, model review packets or course extracts are bundled.

## Limits
The Python code **does not itself call an LLM**; the Agent must actually perform the independent solve and review. Automated verification of a JSON packet is not proof of model semantic accuracy, trustworthy attribution, true identity separation or classroom learning impact. The self-audited demo bank is NOT certified by an independent AI or educator. Qualified human review remains required for official and high-stakes exams; previous evidence-index effectiveness claims are unchanged.
