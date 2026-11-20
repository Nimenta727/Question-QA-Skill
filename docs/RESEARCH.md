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
