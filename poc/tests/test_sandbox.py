import pytest

from leo import sandbox
from leo.sandbox_runner import UnsafeCode, check_code, normalize


@pytest.mark.parametrize("raw, expected", [
    ("2,5x + 0,5", "2.5x + 0.5"),
    ("3·x − 2", "3*x - 2"),
    ("x² + √(x)", "x**2 + sqrt(x)"),
    ("12 : 4", "12/4"),
    ("x^3", "x**3"),
    (r"$\frac{1}{2}x$", "((1)/(2))x"),
])
def test_normalize(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.parametrize("code", [
    "import os",
    "from subprocess import run",
    "open('f.txt')",
    "().__class__.__bases__",
    "eval('1')",
    "getattr(1, 'real')",
])
def test_check_code_rejects(code):
    with pytest.raises(UnsafeCode):
        check_code(code)


def test_exec_factor():
    res = sandbox.exec_code("x = symbols('x')\nresult = factor(x**2 - 9)")
    assert res["ok"] and res["result_str"] == "(x - 3)*(x + 3)"


def test_exec_blocks_import_at_runtime():
    # contourne l'AST côté hôte : le sous-processus doit refuser aussi
    res = sandbox.run_jobs([{"op": "analyze", "candidates": [], "targets": []},
                            {"op": "exec", "code": "from math import *\nresult = sqrt(16)"}])
    assert res[1]["ok"] and res[1]["result_str"] == "4.0"


def test_timeout():
    with pytest.raises(sandbox.SandboxTimeout):
        sandbox.exec_code("while True:\n    pass", timeout=3)


TARGETS = ["3x + 5 = 2x - 7", "x + 5 = -7", "x = -12", "3(x+2) - 2(x-1)", "x + 8"]


@pytest.fixture(scope="module")
def analysis():
    cands = ["x = -12", "-12", "S = {-12}", "x = 12", "x+5=-7", "3x+6-2x+2", "x+8", "3x + 5 = 2x - 7"]
    return {r["text"]: r for r in sandbox.analyze(cands, TARGETS)}


def _eq(analysis, cand):
    return {m["target"] for m in analysis[cand]["matches"] if m["equivalent"]}


def _adv(analysis, cand):
    return {m["target"] for m in analysis[cand]["matches"] if m["equivalent"] and m["not_more_complex"]}


def test_equation_equivalence(analysis):
    assert _eq(analysis, "x = -12") == {0, 1, 2}
    assert _eq(analysis, "-12") == {0, 1, 2}
    assert _eq(analysis, "S = {-12}") == {0, 1, 2}
    assert _eq(analysis, "x = 12") == set()


def test_complexity_distinguishes_progress(analysis):
    # l'énoncé recopié est équivalent à tout mais n'est « avancé » que vis-à-vis de lui-même
    assert _adv(analysis, "3x + 5 = 2x - 7") == {0}
    assert 2 in _adv(analysis, "x = -12")
    assert _adv(analysis, "x+5=-7") == {0, 1}


def test_expression_equivalence(analysis):
    assert _eq(analysis, "3x+6-2x+2") == {3, 4}
    assert _adv(analysis, "3x+6-2x+2") == {3}
    assert _adv(analysis, "x+8") == {3, 4}


def test_positive_domain():
    res = sandbox.analyze(["c = 5", "c = -5"], ["c^2 = 3^2 + 4^2"], domain="positifs")
    assert res[0]["matches"][0]["equivalent"] is True
    assert res[1]["matches"][0]["equivalent"] is False
