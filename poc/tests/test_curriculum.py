from pathlib import Path

import pytest

from leo.curriculum.search import CurriculumIndex, tokenize

PER_DIR = Path(__file__).resolve().parents[2] / "per" / "math"


def chunk(i, objectif, sous_champ, text, degres=("9H", "10H", "11H"), type_="progression"):
    return {"id": str(i), "source": "PER", "cycle": 3, "page": 1, "objectif": objectif, "champ": "",
            "sous_champ": sous_champ, "type": type_, "degres": list(degres), "discipline": "maths",
            "text": text, "liens": []}


CHUNKS = [
    chunk(0, "MSN 33", "Algèbre – Équations", "Résolution d'équations du premier degré à une inconnue",
          degres=("10H", "11H")),
    chunk(1, "MSN 34", "Calcul de grandeurs", "Utilisation du théorème de Pythagore"),
    chunk(2, "MSN 33", "Algèbre – Calcul littéral", "Factorisation à l'aide des identités remarquables",
          degres=("11H",)),
    chunk(3, "MEP 32", "Nombres", "Trigonométrie dans le triangle rectangle et Pythagore"),
]


def test_tokenize_strips_accents_and_stems():
    assert tokenize("Les équations résolues") == tokenize("equation resolue")
    assert "le" not in tokenize("le théorème")


def test_bm25_ranks_and_filters_by_degree():
    idx = CurriculumIndex(CHUNKS)
    assert idx.search("résoudre une équation", degre="10H", k=1)[0].chunk["id"] == "0"
    # la factorisation n'est au programme qu'à partir de la 11H dans ce jeu
    assert all(h.chunk["id"] != "2" for h in idx.search("factoriser identités remarquables", degre="9H"))


def test_vd_option_excluded_unless_requested():
    idx = CurriculumIndex(CHUNKS)
    assert {h.chunk["objectif"] for h in idx.search("Pythagore")} == {"MSN 34"}
    assert "MEP 32" in {h.chunk["objectif"] for h in idx.search("Pythagore", options=True)}


@pytest.mark.skipif(not (PER_DIR / "276.pdf").exists(), reason="PDF du PER absent")
def test_ingest_cycle3_reads_columns():
    from leo.curriculum.ingest import ingest_pdf

    chunks = ingest_pdf(PER_DIR / "276.pdf")
    eq = [c for c in chunks if c.sous_champ == "Algèbre – Équations" and "système d’équations" in c.text]
    assert eq and all(c.objectif == "MSN 33" for c in eq)
    # le système d'équations commence en 11H (colonne de droite)
    assert "[dès 11H] Résolution d’un système" in "\n".join(c.text for c in eq)
    assert any(c.type == "attente" for c in chunks) and any(c.type == "indication" for c in chunks)
