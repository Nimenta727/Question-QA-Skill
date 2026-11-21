# Study C: Adaptive vs fixed-order follow-up / 自适应追问与固定题序对照

**NOT RUN** · RM-07, RM-08, RM-09, RM-10, RM-11.

1. **Frozen reasoning cases:** Use licensed or synthetic, de-identified traces covering wrong/unknown cause, guessed correct, hinted correct, partial, justified correct, alternative valid reasoning, transfer, stop and exhausted question family. Group by genuine reasoning family.
2. **Pre-register control:** Freeze the fixed-order question sequence and tie-breaking policy **before** inspecting model results. Give both arms identical source material, question pool, model, Skill constraints, turn limit and budget. Record any deviations.
3. **Paired execution:** Run both adaptive and fixed-order strategies on each frozen case. Randomize presentation order; blind expert graders to strategy arm where possible. Log actual model calls, case hashes and decision metadata.
4. **Primary endpoint:** Paired expert-rated *diagnostic information value* of the chosen next question for the observed reasoning, using a pre-specified ordinal rubric; report per-family paired differences and adjudication disagreements, not just a single average.
5. **Secondary endpoints:** Repeated item-family rate, unjustified misconception labels, invalid questions, appropriate stop, token usage, number of calls, measured latency and optional transfer performance. Report missing telemetry as missing.
6. **Interpretation:** Offline replay evaluates *decision quality*, **not causal learning gain**. Genuine learning improvement requires a separate consented prospective, learner-level study with independent delayed assessment and suitable randomization.
