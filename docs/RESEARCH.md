# Evidence base / 学术依据（2026-11-20）

Design decisions are inspired by the following sources; the repo implements lightweight *practical heuristics*, NOT scientific reproductions of these models.

1. Mislevy, R. (2003), Evidence-Centered Design: https://cresst.org/publication/a-brief-introduction-to-evidence-centered-design/
   - Translate construct -> observable evidence -> item/task. Used for claim / evidence fields and source audit.
2. Roediger & Karpicke (2006), Test-Enhanced Learning: https://pubmed.ncbi.nlm.nih.gov/16507066/
   - Retrieval can aid later retention; used to justify asking, not merely explaining.
3. Dunlosky et al. (2013), Improving Students' Learning With Effective Learning Techniques: https://www.psychologicalscience.org/publications/journals/pspi/learning-techniques.html
   - Practice testing and distributed practice have strong supporting evidence; motivates follow-ups.
4. Carnegie Mellon DataLab, Bayesian Knowledge Tracing overview: https://www.cmu.edu/datalab/getting-started/key-concepts.html
   - Knowledge should be tracked across observations. The project's simple smoothed score is *not* BKT.
5. ETS (2022), Guidelines for Developing Fair Tests and Communications: https://www.ets.org/pdfs/about/fair-tests-and-communications.pdf
   - Fair coverage and avoidance of irrelevant obstacles are part of validity.
6. Educator's Blueprint (2023), high-quality MCQ design: https://pmc.ncbi.nlm.nih.gov/articles/PMC9873868/
   - Plausible distractors, unambiguous stems and evidence-backed review.
7. Agent Skills open spec: https://github.com/agentskills/agentskills
   - Progressive disclosure; top-level SKILL.md, scoped references, optional scripts.

## Claims we do NOT make
No calibrated item-response parameters (IRT), no certified CAT, no validated learner probability of mastery, no automatic fairness guarantee, no automatic source verification by the CLI. Thresholds and review intervals are transparent implementation defaults to be tuned against real item response data, not empirical accuracy claims.


## Diagnostic fidelity research (2026-11-20) / 诊断精度研究
Compared implementations and their appropriate uses:
- https://github.com/CAHLR/pyBKT — models slip, guess and learning transitions, but requires parameter fitting. We adopt the principle of uncertain knowledge, not its uncalibrated probabilities.
- https://github.com/pykt-team/pykt-toolkit — sequence-based deep KT benchmarks; not suitable as a default zero-dependency runtime without training data.
- https://github.com/douglasrizzo/catsim — IRT-based adaptive testing; item parameters should be calibrated before using its test information as a certainty measure.
- https://github.com/open-spaced-repetition/py-fsrs — spaced-repetition scheduler; our simple due-date defaults are NOT FSRS.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13121518/ — distractor selection can support cognitive diagnosis when distractors and skills are properly linked and validated.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12705826/ — self-evaluation confidence has measurable calibration limitations and should be a supporting rather than decisive indicator.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9873868/ — independent checking, plausible distractors and validity evidence matter for robust items.
- https://www.tandfonline.com/doi/full/10.1080/2331186X.2026.2743418 — item-bank coverage, fairness and exposure are integral to responsible CAT systems.

What is implemented: deterministic family/day evidence deduplication; cognitive-level gates; weak-confidence/assisted evidence discounting; reviewed misconception labels; branching heuristics and bounded sessions. What is NOT implemented: calibrated BKT/IRT/CAT inference, fitted FSRS, or claimed empirical accuracy improvement. Calibration on held-out student sequences is required before claiming improved prediction.
