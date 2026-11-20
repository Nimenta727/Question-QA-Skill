"""Safe bounded exact equivalence for explicitly opted-in numeric short answers.

This is not a general CAS. It accepts only restricted Python-like expressions
and exact rational polynomial arithmetic; no eval, code execution, functions,
variable denominators, arbitrary roots, units or mathematical domain proofs.
"""
import ast
import math
from fractions import Fraction

MAX_SOURCE = 120
MAX_NODES = 80
MAX_DEPTH = 16
MAX_TERMS = 60
MAX_DEGREE = 8
MAX_BITS = 128
VARS = ("x", "y")


def validate_spec(spec):
    if not isinstance(spec, dict):
        raise ValueError("answer_equivalence must be an object")
    if spec == {"kind": "rational"}:
        return ()
    if (set(spec) == {"kind", "variables"} and spec["kind"] == "polynomial"
            and isinstance(spec["variables"], list)
            and spec["variables"] in (["x"], ["y"], ["x", "y"])):
        return tuple(spec["variables"])
    raise ValueError("unsupported answer_equivalence; use rational or polynomial with x/y")


def _check(poly):
    if len(poly) > MAX_TERMS:
        raise ValueError("too many polynomial terms")
    for mono, number in poly.items():
        if sum(mono) > MAX_DEGREE:
            raise ValueError("polynomial degree too high")
        if number.numerator.bit_length() > MAX_BITS or number.denominator.bit_length() > MAX_BITS:
            raise ValueError("numeric expression exceeds bit limit")
    return {key: val for key, val in poly.items() if val}


def _sum(a, b, sign=1):
    result = dict(a)
    for key, val in b.items():
        result[key] = result.get(key, Fraction(0)) + sign * val
    return _check(result)


def _mul(a, b):
    out = {}
    for ma, va in a.items():
        for mb, vb in b.items():
            key = tuple(x + y for x, y in zip(ma, mb))
            if sum(key) > MAX_DEGREE:
                raise ValueError("polynomial degree too high")
            out[key] = out.get(key, Fraction(0)) + va * vb
            if len(out) > MAX_TERMS:
                raise ValueError("too many polynomial terms")
    return _check(out)


def polynomial(source, variables=()):
    if not isinstance(source, str) or not source.strip() or len(source) > MAX_SOURCE:
        raise ValueError("expression too long or empty")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError("unsupported expression syntax") from exc
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise ValueError("expression too complex")
    zero = (0,) * len(variables)

    def walk(node, depth):
        if depth > MAX_DEPTH:
            raise ValueError("expression too deep")
        if isinstance(node, ast.Expression):
            return walk(node.body, depth+1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("nonfinite literal")
            if abs(value) > 10 ** 9:
                raise ValueError("large numeric literal")
            return _check({zero: Fraction(str(value))})
        if isinstance(node, ast.Name) and node.id in variables:
            monomial = tuple(int(v == node.id) for v in variables)
            return {monomial: Fraction(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            parsed = walk(node.operand, depth+1)
            return parsed if isinstance(node.op, ast.UAdd) else _check({k:-v for k,v in parsed.items()})
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int or not 0 <= node.right.value <= 4:
                    raise ValueError("only integer powers 0..4")
                base = walk(node.left, depth+1)
                out = {zero: Fraction(1)}
                for _ in range(node.right.value):
                    out = _mul(out, base)
                return out
            left, right = walk(node.left, depth+1), walk(node.right, depth+1)
            if isinstance(node.op, ast.Add):
                return _sum(left, right)
            if isinstance(node.op, ast.Sub):
                return _sum(left, right, -1)
            if isinstance(node.op, ast.Mult):
                return _mul(left, right)
            if isinstance(node.op, ast.Div):
                if not right or set(right) != {zero}:
                    raise ValueError("division by a variable or zero unsupported")
                divisor = right[zero]
                return _check({k:v / divisor for k,v in left.items()})
        raise ValueError("unsafe or unsupported mathematical expression")
    return walk(tree, 0)


def matches(key, response, spec):
    variables = validate_spec(spec)
    return polynomial(key, variables) == polynomial(response, variables)
