"""Lecture d'énoncé depuis une photo. L'image reste en mémoire et n'est jamais écrite sur disque
ni journalisée (specs/08-donnees-conformite.md §8.5)."""

import base64

from .config import settings
from .llm import ChatProvider, extract_json
from .prompts import load_prompt

MAX_BYTES = 8 * 1024 * 1024
MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


def extract_exercises(llm: ChatProvider, image: bytes, mime: str) -> dict:
    if mime not in MIME_TYPES:
        raise ValueError(f"format non supporté : {mime}")
    if len(image) > MAX_BYTES:
        raise ValueError("image trop lourde")
    if not settings.vision_model:
        raise RuntimeError("LEO_VISION_MODEL non configuré (voir python -m leo.models)")
    data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
    messages = [{"role": "user", "content": [
        {"type": "text", "text": load_prompt("extract")},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}]
    try:
        raw = llm.chat(messages, model=settings.vision_model, temperature=0, max_tokens=2000)
    finally:
        del data_url, messages  # purge explicite des références à l'image
    return extract_json(raw)
