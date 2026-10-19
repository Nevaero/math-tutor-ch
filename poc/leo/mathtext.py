"""Repérage des fragments mathématiques dans un texte libre (message élève ou tuteur)."""

import re

from .sandbox_runner import normalize

_LETTER = "A-Za-zÀ-ÿ"
_LATEX = re.compile(r"\$\$?(.+?)\$\$?|\\\((.+?)\\\)|\\\[(.+?)\\\]", re.S)


def variables_of(math: str) -> list[str]:
    """Variables à une lettre présentes dans une expression (ex. « 3x + 5 = 2x - 7 » -> ['x'])."""
    plain = re.sub(r"sqrt|pi|sin|cos|tan|ln|log|exp", " ", normalize(math))
    return sorted(set(re.findall(rf"(?<![{_LETTER}])[a-z](?![{_LETTER}])", plain)))


def extract_candidates(text: str, variables: list[str]) -> list[str]:
    """Fragments susceptibles d'être des expressions, équations ou ensembles.

    Seules les lettres isolées correspondant aux variables du problème sont acceptées,
    pour ne pas confondre « a » (verbe avoir) ou « y » avec une inconnue.
    """
    candidates = [next(g for g in m.groups() if g) for m in _LATEX.finditer(text)]
    plain = _LATEX.sub(" ", text)
    var_class = "[" + "".join(variables) + "]" if variables else "(?!)"
    var = rf"(?<![{_LETTER}]){var_class}(?![{_LETTER}])"
    token = rf"(?:\d+(?:[.,]\d+)?|{var}|sqrt|π|√|[+\-−*/^()=·×÷²³{{}};:]|[ \t])"
    for m in re.finditer(rf"(?:{token})+", plain):
        frag = m.group(0).strip(" \t,;:=")
        if not frag or not re.search(rf"\d|{var}", frag):
            continue
        candidates.append(frag)
    seen, out = set(), []
    for c in candidates:
        c = c.strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def compact(s: str) -> str:
    return re.sub(r"\s+", "", normalize(s))
