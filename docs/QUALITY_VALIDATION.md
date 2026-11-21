# Question quality and diagnosis validation — proposed next phase

**Status: protocol only; no independent model/educator pilot or learner-outcome results have been completed under this plan.**

[Roadmap](ROADMAP.md) · [Model audit](MODEL_AUDIT.md) · [Existing limitations](VALIDATION.md)

## Objectives and study units

Separate three questions: (A) Are questions factually correct and genuinely source-aligned? (B) Does the reviewer detect meaningful item defects? (C) Does an adaptive follow-up yield more reliable, non-overclaimed evidence than a comparable fixed sequence?

- Use **permissioned** course extracts; store chapter/page locator, intended claim, prerequisites, cognitive demand, and an independently checked solution. Without authorized material, use clearly labeled generic tasks.
- Maintain **independent item families**, not minor number swaps. Split pilot/tuning material from final blind evaluation by course/concept/family and, where applicable, learner.
- Build an expert-checked balanced defect set: wrong key, second correct answer/equivalent solution, missing premise, fake or unverifiable course quote, defective distractor/rubric, misleading cognition label, unfair or near-duplicate item, plus genuinely sound controls.
- Record source version, item hash, model/provider/version, prompts and reviewing context, time, whether the review was blind, and a human adjudication of reviewer disagreements. Do not publish private course text or learner data.

## Outcomes to compute (with denominators, not just examples)

| Component | Metric | Important failure signal |
| --- | --- | --- |
| Item correctness | sound items / items checked, with defect categories | Key wrong, multi-key item, unsupported quote |
| Audit sensitivity | caught defective / independently labeled defective | False negative: a bad item was accepted |
| Audit specificity | accepted sound / independently labeled sound | False positive: a sound item was blocked |
| Source traceability | exact and authorized claims / checked claims | Invented citation, source version mismatch |
| Adaptive diagnosis | independent follow-up matching documented missing evidence / cases | Guess treated as mastery, wrong answer treated as proved misconception |
| Fairness / clarity | independent rater scores and disagreement | Overly inferential or inaccessible grading |
| Efficiency | actual input/output tokens, model calls and latency per eligible episode | Savings only asserted from prompt size or ZIP bytes |

For diagnosis, include at least: wrong answer with unknown cause; hinted correct; guessed correct; partial correct; justified correct with transfer; ambiguous valid answer; source unavailable; item exhausted; student asks to stop. Fix outcome rules and the fixed-sequence comparator **before inspecting evaluation results**. Keep reviewer disagreements visible and adjudicated by a separate qualified reviewer.

## Strict publication and acceptance rule

- Engineering CI may pass even if human quality metrics fail; report both separately.
- **Do not** choose pass thresholds after viewing held-out results or advertise any “accuracy” without a defined dataset, sample size, denominator, uncertainty interval and label protocol.
- A reviewer packet passing the JSON verifier proves only the recorded gate, not actual model semantics or independence.
- Stop or revise items with unresolved source/answer risks. A qualified human adjudicator remains mandatory for official/high-stakes use.
- Disclose what is synthetic, what is expert-reviewed, what is independent and what is not. No real-person trials without appropriate permissions, consent and applicable oversight.

## Delivery checklist (future work)

1. Version an item/defect taxonomy and evaluation manifest (only approved or synthetic content).
2. Obtain blinded independent labels and adjudication; freeze a holdout before any tuning.
3. Run actual author and reviewer models, capture failures and repair/re-audit outcomes.
4. Compare adaptive next-question decisions against fixed-order and simple-history baselines.
5. Publish aggregate metrics, confidence intervals, model configuration, costs, and explicit failed gates; update claims only when supported.
