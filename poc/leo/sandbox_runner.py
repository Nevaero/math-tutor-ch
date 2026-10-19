"""Exécuteur isolé, lancé dans un sous-processus (`python -I`) par `leo.sandbox`.

Lit sur stdin {"jobs": [...]} et écrit sur stdout une liste de résultats JSON.
Ce fichier ne doit importer que la bibliothèque standard et SymPy : il est exécuté
sans accès au paquet `leo`.

Opérations :
- exec    : exécute du code SymPy généré par le LLM (vérifié par AST, builtins restreints)
- analyze : pour chaque texte candidat, indique à quelles cibles il est mathématiquement
            équivalent et s'il est au plus aussi « avancé » (pas plus complexe) qu'elles.
"""

import ast
import builtins
import contextlib
import io
import json
import random
import re
import sys

ALLOWED_IMPORTS = {"sympy", "math", "fractions", "numpy"}
FORBIDDEN_NAMES = {
    "__import__", "open", "eval", "exec", "compile", "globals", "locals", "vars",
    "input", "breakpoint", "getattr", "setattr", "delattr", "exit", "quit", "help",
    "memoryview", "__builtins__", "type", "object",
}
SAFE_BUILTINS = [
    "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "int", "isinstance",
    "len", "list", "map", "max", "min", "pow", "print", "range", "reversed", "round", "set",
    "sorted", "str", "sum", "tuple", "zip", "Exception", "ValueError", "ZeroDivisionError",
]


class UnsafeCode(ValueError):
    pass


def check_code(code):
    """Refuse imports hors liste blanche, noms dangereux et attributs privés."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise UnsafeCode(f"import interdit : {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if not node.module or node.module.split(".")[0] not in ALLOWED_IMPORTS:
                raise UnsafeCode(f"import interdit : {node.module}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise UnsafeCode(f"nom interdit : {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise UnsafeCode(f"attribut interdit : {node.attr}")
    return tree


# --- Notation scolaire -> syntaxe SymPy -------------------------------------------------

def latex_to_plain(text):
    t = text.replace("$", "")
    t = re.sub(r"\\left|\\right|\\,|\\;|\\!|\\displaystyle", "", t)
    t = t.replace(r"\cdot", "*").replace(r"\times", "*").replace(r"\div", "/").replace(r"\pi", "pi")
    for _ in range(5):  # \frac imbriqués simples
        t = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", t)
        t = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", t)
        t = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", t)
    t = t.replace(r"\{", "{").replace(r"\}", "}")
    return t


def normalize(text):
    """Notation suisse romande -> syntaxe parsable. Ensembles : séparateur « ; »."""
    t = text.strip()
    if "\\" in t or "$" in t:
        t = latex_to_plain(t)
    for src, dst in (("−", "-"), ("–", "-"), ("·", "*"), ("×", "*"), ("÷", "/"),
                     ("π", "pi"), ("²", "**2"), ("³", "**3")):
        t = t.replace(src, dst)
    t = re.sub(r"√\s*\(", "sqrt(", t)
    t = re.sub(r"√\s*(\d+|[a-zA-Z])", r"sqrt(\1)", t)
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)  # virgule décimale
    t = t.replace("^", "**")
    t = re.sub(r"(?<=[\w)])\s*:\s*(?=[\w(])", "/", t)  # « : » comme division
    return t


def _parse_expr(s, evaluate=True):
    from sympy.parsing.sympy_parser import (
        convert_xor, implicit_multiplication_application, parse_expr, standard_transformations,
    )
    transforms = standard_transformations + (implicit_multiplication_application, convert_xor)
    return parse_expr(s, transformations=transforms, evaluate=evaluate)


def parse_math(text):
    """Retourne (kind, valeur, forme_brute) avec kind ∈ {expression, equation, set}."""
    from sympy import FiniteSet

    t = normalize(text)
    m = re.fullmatch(r"\s*(?:S\s*=\s*)?\{(.*)\}\s*", t)
    if m:
        inner = m.group(1).strip()
        elems = [] if not inner else [_parse_expr(e) for e in re.split(r"[;,]", inner)]
        return "set", FiniteSet(*elems), None
    if t.count("=") == 1:
        lhs, rhs = t.split("=")
        return ("equation", (_parse_expr(lhs), _parse_expr(rhs)),
                (_parse_expr(lhs, evaluate=False), _parse_expr(rhs, evaluate=False)))
    if "=" in t:
        raise ValueError("plusieurs signes =")
    return "expression", _parse_expr(t), _parse_expr(t, evaluate=False)


def complexity(parsed):
    from sympy import count_ops

    kind, value, raw = parsed
    if kind == "set":
        return len(value)
    if kind == "equation":
        return int(count_ops(raw[0])) + int(count_ops(raw[1]))
    return int(count_ops(raw))


# --- Équivalence -----------------------------------------------------------------------

def _expr_equal(a, b):
    from sympy import simplify

    try:
        if simplify(a - b) == 0:
            return True
    except Exception:
        pass
    syms = sorted((a - b).free_symbols, key=str)
    if not syms:
        try:
            return abs(complex((a - b).evalf())) < 1e-9
        except Exception:
            return False
    rng = random.Random(42)
    for _ in range(6):
        point = {s: rng.uniform(-3, 3) for s in syms}
        try:
            va, vb = complex(a.evalf(subs=point)), complex(b.evalf(subs=point))
        except Exception:
            return False
        if abs(va - vb) > 1e-7 * (1 + abs(va)):
            return False
    return True


def _domain(name):
    from sympy import Interval, S, oo

    return Interval.open(0, oo) if name == "positifs" else S.Reals


def _solution_set(eq, domain="reels"):
    from sympy import solveset

    f = eq[0] - eq[1]
    syms = f.free_symbols
    if len(syms) != 1:
        return None
    sym = next(iter(syms))
    return sym, solveset(f, sym, _domain(domain))


def equivalent(a, b, domain="reels"):
    """`domain` = « reels » ou « positifs » (longueurs, durées, quantités)."""
    from sympy import FiniteSet, simplify

    (ka, va, _), (kb, vb, _) = a, b
    if ka == kb == "expression":
        return _expr_equal(va, vb)
    if ka == kb == "set":
        return va.intersect(_domain(domain)) == vb.intersect(_domain(domain))
    if ka == kb == "equation":
        sa, sb = _solution_set(va, domain), _solution_set(vb, domain)
        if sa and sb:
            return sa[0] == sb[0] and sa[1] == sb[1]
        fa, fb = va[0] - va[1], vb[0] - vb[1]
        if fa == 0 or fb == 0:
            return simplify(fa) == simplify(fb)
        q = simplify(fa / fb)
        return bool(q.is_number) and q != 0
    kinds = {ka: va, kb: vb}
    if set(kinds) == {"equation", "set"}:
        sol = _solution_set(kinds["equation"], domain)
        return bool(sol) and sol[1] == kinds["set"].intersect(_domain(domain))
    if set(kinds) == {"expression", "set"}:
        expr = kinds["expression"]
        return not expr.free_symbols and kinds["set"] == FiniteSet(expr)
    if set(kinds) == {"expression", "equation"}:
        expr = kinds["expression"]
        sol = _solution_set(kinds["equation"], domain)
        return not expr.free_symbols and bool(sol) and sol[1] == FiniteSet(expr)
    return False


# --- Opérations ------------------------------------------------------------------------

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] not in ALLOWED_IMPORTS:
        raise ImportError(f"import interdit : {name}")
    return builtins.__import__(name, globals, locals, fromlist, level)


def op_exec(job):
    import sympy

    code = job["code"]
    check_code(code)
    ns = {}
    exec("from sympy import *", ns)
    safe = {k: getattr(builtins, k) for k in SAFE_BUILTINS}
    safe["__import__"] = _safe_import
    ns["__builtins__"] = safe
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<leo>", "exec"), ns)
    result = ns.get("result")
    return {
        "ok": True,
        "result_str": None if result is None else str(result),
        "result_latex": None if result is None else sympy.latex(result),
        "stdout": buf.getvalue()[:2000],
    }


def op_analyze(job):
    targets = []
    for t in job["targets"]:
        try:
            p = parse_math(t)
            targets.append((p, complexity(p)))
        except Exception:
            targets.append(None)
    out = []
    for cand in job["candidates"]:
        try:
            p = parse_math(cand)
            c = complexity(p)
        except Exception:
            out.append({"text": cand, "parsed": False, "matches": []})
            continue
        matches = []
        for i, target in enumerate(targets):
            if target is None:
                continue
            tp, tc = target
            try:
                eq = equivalent(p, tp, job.get("domain", "reels"))
            except Exception:
                eq = False
            matches.append({"target": i, "equivalent": bool(eq), "not_more_complex": c <= tc})
        out.append({"text": cand, "parsed": True, "kind": p[0], "matches": matches})
    return {"ok": True, "results": out}


OPS = {"exec": op_exec, "analyze": op_analyze}


def main():
    request = json.load(sys.stdin)
    results = []
    for job in request["jobs"]:
        try:
            results.append(OPS[job["op"]](job))
        except Exception as exc:  # une erreur dans un job n'empêche pas les autres
            results.append({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:300]}"})
    sys.stdout.write(json.dumps(results))


if __name__ == "__main__":
    main()
