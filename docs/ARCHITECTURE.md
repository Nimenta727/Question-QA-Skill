# Architecture overview — current v1.2.0 structure

## A slim Agent interface, not a platform boot sequence
The normal tutor loads just \`SKILL.md\`. QUICK optionally reads \`references/tutoring.md\`, DEEP reads \`references/authoring.md\`, complicated audit issues read \`references/model_audit.md\`, and subject-specific edge cases consult the corresponding part of \`references/subjects.md\`. These are **progressive disclosures**, not mandatory simultaneous context. A core Skill is fully usable in conversation without any Python or model API infrastructure.

## Release profiles
- **Core:** short prompt, four references, minimal README/LICENSE/VERSION and SHA256 manifest (no scripts, tests, documents, student information).
- **Full:** exact same prompt/references plus existing offline source, examples, tests, bilingual documentation, archives and dated engineering records; \`qa.py\` grading and \`model_audit.py\` source/checksum evidence verification are optional tool calls, not hidden model capabilities.
- User-provided course data is read only when needed, never invented or used as instructions. Neither package stores a long chat history or uses model billing APIs on its own.

## Verification boundaries
Software regression demonstrates API stability, reproducible packaging and selected fail-closed review gates, NOT calibrated student mastery, pedagogical effectiveness or independent correctness of model-authored explanations. Research and reviewer-administration features remain available only in Full and do not affect normal student context.

---
# v0.6.0 modular diagnostic architecture

Three separate concerns are now exposed by the CLI while preserving the previously tested v0.2 algorithm:

1. scripts/evidence_engine.py reports observed independent families, UTC dates, cognitive levels, error flags, evidence gaps and a legacy descriptive index. It is evidence about observed responses, not a forecast and NOT a mastery probability.
2. scripts/prediction_engine.py computes a fixed smoothed historical-score baseline with two pseudo-counts at prior 0.5. It is an interpretable comparison signal, not fitted, calibrated or independently validated individual probability.
3. scripts/adaptive_engine.py continues to use the unchanged diagnosis.select_item policy, adding reason codes for knowledge coverage, uncertain answers, mistake repair and item-family diversity. These reason codes describe broad factors, not exact computed priority contributions or causal learning benefits.

The qa.py report and answer output keep legacy rate/status fields for compatibility and also return evidence_profile and prediction_baseline. The qa.py next command returns a cached selection explanation for the active pending question, without exposing the correct answer or rubric before submission.

FORGET-SE external exam and ASSISTments2015 practice prediction studies did not establish index improvement over simple history baselines. We have not tuned the original model on these two used test sets. Reliable evaluation of strong mastery labels still requires real item identities, independent and delayed recalls, expert-reviewed cognitive annotations, and genuinely unseen target assessments. Adaptive benefits require a separate prospective controlled comparison.


## v0.7.0 additions
math_equivalence.py is a limited deterministic equivalence helper, not an adaptive learner model; old diagnosis weights are unmodified. state_store.py provides native filesystem transactional locks and previous committed backups under CLI, but external file editors and networked filesystems are out of scope. reviewer_study.py is a separate aggregate score-agreement utility, not an automatic semantic grading system; its real participant status is unverified.


## v0.8.0 revision, retention and study boundaries
appeals.py stores minimal reason-coded before/after corrections and updates effective response scores for diagnosis, score-history comparison, adaptive questions and the local dashboard. This is not an authenticated teacher approval or cryptographically protected ledger. state_store.py supports at most five valid prior snapshots and ordinary controlled export/deletion; external file copies remain outside its remit. reviewer_trial.py produces randomized pseudonymous tasks for two independent reviewers and freezes first-round aggregate score statistics, but cannot establish real authorization, blindness or educational effectiveness.


## v1.0.0 pedagogical orchestration — thin and optional
scripts/tutor_core.py sits above the existing offline diagnosis, selector, rubric review and privacy-sensitive state layer. It reads only already-recorded response metadata (score, family, concept, level, confidence, hint and source-reviewed item metadata) and emits a compact instructional plan for the AI. It does not call external APIs, read student original text, author unverified answers, retrain a prediction model, override grading or require the audit platform.

The human-facing pipeline is: course scope → one diagnostic claim/task → student response → justified grade or requested clarification → targeted independent follow-up → cautious session summary. The old v0.2 index and previous validation experiments are preserved unchanged. Security and authentication mechanisms remain independently available via references/operations.md but are not a prerequisite for ordinary tutoring.


## v1.1.0 author-review separation before item release
The Agent must first solve each authored item independently without relying on the proposed key, then use a genuine reviewing model pass to seek counterexamples, source mismatches, alternative answers, misleading distractors/rubric errors and low diagnostic value. scripts/model_audit.py enforces an evidence record with a source/bank digest and fail-closed structure; it does not run the review model. qa.py next can enforce the gate for local banks, while Skill instructions require serious internal model critique even when local CLI is unavailable. Previous offline grading and tutoring evidence functions remain unchanged. For official/high-stakes examinations, external human review remains mandatory.
