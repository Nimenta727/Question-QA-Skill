# v0.7.0 exact opt-in mathematical equivalence for short answers

The historical short-answer key uses normalized exact matching, which is preserved unless a question author **explicitly opts in**.

For a numerical short item add answer_equivalence: {"kind":"rational"}. For limited polynomial expressions add {"kind":"polynomial","variables":["x"]}; ["y"] or ["x","y"] also work. Numeric literals, exact fractions, +,-,*,/ by a nonzero constant, and powers with integer exponent 0..4 are supported; use Python-like x**2 rather than x^2.

The module compares exact Fraction-based sparse polynomials using a whitelist of AST node types. It never uses eval, exec, external model calls, arbitrary Python functions, imports or operating-system commands. To prevent resource exhaustion, source length, AST nodes, depth, degree, term count and coefficient bit length are bounded.

Examples: 14/2 and 7 are numerically identical; x+x and 2*x are identical polynomials; (x+1)*(x-1) and x**2-1 are equivalent on their polynomial domain. Arbitrary variable denominators, functions, radical expressions, natural language, units, piecewise definitions, contextual restrictions and proof correctness are **not supported**. Unsupported input is explicitly left pending for independent review and is NOT automatically scored incorrect. An explicitly valid but mathematically inequivalent expression is scored incorrect under the opt-in rule.

Manual equivalence review remains available with --review-equivalent and --reason. That step requires an actual qualified review of the answer, not a flag used merely to silence an error. Existing non-opted-in short items and single-choice questions retain their exact historical behavior. See examples/sample_bank.json (ALG-003).
