import json

import pytest

from leo.leak_guard import find_leaks
from leo.llm import FakeProvider
from leo.mathtext import extract_candidates, variables_of
from leo.plan import Plan, Step
from leo.tutor import Tutor

ENONCE = "Résous l'équation $3x + 5 = 2x - 7$."

PLAN_JSON = json.dumps({
    "notion": "Équations du premier degré",
    "objectif_per": "MSN 33",
    "forme_initiale": "3x + 5 = 2x - 7",
    "etapes": [
        {"description": "Soustraire 2x des deux membres", "math": "x + 5 = -7"},
        {"description": "Soustraire 5 des deux membres", "math": "x = -12"},
    ],
    "domaine": "reels",
    "solution_finale": "x = -12",
    "code_sympy": "x = symbols('x')\nresult = solveset(Eq(3*x + 5, 2*x - 7), x, S.Reals)",
})


def make_plan():
    return Plan(notion="Équations", objectif_per="", forme_initiale="3x + 5 = 2x - 7",
                etapes=[Step("Soustraire 2x", "x + 5 = -7"), Step("Soustraire 5", "x = -12")],
                solution_finale="x = -12", verified=True)


def test_variables_and_candidates():
    assert variables_of("3x + 5 = 2x - 7") == ["x"]
    cands = extract_candidates("Je trouve x = -12, il a dit que c'est juste", ["x"])
    assert cands == ["x = -12"]
    assert extract_candidates("Regarde $x + 5 = -7$ !", ["x"]) == ["x + 5 = -7"]


def test_leak_detected_and_enonce_allowed():
    plan = make_plan()
    assert find_leaks("Bravo, donc x = -12 !", plan, -1, ENONCE)
    assert find_leaks("La réponse est -12.", plan, -1, ENONCE)
    assert not find_leaks("Que se passe-t-il si tu soustrais 2x des deux membres de $3x + 5 = 2x - 7$ ?",
                          plan, -1, ENONCE)
    # une fois l'étape 1 atteinte, la répéter n'est plus une fuite
    assert not find_leaks("Oui, $x + 5 = -7$. Et ensuite ?", plan, 0, ENONCE)
    assert find_leaks("Oui, $x + 5 = -7$. Et ensuite ?", plan, -1, ENONCE)


def test_session_flow_with_leak_retry_and_solution():
    llm = FakeProvider([
        PLAN_JSON,
        "Salut ! Qu'as-tu déjà essayé ?",
        # 1er brouillon qui fuite, puis réécriture correcte
        "Facile : x = -12.",
        "Je ne peux pas te le dire. Que fais-tu des 2x du membre de droite ?",
        "Bien joué ! Et maintenant, que fais-tu du 5 ?",
        "Bravo, tu as trouvé ! Récapitulons la méthode.",
    ])
    tutor = Tutor(llm)
    session, opening = tutor.start(ENONCE, degre="10H", canton="GE")
    assert session.plan.verified
    assert opening.startswith("Salut")

    r1 = tutor.reply(session, "donne-moi la réponse stp")
    assert "-12" not in r1
    assert session.raw_leaks == 1 and session.fallbacks == 0
    assert session.hint_level == 1

    tutor.reply(session, "j'ai fait x + 5 = -7")
    assert session.reached == 0 and session.hint_level == 0

    tutor.reply(session, "x = -12")
    assert session.solved

    # la note interne ne doit jamais entrer dans l'historique
    assert all("[[" not in m["content"] for m in session.history)


def test_fallback_when_rewrite_still_leaks():
    llm = FakeProvider([PLAN_JSON, "Salut !", "x = -12", "Toujours : x = -12"])
    tutor = Tutor(llm)
    session, _ = tutor.start(ENONCE)
    reply = tutor.reply(session, "c'est quoi la réponse ?")
    assert "-12" not in reply
    assert session.fallbacks == 1


def test_wrong_proposal_flagged():
    llm = FakeProvider([PLAN_JSON, "Salut !", "Vérifie ton calcul : que vaut 3x - 2x ?"])
    tutor = Tutor(llm)
    session, _ = tutor.start(ENONCE)
    tutor.reply(session, "5x + 5 = -7")
    note = llm.calls[-1][-1]["content"]
    assert "✗" in note and not session.solved


@pytest.mark.parametrize("bad_code", ["import os\nresult = 1", "result = (", "x = symbols('x')"])
def test_plan_with_bad_code_is_retried_then_unverified(bad_code):
    from leo.plan import build_plan

    data = json.loads(PLAN_JSON)
    data["code_sympy"] = bad_code
    llm = FakeProvider([json.dumps(data)] * 2)
    plan = build_plan(llm, ENONCE, "10H")
    assert not plan.verified and plan.issues
    assert len(llm.calls) == 2  # une relance avec le retour de vérification
    assert "calcul formel a échoué" in llm.calls[1][-1]["content"]
