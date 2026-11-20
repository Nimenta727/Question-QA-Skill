# Question-QA-Skill v0.7.0 — Mathematical Equivalence & Safe State

- **Opt-in mathematically equivalent short answers**: exact rational/polynomial comparison over a strictly bounded, safe AST subset; no arbitrary code, functions or unsupported semantic inference. Unrecognized input is left pending for human review, rather than blindly marked wrong. Legacy answer keys are unchanged unless authors opt in.
- **Reliable local study state**: native advisory locks on Linux/macOS/Windows prevent concurrent CLI lost updates on a local filesystem; verified, atomic previous-state backup and explicit state-check/state-recover --confirm. Recovery may lose one completed action; cloud-sync/distributed locks are not supported.
- **Reviewer agreement study tool**: aggregate-only exact agreement, weighted Cohen's kappa, item/criterion disagreement, student-case bootstrap uncertainty and adjudication completeness. Source type is self-declared, and no actual independent human study has yet been conducted; all shipped examples are synthetic.
- **Cross-platform release**: Ubuntu, Windows, macOS × Python3.9/3.12 regression; verified deterministic ZIP, SHA256 sums, extracted package smoke tests and immutable Git-tagged v0.7.0 Release.
- No new model trained against previously used FORGET-SE or ASSISTments 2015 held-out results. No arbitrary student code execution or unverified automatic natural-language scoring introduced.

中文重点：数学正确性只在出题者明确授权的受限表达式内核验；无法理解的答案必须复核。并发锁、原子备份和恢复仅支持本地文件系统。双人评阅统计工具不等于真人研究已经进行，所附案例全部合成。
