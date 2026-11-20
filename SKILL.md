---
name: question-qa-skill
description: Design source-grounded, original, rigorous and fair questions; run adaptive one-at-a-time quick oral/written checks; diagnose knowledge and plan spaced reviews with verifiable evidence. Use for quizzes, exam generation, learning diagnostics and follow-up practice.
license: MIT
compatibility: Any Agent Skills-compatible assistant; Python 3.9+ optional for local state and deterministic grading.
metadata:
  version: "0.8.0"
  languages: "zh-CN,en"
---

# Question-QA-Skill

Purpose: generate deep but fair questions, then diagnose learning through *evidence*, not impression. Default to Chinese when the learner writes in Chinese. Preserve the instructor's scope and definitions; never invent what a teacher taught.

## 1. Route, and load only what is needed
- "出题/模拟卷/深度练习" => DEEP mode; read references/authoring.md once.
- "快问快答/测测掌握/抽查" => QUICK mode; read references/diagnosis.md once.
- A specified discipline => read ONLY the matching portion of references/subjects.md.
- "继续/复习/追踪" => read compact report via scripts/qa.py if state and bank exist; otherwise ask for the prior record or begin a new baseline.
- "可视化/学习报告/知识图谱" => generate offline HTML via scripts/dashboard.py; do not embed student answers or answer keys.
- "评估学生回答/批改开放题" => use a reviewed per-criterion rubric and structured evidence; read docs/INSTALL.zh-CN.md or docs/INSTALL.md for the assessor format.
- For a course file or named teacher's material, analyze available source first. If inaccessible, label as general-knowledge questions and do not impersonate that source.
- No source material? Ask at most one essential question about subject; if subject is known, begin with a defensible general-level baseline.
- Do not preload all references. Do not generate extra examples until requested.

## 2. Modes
### QUICK — default 6 prompts, one per turn
1. Establish the knowledge claims and breadth; start with a short, straightforward diagnostic probe.
2. Ask exactly ONE question; wait for the learner's answer. Never expose the answer/rubric in the prompt.
3. Prefer short recall, discrimination between close concepts, one-step application and reasoned "why"; multiple-choice only when it adds diagnostic value. Avoid trivia and trick wording.
4. After response: judge against an explicit key/rubric; report brief result + precise misconception ONLY when supported by the selected distractor or reviewed rubric, otherwise say uncertain. If ambiguous, ask a targeted follow-up before scoring.
5. Ask confidence (sure/unsure/guess) optionally, not on every turn. Use confidence and response time only as soft context, never as proof of mastery.
6. Adapt: if wrong, test a different item family on the prerequisite/contrast; if guessed correct, confirm via a different item type; if confidently correct, test transfer or uncovered concepts. Stop at 6 by default, or earlier if the learner chooses.
7. End with coverage, evidence count, current strengths, untested areas, next 2–3 recommended probes, and suggested review dates. Never equate one correct response or repeated same-day exposure with mastery; check different cognitive levels and delayed retrieval.

### DEEP — default 5 questions
1. Map objectives and key concepts from source; balance core coverage.
2. Design ECD trio: target CLAIM -> observable EVIDENCE -> TASK for each question.
3. Mix mechanisms, derivations, error detection, boundary cases, transfer and synthesis. Novelty comes from authentic contexts and meaningful reasoning, NEVER obscure trivia.
4. State conditions, units, assumptions, expected answer form, scoring rubric, source anchors and difficulty justification.
5. Verify every answer independently, check distractor plausibility, ambiguity, accessibility, neutrality, instruction alignment and all alternative valid answers.
6. Deliver student paper first and answer/explanation as a separate, clearly marked section ONLY when requested, or after submission for interactive practice.
7. If current claims require verification, retrieve reliable material, cite dated sources and mark uncertain facts. Do not fabricate official examination questions.

## 3. Evidence integrity
- Evidence precedence: user-provided lesson > verified curriculum/primary source > reliable secondary source > clearly labeled model-generated practice.
- Source anchors must identify the section/line/page when available. Do not claim verified provenance without inspection.
- Neutrality: never assume a political, cultural or personal view as the only correct one on disputed subjects; frame questions around attributable evidence and explicit criteria.
- Coverage and depth are separate axes. Avoid rewarding linguistic fluency when testing math/science reasoning.
- For open responses, score only against a published rubric; when equivalence or correctness is unclear, return "needs review", do not silently score zero.
- An estimated mastery indicator is **formative** and not a calibrated test score.
- Open-answer assessment must cite concrete reasoning evidence for each rubric criterion and provide feedback specific to incomplete criteria. Use human or careful AI review; local code validates the rubric data but does not semantically evaluate student text.
- For equivalent short answers not explicitly listed in aliases, allow a reviewer-documented equivalence override only after an independent check; objective multiple-choice keys are never overridable.

## 4. Optional executable local workflow
Use python3 scripts/qa.py (Python 3.9+, no dependencies):
- validate BANK.json
- start BANK.json --state .qa-state.json --mode quick --limit 6 --focus concept-id (focus optional)
- next BANK.json --state .qa-state.json --mode quick
- answer BANK.json --state .qa-state.json --response "B" --confidence sure --hint-used (hint flag optional)
- answer BANK.json --state .qa-state.json --response "..." --score 0.5 --reason "rubric-based evaluation" (manual/open responses only)
- report --state .qa-state.json --bank BANK.json
- answer BANK.json --state .qa-state.json --response "..." --reason "reviewed each criterion" --rubric-judgments @review.json (manual items)
- answer BANK.json --state .qa-state.json --response "equivalent representation" --review-equivalent --reason "verified equivalence" (short-only)
- dashboard via python3 scripts/dashboard.py BANK.json --state .qa-state.json --output learning-dashboard.html

Write bank format per examples/sample_bank.json and docs/FORMAT.md. For interpretation gates read docs/DIAGNOSIS.md only when needed. Never show the bank JSON to a learner before answering; it contains keys. State is LOCAL and untracked.

## 5. Token budget
- For each QUICK turn: question only (typically under 80 Chinese characters unless reasoning needs data); after answer, 1-line verdict + 1-line reason + next single question.
- Persist compact records of item families, cognitive levels, time, optional hint/confidence and misconception code; on continuation read the report, not entire dialogue.
- Deterministically validate, select, mark objective answers and aggregate stats in Python; spend LLM reasoning on authoring, source checking and nuanced open responses only.
- Reuse validated items until exposed, then generate fresh *variants* of the same concept rather than repeating the same stem.
- Avoid multi-agent orchestration for a six-question quiz. Never echo source files or large rulesets into the learner-facing output.

## 6. Completion gate
Before releasing a question bank check source fidelity; claim/evidence alignment; objective, independent solutions; alternate correct answers; plausible distractors; balanced difficulty; fairness; no leakage; concise feedback; evidence uncertainty. Run python3 -m unittest discover -s tests -v for code changes.

## 7. Evidence and validation gate (load only when needed)
If asked whether the diagnosis is accurate, inspect docs/VALIDATION.md (or docs/VALIDATION.zh-CN.md). The current formative index has **not** shown robust predictive improvement over historical quiz means on the external FORGET-SE exam benchmark. Never describe `rate` as calibrated mastery probability, call a provisional label a standardized test result, or infer adaptive item-choice causal benefits from observational data. Do not add BKT/IRT to the default loop until sufficient held-out calibration data and evidence exist. For offline evaluation use scripts/evaluate.py or scripts/evaluate_forget_se.py; never commit raw learner records.

## 8. Official offline distribution
Release v0.4.0 includes an offline bilingual dashboard, criterion-based student feedback and SHA256-manifest-verified ZIP. Read docs/INSTALL.zh-CN.md or docs/INSTALL.md for installation and privacy notes, docs/RELEASE.md for reproducibility, and CHANGELOG.md for version changes. Only release files allowlisted by scripts/build_release.py. Never embed student raw responses in the dashboard, demos or release.


## 9. Independent item-quality review / 命题质量门槛
Before releasing a newly generated question bank, use python3 scripts/qa.py validate BANK.json followed by python3 scripts/question_quality.py BANK.json. Arithmetic witnesses (when available) check only explicit numeric consistency, not proof of curriculum or fairness. For an independently reviewed bank, generate an all-false review template with --review-template FILE, have the reviewer attest to source, answer, scope, ambiguity, fairness and rubric, then run --review FILE --strict. Do not have the authoring model self-certify every box. Read docs/QUESTION_QUALITY.zh-CN.md or docs/QUESTION_QUALITY.md only when authoring/auditing.

External validation has now been replicated on the independent ASSISTments2015 mathematics practice cohort (docs/VALIDATION_ASSIST2015.md), with no proven index advantage over a simple learner-history baseline. The previous FORGET-SE result remains separate (different prediction task). Never imply item-family/day/cognitive-level data exist when absent. BKT/IRT not yet released.


## 10. v0.6.0 formative, reviewer and release workflows
For student free-form answers, an independently arranged two-reviewer assessment may be supplied to qa.py answer through --independent-reviews @reviews.json. Each reviewer must anchor each rubric judgment in the student's actual answer, with evidence, feedback and a declared independent identity. When the two reviewers disagree, require a distinct adjudicator using --adjudication @decisions.json before scoring. Prefer --response-file PRIVATE.txt over raw answers in command arguments. Details: docs/ASSESSMENT.zh-CN.md or docs/ASSESSMENT.md. The local CLI does NOT call LLMs or independently verify semantic correctness, nor does it cryptographically prove reviewers' independence.

Use separate evidence_engine.py, prediction_engine.py and adaptive_engine.py: a descriptive evidence sufficiency index is not a calibrated probability; the historical-score baseline is uncalibrated and distinct; selecting the next question returns an explanatory rule-code, not a proven causal benefit. See docs/ARCHITECTURE.md. Versioned ZIPs are published once per fixed Git tag, never silently replaced.


## 11. v0.7.0 safe math, state and reviewer study
For explicitly numeric/polynomial short answers, the bank may opt into restricted exact math equivalence with answer_equivalence; never enable this on choice/manual questions, and never run arbitrary student Python source. Unsupported syntax should preserve the pending answer for independent review. Consult docs/MATH_EQUIVALENCE.zh-CN.md / .md when authoring numerical items.

State transactions now require OS-native exclusive locks and save a last-good previous committed state as STATE.bak. Use qa.py state-check and state-recover --confirm only with understanding that the newest action may be rolled back; never publish private state or backups. Consult docs/STATE_SAFETY.zh-CN.md / .md.

A separate aggregate-only reviewer study tool measures rubric-score agreement and weighted kappa, not correctness. Genuine independent reviewers, opt-in/permissions and separate expert criterion validation are required before claiming real study results. See docs/REVIEWER_STUDY.zh-CN.md / .md.


## 12. v0.8.0 appeals, private lifecycle and permission-gated review research
Each new completed response carries a stable event_id. A student may request correction with qa.py appeal-open, and an actual independent reviewer should verify the original answer before appeal-resolve --reviewer-confirmed is declared. Corrected rubric scores must agree with the published criteria, and original grade plus corrected grade remain in reason-coded audit metadata without student raw text. See docs/APPEALS.zh-CN.md / docs/APPEALS.md.

Local state retains up to five prior valid snapshots plus the previous .bak. Explicit snapshot recovery, aggregate/private export and local managed-file deletion are available; private export and deletion require confirmation. Deletion does not securely erase remote or historical copies. See docs/DATA_LIFECYCLE.zh-CN.md / docs/DATA_LIFECYCLE.md.

A pseudonymous two-reviewer study preparation tool can split randomized A/B task lists and freeze completed first-round rating packets, but real reviewer independence, educational authorization and consent must be verified externally. No human-subject study was performed. See docs/REVIEW_TRIAL.zh-CN.md / docs/REVIEW_TRIAL.md.


## 13. v0.9.0 — locally authenticated correction and HMAC evidence
For high-trust local grading correction, enroll reviewer capabilities using scripts/reviewer_credentials.py and enable audit protection in qa.py **before opening any appeals**. A protected appeal must be opened with --audit-key-file and closed only by an active enrolled --reviewer-id/--reviewer-token-file plus a matching --registry and --audit-key-file; --reviewer-confirmed alone is NEVER sufficient on protected state.

Use qa.py audit-verify to verify HMAC links and the externally authenticated .audit-policy marker. Retain independently stored audit-checkpoint receipts to detect replacement by older, valid signed state; the key is never included in learning state or release assets. Reviewer credentials authenticate local secret possession, NOT actual educator identity; controlled storage and external institutional verification are mandatory. Read docs/SECURITY_AUDIT.zh-CN.md or docs/SECURITY_AUDIT.md when using protected appeals.

The private reviewer_trial.py workflow can finalize C decisions only after frozen A/B scores match their original hashes and all disputed rubric criteria are adjudicated. This is NOT proof of genuine independent human participation or consent. Research oversight remains external. See docs/REVIEW_TRIAL.zh-CN.md.
