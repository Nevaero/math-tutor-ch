from functools import cache
from pathlib import Path

import yaml


@cache
def _entries() -> list[dict]:
    return yaml.safe_load(Path(__file__).with_name("glossaire.yaml").read_text(encoding="utf-8"))


def for_degree(degre: str) -> str:
    """Résumé du glossaire pour un degré, à injecter dans les prompts."""
    parts = []
    for e in _entries():
        if degre in e["degres"] or not degre.endswith("H"):
            avoid = f" (et non « {' », « '.join(e['eviter'])} »)" if e["eviter"] else ""
            parts.append(f"« {e['terme']} »{avoid} = {e['sens']}")
    return "; ".join(parts)
