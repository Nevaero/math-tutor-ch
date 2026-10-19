from functools import cache
from pathlib import Path
from string import Template

_DIR = Path(__file__).parent


@cache
def _raw(name: str) -> str:
    return (_DIR / f"{name}.md").read_text(encoding="utf-8")


def load_prompt(name: str, **values: str) -> str:
    """Charge un prompt versionné ; variables au format $nom (pas d'accolades, à cause du LaTeX)."""
    return Template(_raw(name)).safe_substitute(**values)
