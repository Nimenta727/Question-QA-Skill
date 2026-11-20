# QUICK 快问快答诊断协议

## Default six-probe loop
- Q1 baseline concept or prerequisite; Q2 neighboring core concept; Q3–Q4 apply and distinguish; Q5 counterexample/transfer; Q6 confirm the weakest *different* subskill.
- This is a template, not a fixed sequence: adaptive branching may override it.
- One prompt per exchange. Wait for the learner; no answer or marked choice is shown before the response.
- Choose a brief free-response when objective recall matters; use choice questions when distinguishing misconceptions.
- Confidence labels: sure / unsure / guess / none. Avoid forced self-disclosure or high-pressure timers.

## Branching and evidence
After an answer, tag: concept, cognitive level, source, task variant, score {0, 0.5, 1}, confidence, brief error category.
- Correct + sound explanation => ask a higher-level transfer or sample an untested concept.
- Correct + guessed/uncertain => ask a *different representation* of the same skill before claiming mastery.
- Wrong => test the nearest prerequisite or a contrast (not another near-identical prompt).
- Ambiguous response => clarify before attributing a misconception.
- Stop at the learner's request; or after default 6, providing a concise provisional profile.

A single right or wrong answer is weak evidence. Offline estimate accounts for independent item families (not merely IDs), distinct UTC dates, multiple cognitive levels, guessing and hint-assisted responses. Tentatively strong is withheld without delayed, higher-order and independent evidence. See docs/DIAGNOSIS.md. Results are formative and should state untested areas, rather than reporting universal ability.

## Output template
During session:
Question 3/6 — [one self-contained question].
After response: [correct/partial/needs review] — [one precise reason]. Next: [one question].
Closing: [tested topics + evidence counts]; [provisional strengths and uncertain/weak areas]; [one prioritized review action]; [suggested spaced follow-up]. No verbose transcript.

## Minimal state to persist
Persist only IDs, item families, scores, concept/level, confidence, hint use, misconception code and timestamps locally (scripts/qa.py); NEVER log identifiable student details or raw free-text answers by default. If no storage is available, keep a 1–2 line state summary in conversation, never promise cross-chat persistence.

## Limitations
Response time, confidence, speed and choice distractors can inform a follow-up, but alone do not measure comprehension. Offline scorer has exact-match short answers; semantically equivalent alternatives require explicit aliases or rubric review.
