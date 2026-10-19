"""Recherche hybride dans le PER : BM25 (lexical) + embeddings (vectoriel), fusion RRF.

    python -m leo.curriculum.search --embed                        # calcule les embeddings (API)
    python -m leo.curriculum.search "résoudre 3x + 5 = 2x - 7" --degre 10H

PoC en mémoire (numpy). Cible production : PostgreSQL pgvector + BM25 (specs/06 §6.6).
Sans embeddings (pas de clé API ou index non calculé), la recherche se limite à BM25.
"""

import argparse
import json
import logging
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import numpy as np
import snowballstemmer

from ..config import settings

log = logging.getLogger(__name__)

DATA = Path(__file__).resolve().parents[2] / "data"
CHUNKS = DATA / "per_chunks.jsonl"
VECTORS = DATA / "per_embeddings.npy"
RRF_K = 60

STOPWORDS = set("""au aux avec ce ces dans de des du elle en et eux il je la le les leur lui ma mais me même
mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos
votre vous c d j l à m n s t y été être avoir a est sont ainsi etc notamment cf""".split())
_stemmer = snowballstemmer.stemmer("french")


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    words = re.findall(r"[a-z]+|\d+", text)
    return _stemmer.stemWords([w for w in words if w not in STOPWORDS and (len(w) > 1 or w.isdigit())])


@dataclass
class Hit:
    chunk: dict
    score: float
    bm25_rank: int | None
    vector_rank: int | None

    def render(self) -> str:
        c = self.chunk
        return f"[{c['objectif']} · {c['sous_champ'] or c['champ'].capitalize()} · {c['type']}] {c['text']}"


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tfs = [Counter(d) for d in docs]
        self.lens = np.array([len(d) for d in docs], dtype=float)
        self.avg = self.lens.mean() if len(docs) else 0.0
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tfs))
        for i, tf in enumerate(self.tfs):
            norm = self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg)
            out[i] = sum(self.idf[t] * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in query if t in tf)
        return out


def _indexed_text(c: dict) -> str:
    ctx = " · ".join(p for p in [f"{c['source']} cycle {c['cycle']}", c["objectif"],
                                 c["champ"].capitalize(), c["sous_champ"], c["type"]] if p)
    return f"{ctx}\n{c['text']}"


def _embed(texts: list[str], batch: int = 64) -> np.ndarray:
    from openai import OpenAI

    client = OpenAI(base_url=settings.base_url, api_key=settings.infomaniak_api_token)
    vecs = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=settings.embedding_model, input=texts[i:i + batch])
        vecs += [d.embedding for d in resp.data]
    arr = np.array(vecs, dtype=np.float32)
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


class CurriculumIndex:
    def __init__(self, chunks: list[dict], vectors: np.ndarray | None = None):
        self.chunks = chunks
        self.bm25 = BM25([tokenize(_indexed_text(c)) for c in chunks])
        self.vectors = vectors if vectors is not None and len(vectors) == len(chunks) else None

    @classmethod
    def load(cls) -> "CurriculumIndex | None":
        if not CHUNKS.exists():
            return None
        chunks = [json.loads(line) for line in CHUNKS.open(encoding="utf-8")]
        vectors = np.load(VECTORS) if VECTORS.exists() else None
        return cls(chunks, vectors)

    def _mask(self, degre: str | None, discipline: str | None, types: tuple[str, ...] | None,
              options: bool) -> np.ndarray:
        return np.array([
            (options or not c["objectif"].startswith("MEP"))
            and (not degre or degre in c["degres"])
            and (not discipline or c["discipline"] == discipline)
            and (not types or c["type"] in types)
            for c in self.chunks
        ])

    def search(self, query: str, *, degre: str | None = None, discipline: str | None = "maths",
               types: tuple[str, ...] | None = None, k: int = 5, depth: int = 50,
               use_bm25: bool = True, use_vectors: bool = True, options: bool = False) -> list[Hit]:
        """`options` : inclure l'option spécifique VD Maths et Physique (MEP), selon le profil."""
        mask = self._mask(degre, discipline, types, options)
        ranked: dict[str, list[int]] = {}
        if use_bm25:
            bm = np.where(mask, self.bm25.scores(tokenize(query)), -np.inf)
            ranked["bm25"] = [int(i) for i in np.argsort(-bm)[:depth] if bm[i] > 0]
        if use_vectors and self.vectors is not None and settings.embedding_model:
            try:
                q = _embed([query])[0]
                sim = np.where(mask, self.vectors @ q, -np.inf)
                ranked["vector"] = [int(i) for i in np.argsort(-sim)[:depth]]
            except Exception:
                log.exception("embeddings indisponibles, BM25 seul")
        fused: Counter = Counter()
        for ranks in ranked.values():
            for r, i in enumerate(ranks):
                fused[i] += 1 / (RRF_K + r + 1)
        pos = {name: {i: r + 1 for r, i in enumerate(ranks)} for name, ranks in ranked.items()}
        return [Hit(self.chunks[i], s, pos.get("bm25", {}).get(i), pos.get("vector", {}).get(i))
                for i, s in fused.most_common(k)]


@cache
def index() -> CurriculumIndex | None:
    idx = CurriculumIndex.load()
    if idx is None:
        log.warning("index PER absent : lancer python -m leo.curriculum.ingest ../per/math")
    return idx


def context_for(query: str, degre: str, k: int = 4, options: bool = False) -> str:
    """Extraits du PER à injecter dans un prompt (vide si l'index n'existe pas)."""
    idx = index()
    if idx is None:
        return ""
    hits = idx.search(query, degre=degre, types=("progression", "attente", "indication"), k=k, options=options)
    return "\n".join(f"- {h.render()}" for h in hits)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?")
    parser.add_argument("--degre")
    parser.add_argument("--discipline", default="maths")
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--embed", action="store_true", help="calcule les embeddings de l'index")
    args = parser.parse_args()
    if args.embed:
        chunks = [json.loads(line) for line in CHUNKS.open(encoding="utf-8")]
        vecs = _embed([_indexed_text(c) for c in chunks])
        np.save(VECTORS, vecs)
        print(f"{len(vecs)} embeddings ({vecs.shape[1]} dim) -> {VECTORS}")
        return
    for h in CurriculumIndex.load().search(args.query, degre=args.degre, discipline=args.discipline, k=args.k):
        print(f"{h.score:.4f} (bm25 #{h.bm25_rank}, vect #{h.vector_rank}) {h.render()[:220]}\n")


if __name__ == "__main__":
    main()
