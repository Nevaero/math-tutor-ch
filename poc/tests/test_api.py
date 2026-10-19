import json

from fastapi.testclient import TestClient

from leo import api
from leo.llm import FakeProvider
from tests.test_tutor import ENONCE, PLAN_JSON

SHEET_JSON = json.dumps({
    "notion": "Équations du premier degré", "objectif_per": "MSN 33", "attendus": "Résoudre avec les règles d'équivalence.",
    "prerequis": ["Termes semblables"], "deroule": ["Isoler x"], "pieges": ["Oublier un membre"],
    "questions": ["Que veut dire résoudre ?", "Que fais-tu des deux membres ?"],
})


def client(replies):
    fake = FakeProvider(replies)
    api.llm.cache_clear()
    api.app.dependency_overrides = {}
    api.llm = lambda: fake  # noqa: E731 — remplace le fournisseur réel
    api.llm.cache_clear = lambda: None
    return TestClient(api.app), fake


def test_tutor_endpoints():
    c, _ = client([PLAN_JSON, "Salut ! Qu'as-tu essayé ?", "Bravo, c'est la solution !"])
    r = c.post("/tutor/sessions", json={"enonce": ENONCE, "degre": "10H", "canton": "GE"}).json()
    assert r["plan_verified"] and r["message"].startswith("Salut")
    r2 = c.post(f"/tutor/sessions/{r['session_id']}/messages", json={"text": "x = -12"}).json()
    assert r2["solved"] and r2["step_reached"] == r2["steps_total"]
    assert c.post("/tutor/sessions/inconnue/messages", json={"text": "x"}).status_code == 404


def test_copilot_endpoint():
    c, _ = client([PLAN_JSON, SHEET_JSON, "Parce qu'on garde l'égalité vraie."])
    r = c.post("/copilot", json={"enonce": ENONCE}).json()
    assert r["objectif_per"] == "MSN 33" and len(r["questions"]) == 2
    assert r["solution"][-1]["math"] == "x = -12" and r["solution"][-1]["verified"]
    assert "<details>" in r["markdown"]
    r2 = c.post(f"/copilot/{r['session_id']}/messages", json={"text": "Pourquoi ?"}).json()
    assert "égalité" in r2["message"]


def test_extract_rejects_bad_type():
    c, _ = client([])
    r = c.post("/extract", files={"image": ("a.txt", b"hello", "text/plain")})
    assert r.status_code == 422
