# Question quality audit / v0.5.0

Question-QA-Skill separates verifiable software checks from **human-reviewed educational correctness**. Neither an error-free static audit nor a filled review form proves factual accuracy, no ambiguity, curriculum scope or fairness.

## Usage

    python3 scripts/qa.py validate examples/sample_bank.json
    python3 scripts/question_quality.py examples/sample_bank.json --output quality-audit.json

The item-ID-only output reports errors/warnings/info and the input SHA256 digest without printing keys, source questions or learner responses.

Automatic checks: duplicate normalized and near-duplicate longer stems; cross-concept family tags; repeated open-response criteria; short explanations and unusual source anchors. Legacy qa.py checks core JSON structure, types and option uniqueness.

Optional exact arithmetic witness for a numerical short answer or MCQ:

    "verification": {"kind": "arithmetic", "expression": "(19-4)/3"}

This runs constrained Python AST and Fraction arithmetic (integer/decimal literals; +,-,*,/) and compares the exact rational result to the marked numeric answer. It can detect another numerically equivalent MCQ option. It is not a general solution proof, symbolic solver, source fact-checker or guarantee of well-posedness; unsupported expressions fail safely.

## Independent review and publication gate

    python3 scripts/question_quality.py examples/sample_bank.json --review-template review.json

The generated JSON is bound to the SHA256 of the complete question-bank bytes. **Every approval is false by default.** An actual reviewer must check each question for answer correctness, traceable source, curriculum scope, absence of ambiguity, fairness and usable scoring criteria; enter a reviewer identity and any remaining limitations.

    python3 scripts/question_quality.py examples/sample_bank.json --review review.json --strict

Strict mode fails if any item lacks a completed review, the bank bytes changed, or any critical structural/mathematical contradiction is found. Warnings still require professional follow-up. Review entries are attestations, not tamper-proof digital signatures or independent mathematical proofs.

## Important limitations
- Near-duplicate flagging is heuristic, not semantic paraphrase detection.
- Only bounded rational arithmetic is deterministically evaluated, not symbolic mathematics or explanations.
- The reviewer identity and checks are not cryptographically verifiable; false sign-off remains possible.
- The checker is not a psychometric or inter-rater agreement study and cannot establish predictive diagnostic validity.

Recommended release pipeline: source-grounded draft, independent solution, static audit, professional item-by-item review, recorded strict gate, then student delivery. Keep the review manifest private when it reveals reviewer identity.
