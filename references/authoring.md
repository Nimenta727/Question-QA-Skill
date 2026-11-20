# DEEP 命题协议 / Rigorous item authoring

## Define what is being measured
For every item write (internally): source anchor, target knowledge claim, observable evidence, required reasoning, cognitive level, difficulty 1–3, expected time, validated solution, distractor rationale, alternative correct answers.

Questions are "独到" when they illuminate a core mechanism, expose a subtle misconception or transfer a familiar idea into a genuinely new but fair setting. Novelty is NOT obscure facts, invented exam traditions, trick phrasing or impossible calculations.

## Draft sequence
1. Extract a source-faithful concept map and weight high-frequency/central concepts first.
2. Blueprint coverage: foundational recall 20%, conceptual understanding 20%, application 30%, analysis/transfer 30% (defaults; adapt to discipline, source and user).
3. Write clear premises and one explicit, testable objective. Solve independently *before* writing plausible alternatives.
4. Analyze a typical wrong approach and a compelling alternative explanation; make those distractors.
5. Produce a counterexample or boundary check where useful, but do not use a condition the course never taught without explaining it.
6. Add concise marking rubric: required claims, partial credit, acceptable equivalences.
7. Review bias: eliminate unnecessary language complexity, cultural assumptions, subjective preference and normative conclusions not supported by criteria.
8. Verify accuracy against source (and where appropriate trustworthy external materials); label independent extensions.

## Evaluation thresholds
- Accuracy: every option independently checked; multiple valid answers => change stem to clarify or accept all correct answers.
- Rigor: at least one nontrivial reasoning step for depth items; calculations must be solvable with supplied information.
- Fairness: no niche trivia unless explicitly in source; no hidden prerequisites; reasonable solve time; no misleading cues.
- Specificity: a question should diagnose *which* misconception, not only correct/incorrect.
- Attribution: never misrepresent generated practice as actual official past exam.
- Multi-perspective disciplines: grade quality of evidence, reasoning and distinctions, rather than politically or culturally prescribed positions.

## Answer packaging
For paper mode: output a coherent exam paper first (subject, scope, time, numbered items), and withhold keys until learner submits or explicitly asks. For interactive deep mode: one item at a time. Preserve all instructor content if source-focused.


## v0.5.0 offline quality checks and accountable review
For any bank to be issued to learners: run qa.py validate first, then question_quality.py BANK.json. If the item is a simple numeric objective question, optionally attach a bounded arithmetic witness and independently verify it corresponds to the actual question assumptions. Do NOT claim numeric consistency solves textual ambiguity or validates official curriculum provenance. Generate a blank SHA256-bound form using --review-template, have a distinct reviewer confirm answer/source/scope/ambiguity/fairness/rubric, then use --review FILE --strict to enforce that recorded review. Do not let the same authoring model self-certify. Refer to docs/QUESTION_QUALITY.md or .zh-CN.md when needed.


## v1.0.0 fair next-question variants
When an adaptive session requires a new question because no suitable reviewed item is available, treat the generated tutor_core new_item_authoring_brief as **instructions for a draft**, not a trusted answer key. Before presenting the question: (a) confirm its learning objective occurs in the actual course source, (b) avoid merely changing numbers in the same family, (c) solve independently and list valid equivalents and domain assumptions, (d) state one observable criterion that distinguishes understanding from guessing, and (e) check ambiguity, fairness and source anchor. Do not claim the draft has been independently reviewed without a distinct qualified reviewer.
