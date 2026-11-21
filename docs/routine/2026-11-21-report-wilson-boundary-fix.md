# 2026-11-21 — Wilson interval endpoint precision after cross-platform CI

## Observed failure
- The first PR CI on Linux/Windows/macOS identified a numeric boundary failure in `test_wilson_intervals_are_bounded`: for k=0, n=6, subtraction/cancellation yielded a lower endpoint of about 2.8e-17 instead of mathematically exact 0.
- The corresponding report calculation could display an imprecise lower bound for zero successes. No statistical dataset or model run was involved.

## Actual fix
- Explicitly set the Wilson lower bound to 0 when k=0 and the upper bound to 1 when k=n; retain the usual formula otherwise.
- Keep the original strict regression test (no tolerance relaxation). This is a numeric presentation correctness fix, not a new psychometric validation claim.

## Next
- Re-run all platform CI plus the Full ZIP tests; verify the report generator with synthetic input.
- Add bilingual source-linked design and usage guides; no real model/expert trials claimed.
