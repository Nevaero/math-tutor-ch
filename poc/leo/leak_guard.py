"""Garde-fou anti-fuite : un message du tuteur ne doit pas révéler une étape (ou la solution)
que l'élève n'a pas encore produite (specs/05-moteur-pedagogique.md §5.3).

Règle : un fragment du message fuite s'il est mathématiquement équivalent à une étape
non atteinte ET pas plus complexe qu'elle (il en dit au moins autant). Rappeler l'énoncé,
plus complexe, n'est donc pas une fuite.
"""

from dataclasses import dataclass

from . import sandbox
from .mathtext import compact, extract_candidates
from .plan import Plan


@dataclass
class Leak:
    fragment: str
    revealed: str


def find_leaks(message: str, plan: Plan, reached: int, enonce: str) -> list[Leak]:
    """`reached` = indice de la dernière étape atteinte par l'élève (-1 : aucune).
    La solution finale reste secrète tant que l'élève ne l'a pas trouvée."""
    secrets = [s.math for i, s in enumerate(plan.etapes) if i > reached]
    if reached < len(plan.etapes):
        secrets.append(plan.solution_finale)
    if not secrets:
        return []
    enonce_c = compact(enonce)
    cands = [c for c in extract_candidates(message, plan.variables) if compact(c) not in enonce_c]
    leaks = []
    for res in sandbox.analyze(cands, secrets, plan.domaine):
        for m in res["matches"]:
            if m["equivalent"] and m["not_more_complex"]:
                leaks.append(Leak(res["text"], secrets[m["target"]]))
                break
    return leaks
