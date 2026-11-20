---
name: question-qa-skill
description: Design source-grounded, original, rigorous and fair questions; run adaptive one-at-a-time quick oral/written checks; diagnose knowledge and plan spaced reviews with verifiable evidence. Use for quizzes, exam generation, learning diagnostics and follow-up practice.
license: MIT
compatibility: Any Agent Skills-compatible assistant; Python 3.9+ optional for local state and deterministic grading.
metadata:
  version: "0.1.0"
  languages: "zh-CN,en"
---

# Question-QA-Skill

Purpose: generate deep but fair questions, then diagnose learning through *evidence*, not impression. Default to Chinese when the learner writes in Chinese. Preserve the instructor's scope and definitions; never invent what a teacher taught.

## 1. Route, and load only what is needed
- "出题/模拟卷/深度练习" => DEEP mode; read references/authoring.md once.
- "快问快答/测测掌握/抽查" => QUICK mode; read references/diagnosis.md once.
- A specified discipline => read ONLY the matching portion of references/subjects.md.
- "继续/复习/追踪" => read compact report via scripts/qa.py if state and bank exist; otherwise ask for the prior record or begin a new baseline.
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

## 4. Optional executable local workflow
Use python3 scripts/qa.py (Python 3.9+, no dependencies):
- validate BANK.json
- start BANK.json --state .qa-state.json --mode quick --limit 6 --focus concept-id (focus optional)
- next BANK.json --state .qa-state.json --mode quick
- answer BANK.json --state .qa-state.json --response "B" --confidence sure --hint-used (hint flag optional)
- answer BANK.json --state .qa-state.json --response "..." --score 0.5 --reason "rubric-based evaluation" (manual/open responses only)
- report --state .qa-state.json --bank BANK.json

Write bank format per examples/sample_bank.json and docs/FORMAT.md. For interpretation gates read docs/DIAGNOSIS.md only when needed. Never show the bank JSON to a learner before answering; it contains keys. State is LOCAL and untracked.

## 5. Token budget
- For each QUICK turn: question only (typically under 80 Chinese characters unless reasoning needs data); after answer, 1-line verdict + 1-line reason + next single question.
- Persist compact records of item families, cognitive levels, time, optional hint/confidence and misconception code; on continuation read the report, not entire dialogue.
- Deterministically validate, select, mark objective answers and aggregate stats in Python; spend LLM reasoning on authoring, source checking and nuanced open responses only.
- Reuse validated items until exposed, then generate fresh *variants* of the same concept rather than repeating the same stem.
- Avoid multi-agent orchestration for a six-question quiz. Never echo source files or large rulesets into the learner-facing output.

## 6. Completion gate
Before releasing a question bank check source fidelity; claim/evidence alignment; objective, independent solutions; alternate correct answers; plausible distractors; balanced difficulty; fairness; no leakage; concise feedback; evidence uncertainty. Run python3 -m unittest discover -s tests -v for code changes.
