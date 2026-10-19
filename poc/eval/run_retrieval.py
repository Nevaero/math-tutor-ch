"""Compare BM25 seul, vectoriel seul et hybride (RRF) sur eval/retrieval.yaml.

    python -m eval.run_retrieval
"""

from pathlib import Path

import yaml

from leo.config import settings
from leo.curriculum.search import CurriculumIndex

HERE = Path(__file__).parent
K = 5


def relevant(chunk: dict, case: dict) -> bool:
    hay = f"{chunk['sous_champ']} {chunk['text']}".lower()
    return chunk["objectif"] == case["objectif"] and any(t.lower() in hay for t in case["termes"])


def main() -> None:
    cases = yaml.safe_load((HERE / "retrieval.yaml").read_text(encoding="utf-8"))
    idx = CurriculumIndex.load()
    modes = {"bm25": dict(use_bm25=True, use_vectors=False)}
    if idx.vectors is not None and settings.embedding_model:
        modes |= {"vectoriel": dict(use_bm25=False, use_vectors=True),
                  "hybride": dict(use_bm25=True, use_vectors=True)}
    else:
        print("(embeddings absents : BM25 seul — lancer python -m leo.curriculum.search --embed)\n")
    for name, opts in modes.items():
        hits_at_k, rr = 0, 0.0
        misses = []
        for case in cases:
            hits = idx.search(case["q"], degre=case["degre"], k=K, depth=100, **opts)
            rank = next((r + 1 for r, h in enumerate(hits) if relevant(h.chunk, case)), None)
            hits_at_k += rank is not None
            rr += 1 / rank if rank else 0
            if not rank:
                misses.append(case["q"][:60])
        n = len(cases)
        print(f"{name:10s} recall@{K} = {hits_at_k}/{n} ({hits_at_k / n:.0%})   MRR = {rr / n:.2f}")
        for m in misses:
            print(f"   ✗ {m}")


if __name__ == "__main__":
    main()
