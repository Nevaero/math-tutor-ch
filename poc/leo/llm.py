"""Fournisseurs LLM. Interface minimale `chat(messages) -> str` pour pouvoir changer de modèle
(API Infomaniak, GPU auto-hébergé, faux fournisseur pour les tests)."""

import json
import re
import time
from dataclasses import dataclass, field
from typing import Protocol

from .config import settings


@dataclass
class Usage:
    calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    latencies_s: list[float] = field(default_factory=list)

    def cost_chf(self) -> float:
        return (self.tokens_in * settings.price_in_per_mtok
                + self.tokens_out * settings.price_out_per_mtok) / 1_000_000


class ChatProvider(Protocol):
    usage: Usage

    def chat(self, messages: list[dict], *, temperature: float = 0.3,
             max_tokens: int = 1200, model: str | None = None) -> str: ...


_THINK = re.compile(r"<think>.*?</think>", re.S)


def clean(text: str) -> str:
    """Retire les blocs de raisonnement de certains modèles (Qwen3, DeepSeek…)."""
    return _THINK.sub("", text or "").strip()


class InfomaniakProvider:
    def __init__(self, model: str | None = None):
        from openai import OpenAI

        if not settings.infomaniak_api_token or not settings.infomaniak_product_id:
            raise RuntimeError("LEO_INFOMANIAK_API_TOKEN et LEO_INFOMANIAK_PRODUCT_ID requis (voir .env.example)")
        self.client = OpenAI(base_url=settings.base_url, api_key=settings.infomaniak_api_token)
        self.model = model or settings.chat_model
        self.usage = Usage()

    def chat(self, messages, *, temperature=0.3, max_tokens=1200, model=None):
        start = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=model or self.model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        self.usage.calls += 1
        self.usage.latencies_s.append(time.perf_counter() - start)
        if resp.usage:
            self.usage.tokens_in += resp.usage.prompt_tokens
            self.usage.tokens_out += resp.usage.completion_tokens
        return clean(resp.choices[0].message.content)


class FakeProvider:
    """Renvoie des réponses scriptées, dans l'ordre. Pour les tests."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls: list[list[dict]] = []
        self.usage = Usage()

    def chat(self, messages, *, temperature=0.3, max_tokens=1200, model=None):
        self.calls.append(messages)
        self.usage.calls += 1
        return clean(self.replies.pop(0))


def extract_json(text: str) -> dict:
    """Extrait le premier objet JSON d'une réponse (tolère ```json et texte autour)."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"pas de JSON dans la réponse : {text[:200]}")
    return json.loads(text[start:end + 1])
