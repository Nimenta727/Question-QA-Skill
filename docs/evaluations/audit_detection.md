# Study B: Independent item audit misses and false alarms / 审题漏检与误报

**NOT RUN** · RM-03, RM-04, RM-05, RM-06.

1. **Gold set:** Freeze independently adjudicated defective and sound items from distinct reasoning families. Defects include wrong key, hidden second correct answer, ambiguous premise, rubric gap, invalid distractor, fabricated/mismatched source and out-of-scope claim. Include clean controls and difficult near-misses.
2. **Blind audit:** Auditor receives no gold labels or author verdicts. Record accept/block/uncertain, *actual stated reason*, source checks, item-family ID and pinned model/Skill version.
3. **Reason-match adjudication:** Independent reviewer decides if a blocked defective item identified the **real** flaw. Merely rejecting a defective question for an unrelated reason is **not detection**; mark `caught_actual_defect=false`.
4. **Primary metrics:** Detection = defective items blocked **for the true flaw** / all adjudicated defective items. Miss rate = defective items not correctly identified / all adjudicated defective items (separately disclose accepted, uncertain and wrong-reason blocks). False-alarm rate = sound items blocked / all adjudicated sound items; report sound uncertainty separately.
5. **Audit trail:** Report TP/FP/FN/TN policy, defect-category denominators, item-family clustering, reviewer disagreement, unresolved items, latency and tokens only if actually measured. No independent-expert claim from same-model self-review.
6. **Exit gate:** Two independent expert reviews or documented adjudication, with the gold labels frozen before inference; report unresolved cases rather than quietly discarding them.
