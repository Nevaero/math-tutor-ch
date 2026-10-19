"""Mode Copilote Parent : fiche structurée + solution vérifiée (repliée côté app)."""

from dataclasses import dataclass, field

from . import glossary
from .curriculum.search import context_for
from .llm import ChatProvider, extract_json
from .plan import Plan, build_plan
from .prompts import load_prompt


@dataclass
class CopilotSheet:
    plan: Plan
    notion: str
    prerequis: list[str]
    deroule: list[str]
    pieges: list[str]
    questions: list[str]
    objectif_per: str = ""
    attendus: str = ""
    per_context: str = ""
    history: list[dict] = field(default_factory=list)

    def solution(self) -> list[dict]:
        p = self.plan
        steps = [{"description": s.description, "math": s.math, "verified": s.verified} for s in p.etapes]
        return steps + [{"description": "Solution", "math": p.solution_finale, "verified": p.verified}]

    def markdown(self) -> str:
        def bullets(items):
            return "\n".join(f"- {i}" for i in items)

        sol = "\n".join(f"{i + 1}. {s['description']} : `{s['math']}` {'✓' if s['verified'] else '⚠ non vérifié'}"
                        for i, s in enumerate(self.solution()))
        per = f"*{self.objectif_per}* — {self.attendus}\n\n" if self.objectif_per else ""
        return (f"## {self.notion}\n\n{per}**Prérequis**\n{bullets(self.prerequis)}\n\n"
                f"**Déroulé**\n{bullets(self.deroule)}\n\n**Pièges fréquents**\n{bullets(self.pieges)}\n\n"
                f"**Questions à poser à votre enfant**\n{bullets(self.questions)}\n\n"
                f"<details><summary>Solution (pour vous)</summary>\n\n{sol}\n\n</details>\n")


def _plan_text(plan: Plan) -> str:
    steps = "\n".join(f"- {s.description} : {s.math}" for s in plan.etapes)
    return f"Départ : {plan.forme_initiale}\n{steps}\nSolution : {plan.solution_finale}"


def build_sheet(llm: ChatProvider, enonce: str, degre: str = "10H", canton: str = "VD") -> CopilotSheet:
    plan = build_plan(llm, enonce, degre)
    per = context_for(f"{plan.notion}. {enonce}", degre, k=5)
    system = load_prompt("copilot", degre=degre, canton=canton, glossaire=glossary.for_degree(degre),
                         enonce=enonce, plan=_plan_text(plan), per=per or "(non disponible)")
    data = extract_json(llm.chat([{"role": "system", "content": system},
                                  {"role": "user", "content": "Prépare la fiche."}], max_tokens=1500))
    return CopilotSheet(plan=plan, notion=data.get("notion") or plan.notion,
                        prerequis=data.get("prerequis", []), deroule=data.get("deroule", []),
                        pieges=data.get("pieges", []), questions=data.get("questions", []),
                        objectif_per=data.get("objectif_per", ""), attendus=data.get("attendus", ""),
                        per_context=per)


def follow_up(llm: ChatProvider, sheet: CopilotSheet, enonce: str, question: str) -> str:
    """Question de suivi du parent (« pourquoi cette étape ? », « s'il répond X ? »)."""
    system = (f"Tu es Leo, en mode Copilote Parent. Vouvoiement, réponses courtes et concrètes, "
              f"vocabulaire de l'école.\nExercice : {enonce}\nPlan vérifié :\n{_plan_text(sheet.plan)}")
    messages = [{"role": "system", "content": system}, *sheet.history, {"role": "user", "content": question}]
    answer = llm.chat(messages)
    sheet.history += [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
    return answer
