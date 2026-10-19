"""Plan de résolution interne : généré par le LLM, vérifié étape par étape par la sandbox.

Le plan n'est jamais montré à l'élève. Il sert au tuteur (étape suivante, indices),
au suivi de progression et au garde-fou anti-fuite.
"""

from dataclasses import dataclass, field

from . import sandbox
from .llm import ChatProvider, extract_json
from .mathtext import variables_of
from .prompts import load_prompt
from .sandbox_runner import UnsafeCode


@dataclass
class Step:
    description: str
    math: str
    verified: bool = False


@dataclass
class Plan:
    notion: str
    objectif_per: str
    forme_initiale: str
    etapes: list[Step]
    solution_finale: str
    domaine: str = "reels"
    sympy_result: str | None = None
    verified: bool = False
    issues: list[str] = field(default_factory=list)

    @property
    def variables(self) -> list[str]:
        return variables_of(self.forme_initiale) or ["x"]

    def targets(self) -> list[str]:
        """Cibles d'analyse : [forme_initiale, étape 0..n-1, solution_finale]."""
        return [self.forme_initiale, *(s.math for s in self.etapes), self.solution_finale]


def _verify(plan: Plan) -> None:
    issues = []
    # 1. Le résultat calculé par SymPy doit correspondre à la solution annoncée
    # 2. Chaque étape doit être équivalente à la forme initiale
    targets = [plan.solution_finale, plan.forme_initiale]
    cands = [s.math for s in plan.etapes] + [plan.solution_finale]
    if plan.sympy_result:
        cands.append(plan.sympy_result)
    results = sandbox.analyze(cands, targets, plan.domaine)
    by_text = {r["text"]: r for r in results}

    def eq(text: str, target: int) -> bool:
        r = by_text.get(text)
        return bool(r and any(m["target"] == target and m["equivalent"] for m in r["matches"]))

    for step in plan.etapes:
        step.verified = eq(step.math, 1)
        if not step.verified:
            issues.append(f"étape non équivalente à la forme initiale : {step.math}")
    if not eq(plan.solution_finale, 1):
        issues.append(f"solution finale non équivalente à la forme initiale : {plan.solution_finale}")
    if plan.sympy_result is None:
        issues.append("le code SymPy n'a pas produit de résultat")
    elif not eq(plan.sympy_result, 0):
        issues.append(f"SymPy trouve {plan.sympy_result}, différent de {plan.solution_finale}")
    plan.issues = issues
    plan.verified = not issues


def build_plan(llm: ChatProvider, enonce: str, degre: str, attempts: int = 2) -> Plan:
    system = load_prompt("plan")
    user = f"Degré : {degre}\nÉnoncé :\n{enonce}"
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    plan = None
    for _ in range(attempts):
        raw = llm.chat(messages, temperature=0.1, max_tokens=1500)
        data = extract_json(raw)
        try:
            result = sandbox.exec_code(data.get("code_sympy", ""))
        except (UnsafeCode, SyntaxError, sandbox.SandboxError) as exc:
            result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        plan = Plan(
            notion=data.get("notion", ""),
            objectif_per=data.get("objectif_per", ""),
            forme_initiale=data["forme_initiale"],
            etapes=[Step(e["description"], e["math"]) for e in data.get("etapes", [])],
            solution_finale=data["solution_finale"],
            domaine="positifs" if data.get("domaine") == "positifs" else "reels",
            sympy_result=result.get("result_str") if result.get("ok") else None,
        )
        if not result.get("ok"):
            plan.issues.append(f"erreur SymPy : {result.get('error')}")
        _verify(plan)
        if plan.verified:
            return plan
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "La vérification par calcul formel a échoué :\n- "
             + "\n- ".join(plan.issues) + "\nCorrige le plan et renvoie uniquement le JSON."},
        ]
    return plan
