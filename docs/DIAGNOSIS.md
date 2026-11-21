# Formative diagnostic semantics — current v1.2.0

[Architecture](ARCHITECTURE.md) · [Research evidence](VALIDATION.md) · [Next evaluation](QUALITY_VALIDATION.md)

The Full toolkit records **observations and rule-based follow-up intentions**, not a calibrated psychological or educational estimate of mastery. The descriptive index is historically named “v0.2” in the implementation; this is an algorithm lineage, **not** the current package version.

## Evidence stored for an answered item

An event can include question ID, family, concept, cognitive level, difficulty, format, normalized score, session, self-reported confidence/hint use, time and reviewed error mapping. Original free-text student submissions are not required for the diagnostic index. Treat unreviewed alleged misconceptions as **unconfirmed alternatives**, not diagnoses.

The evidence heuristics limit repeated exposure: same item family on the same UTC date does not generate independent positive evidence, and later exposure contributes at reduced weight. Multiple dates, independent families and higher-level questions are considered, but simply crossing midnight does not demonstrate retention.

## Descriptive output, not probability

| Field / status | Interpretation |
| --- | --- |
| `rate` | Smoothed historical index; **not** P(mastered concept) |
| `count`, `families`, `days`, `levels` | Observed coverage dimensions; use to identify untested claims |
| `effective_evidence` | Heuristic weighting of observations, not sample size or confidence interval |
| `untested` / `insufficient_evidence` | No data or breadth too limited for even a tentative descriptive label |
| `needs_review` / `developing` | Follow-up may be useful; not a permanent label for the learner |
| `tentatively_strong` | Multiple families, dates and higher-order successes pass engineering rules; **not** verified long-term retention |

The historical tentative-strong gate requires at least four family/day observations, three distinct families, two UTC dates, two cognitive levels, an unassisted higher-order correct result, effective evidence ≥ 2.2, descriptive rate ≥ 0.72 and no latest severe miss. These are **engineering thresholds**, not validated official cut scores.

## How a question is selected

1. Start with the named focus or coverage gap; choose one reviewable claim and one safe question.
2. Wrong, unknown cause: clarify the reasoning or a relevant prerequisite; never label a specific misconception without supporting evidence.
3. Correct but guessed/unsure/hinted: use an **independent family or representation**, with no hint, to rule out chance/exposure.
4. Partial score: probe the critical missing rubric criterion; reliable explained success: probe a boundary, transfer or uncovered skill.
5. Avoid the same question again in a session, cap redundant exposure, honor early stop and report unknowns.

This is **heuristic routing**, not calibrated computerized adaptive testing, validated information gain, BKT or IRT. The conversational agent still has to inspect and interpret free-form reasoning separately; the Python scripts cannot independently do that.

## Full CLI example

~~~bash
python scripts/qa.py validate examples/sample_bank.json
python scripts/qa.py start examples/sample_bank.json --mode quick --limit 6 --focus linear-equations
python scripts/qa.py next examples/sample_bank.json
python scripts/qa.py answer examples/sample_bank.json --response C --confidence guess
python scripts/qa.py report --bank examples/sample_bank.json
~~~

Default local state is `.qa-state.json`; use separate files for separate learners and never commit them. `qa.py next` can expose an internal `tutor_intent`; `answer` returns `tutor_next_move`; `report` provides `teaching_summary`. These are **assistant planning metadata**, not proof of answer reasoning or student-facing scores. A strict model-review evidence gate is optional in Full; see [audit](MODEL_AUDIT.md).

## Scientific limitation

Held-out evaluation on FORGET-SE did not show an advantage of the historical index over simple score-history baselines; the separately evaluated ASSISTments2015 task also favored a simple baseline. The targets differ across datasets and cannot be compared as if identical. Missing reliable cognitive-level and revisit-time evidence prevents estimating the “tentatively strong” label's true false-positive rate. No causal learning gain, durable retention or calibrated proficiency has been established. [Validation](VALIDATION.md).
