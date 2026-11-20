# QUICK observed-evidence diagnosis (implementation notes)

The learner-facing default tutoring protocol is now references/tutoring.md. This file describes **only the local diagnostic interpretation rules**, not the complete AI teaching conversation.

- Each observation needs concept, independent item family, cognitive level, score, confidence (optional), hint flag, UTC date and concise **reviewed** misconception code if available.
- One correct response is not mastery; same-family repetitions or same-day practice do not establish retention. A verified higher-order or delayed response requires a genuinely distinct task and time gap, not an invented timestamp.
- Wrong answers without a reviewed reason must be flagged error_cause_unverified, not assigned a fictitious misconception. Guess/hint-assisted success needs an independent confirmation.
- The historical descriptive evidence index in scripts/diagnosis.py, separate history baseline in scripts/prediction_engine.py and adaptive selector in scripts/adaptive_engine.py remain unchanged for prior-study reproducibility; they are **not calibrated mastery probabilities**.
- scripts/tutor_core.py maps the most recent recorded response to a compact teaching instruction and checks whether the next selected item fits the desired independent probe. Its plan is advice to the AI, never itself a semantic judgment about student thinking.
- A completed session receives a bounded report: what was actually tested, which knowledge claims remain uncertain or untested, and one justified next retrieval task. Do not continue asking when the student stops.

See docs/DIAGNOSIS.md, docs/VALIDATION.md and docs/VALIDATION_ASSIST2015.md for scientific limitations.
