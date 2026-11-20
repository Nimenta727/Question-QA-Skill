# Diagnosis v0.2 / 深度学习诊断

The offline module makes **formative, interpretable judgments**. It does NOT perform statistically calibrated psychometrics.

## Core data / 记录与证据
- One event per answered question: item ID, family, concept, cognitive level, difficulty, response type, normalized score, session ID, confidence/hint flag, timestamp and optional reviewed misconception code. Do not store original learner response.
- Same item family and UTC day: only the most recent event contributes to evidence index; repeating a question/variant does not multiply evidence. Different-day repetition contributes at a sharply reduced weight.
- Observed evidence is separated by concept and by cognitive level. Reports also include untested concepts if a bank is provided.
- Correct answers marked guess/unsure or hint-used receive reduced positive evidential weight; they are not relabeled as wrong.
- Misconceptions are only assigned from reviewed wrong-option mappings or explicit reviewer labels; never inferred from the fact of being wrong alone.

## Heuristic interpretation / 暂定诊断
Outputs: rate (smoothed descriptive performance index), count (raw events), unique_items, families, days, levels, effective_evidence (weighted diagnostic exposure), flags and gaps. rate is NOT the probability the student masters the concept.

Status interpretation:
- untested: no observation;
- insufficient_evidence: fewer than three family/day observations or fewer than two distinct item families;
- needs_review: weak observed index with at least three observations and two families;
- developing: evidence exists but is not yet sufficiently broad, retained or consistently strong;
- tentatively_strong: requires 4 family/day observations, 3 distinct item families, 2 UTC dates, 2 cognitive levels, at least one correct unassisted higher-order item (apply/analyze/transfer), effective evidence >= 2.2, rate >= 0.72 and no latest hard miss.

These cutoffs are transparent **engineering assumptions**, not validated clinical, educational placement or official exam cut scores. Crossing UTC midnight does not prove durable learning; use reasonably spaced actual revisits.

## Adaptive item targeting / 选下一题
1. New session starts broad, unless a named focus concept is supplied.
2. Wrong answer => a distinct question on the same skill or its explicitly mapped prerequisite; favor approachable difficulty.
3. Correct but guessed/unsure/hinted => another format or independent item family on the same concept.
4. Confident correct => higher-order transfer or uncovered concept.
5. Between candidates, reward untested concepts/levels and unresolved transfer evidence; reduce exposure of seen families and recently asked items.
6. Never repeat the same item in one session. Stop at budget or item exhaustion, stating which.
This is **heuristic routing**, NOT calibrated CAT information gain, BKT or IRT.

## Commands / CLI
~~~bash
python3 scripts/qa.py validate examples/sample_bank.json
python3 scripts/qa.py start examples/sample_bank.json --mode quick --limit 6 --focus linear-equations
python3 scripts/qa.py next examples/sample_bank.json
python3 scripts/qa.py answer examples/sample_bank.json --response C --confidence guess
python3 scripts/qa.py report --bank examples/sample_bank.json
~~~

The default state file is .qa-state.json. start explicitly begins a new session but retains prior history. If a question is pending, the command requires --discard-pending; the pending item is not silently dropped. Use a distinct --state file per student and do not commit local state to Git.

## Extending item banks / 题库扩展
- family: stable, nonempty string for near-duplicate items; default item ID.
- prerequisites: list of known concept IDs (not the item ID), excluding itself.
- misconceptions: option-code -> reviewed error label for incorrect single-choice options only.
These optional fields are backward compatible with the v1 schema.

## Accuracy roadmap / 下一阶段
For genuine predictive improvement evaluate held-out future response prediction, false-high-confidence decisions, delayed retention, item quality, demographic fairness where appropriate and consented, and scoring consistency. Only add model-based BKT/IRT or FSRS with suitable historical data and validation. Do not market a heuristic score as a calibrated probability.
