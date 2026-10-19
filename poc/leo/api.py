"""API HTTP du PoC. Lancement : uvicorn leo.api:app --reload

Sessions en mémoire (PoC) ; en production : Redis avec TTL (specs/06-architecture-technique.md).
"""

import time
import uuid
from functools import cache

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from . import copilot as copilot_mod
from .config import settings
from .extraction import extract_exercises
from .llm import InfomaniakProvider
from .tutor import Tutor, TutorSession

app = FastAPI(title="Leo — PoC tuteur de mathématiques")

TUTOR_SESSIONS: dict[str, TutorSession] = {}
COPILOT_SESSIONS: dict[str, tuple[copilot_mod.CopilotSheet, str, float]] = {}


@cache
def llm() -> InfomaniakProvider:
    return InfomaniakProvider()


def _purge() -> None:
    now = time.time()
    for sid in [k for k, s in TUTOR_SESSIONS.items() if now - s.last_active > settings.session_ttl_s]:
        del TUTOR_SESSIONS[sid]
    for sid in [k for k, (_, _, t) in COPILOT_SESSIONS.items() if now - t > settings.session_ttl_s]:
        del COPILOT_SESSIONS[sid]


class StartRequest(BaseModel):
    enonce: str
    degre: str = "10H"
    canton: str = "VD"


class MessageRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"ok": True, "chat_model": settings.chat_model, "vision_model": settings.vision_model or None}


@app.post("/extract")
async def extract(image: UploadFile = File(...)):
    data = await image.read()
    try:
        return extract_exercises(llm(), data, image.content_type or "")
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        del data


@app.post("/tutor/sessions")
def start_tutor(req: StartRequest):
    _purge()
    session, message = Tutor(llm()).start(req.enonce, req.degre, req.canton)
    TUTOR_SESSIONS[session.id] = session
    return {"session_id": session.id, "message": message, "plan_verified": session.plan.verified,
            "notion": session.plan.notion}


@app.post("/tutor/sessions/{session_id}/messages")
def tutor_message(session_id: str, req: MessageRequest):
    _purge()
    session = TUTOR_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "session inconnue ou expirée")
    message = Tutor(llm()).reply(session, req.text)
    return {"message": message, "solved": session.solved, "step_reached": session.reached + 1,
            "steps_total": len(session.plan.etapes), "hint_level": session.hint_level}


@app.post("/copilot")
def start_copilot(req: StartRequest):
    _purge()
    sheet = copilot_mod.build_sheet(llm(), req.enonce, req.degre, req.canton)
    sid = uuid.uuid4().hex
    COPILOT_SESSIONS[sid] = (sheet, req.enonce, time.time())
    return {"session_id": sid, "notion": sheet.notion, "objectif_per": sheet.objectif_per,
            "attendus": sheet.attendus, "prerequis": sheet.prerequis,
            "deroule": sheet.deroule, "pieges": sheet.pieges, "questions": sheet.questions,
            "solution": sheet.solution(), "plan_verified": sheet.plan.verified, "markdown": sheet.markdown()}


@app.post("/copilot/{session_id}/messages")
def copilot_message(session_id: str, req: MessageRequest):
    _purge()
    entry = COPILOT_SESSIONS.get(session_id)
    if not entry:
        raise HTTPException(404, "session inconnue ou expirée")
    sheet, enonce, _ = entry
    COPILOT_SESSIONS[session_id] = (sheet, enonce, time.time())
    return {"message": copilot_mod.follow_up(llm(), sheet, enonce, req.text)}
