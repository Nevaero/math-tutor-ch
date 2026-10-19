"""Découpe les PDF du PER en unités pédagogiques (chunks) pour la recherche hybride.

    python -m leo.curriculum.ingest ../per/math

Structure exploitée (PER v3, CIIP) — chaque objectif occupe des doubles pages :
- page « Progression des apprentissages » : la position horizontale d'un bloc indique l'année
  où l'apprentissage commence (colonnes 9e | 10e | 11e au cycle 3) ;
- page « Attentes fondamentales » : colonne gauche = attentes, colonne droite = indications
  pédagogiques ;
- en-tête de page : code(s) d'objectif (MSN 33 – 35, MEP 31 – MSN 35) + champ (FONCTIONS ET ALGÈBRE).

⚠ Droit de réutilisation du PER à obtenir de la CIIP avant tout usage hors PoC
(specs/08-donnees-conformite.md §8.5). L'index produit reste local (dossier data/, non versionné).
"""

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pymupdf

CONTENT_X0, CONTENT_X1 = 57.0, 553.0  # zone utile des pages de progression
BODY_Y0, BODY_Y1 = 150.0, 800.0
COLUMN_SPLIT_X = 290.0  # attentes | indications
CODE_RE = re.compile(r"\b(MSN|MEP)\s*(\d{2})")
SOURCES = {  # nom de fichier -> (libellé, cycle, degrés du cycle)
    "274": ("PER", 1, ["1H", "2H", "3H", "4H"]),
    "275": ("PER", 2, ["5H", "6H", "7H", "8H"]),
    "276": ("PER", 3, ["9H", "10H", "11H"]),
    "PER-Math-Physique_VD": ("PER VD OS Maths et Physique", 3, ["9H", "10H", "11H"]),
}
DISCIPLINES = {31: "maths", 32: "maths", 33: "maths", 34: "maths", 35: "maths", 36: "sciences",
               37: "sciences", 38: "sciences"}


@dataclass
class Chunk:
    id: str
    source: str
    cycle: int
    page: int
    objectif: str
    champ: str
    sous_champ: str
    type: str  # progression | attente | indication | commentaire
    degres: list[str]
    discipline: str
    text: str
    liens: list[str] = field(default_factory=list)

    def indexed_text(self) -> str:
        """Texte indexé et montré au LLM : contexte hiérarchique + contenu."""
        ctx = " · ".join(p for p in [f"{self.source} cycle {self.cycle}", self.objectif,
                                     self.champ.capitalize(), self.sous_champ, self.type] if p)
        return f"{ctx}\n{self.text}"


def clean(text: str) -> str:
    text = re.sub(r"[\x07\x08]", "", text)
    text = re.sub(r"[  \xa0\t]", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _header(blocks) -> tuple[str, str]:
    for x0, y0, x1, y1, txt, *_ in blocks:
        if y0 < 30 and (x0 < 45 or x0 > 540):
            lines = [ln.strip() for ln in txt.split("\n") if ln.strip()]
            m = CODE_RE.search(lines[0]) if lines else None
            if m:
                return f"{m.group(1)} {m.group(2)}", (lines[1] if len(lines) > 1 else "")
    return "", ""


def _year_columns(blocks, cycle_degrees: list[str]) -> list[str]:
    for _, y0, _, _, txt, *_ in blocks:
        years = re.findall(r"(\d+)e année", txt)
        if years and y0 < 160:
            return [f"{y}H" for y in years]
    return cycle_degrees


def _col(x: float, n: int) -> int:
    width = (CONTENT_X1 - CONTENT_X0) / n
    return max(0, min(n - 1, int((x - CONTENT_X0) // width)))


def _span(x0: float, x1: float, years: list[str]) -> list[str]:
    """Degrés concernés : de la colonne où le bloc commence jusqu'à la fin du cycle.
    (La largeur du bloc dépend de la longueur du texte, pas de la durée de l'apprentissage.)"""
    return years[_col(x0 + 1, len(years)):]


def _label(degrees: list[str]) -> str:
    return f"dès {degrees[0]}" if degrees else ""


def _body(blocks):
    return sorted((b for b in blocks if BODY_Y0 <= b[1] <= BODY_Y1 and b[4].strip()),
                  key=lambda b: (round(b[1]), b[0]))


def parse_progression(blocks, base: dict, years: list[str]) -> list[Chunk]:
    chunks, items = [], []
    sous_champ, liens = base.pop("sous_champ", ""), []
    body = [b for b in _body(blocks) if not re.match(r"(\d+e année\s*)+$", clean(b[4]))
            and "Progression des apprentissages" not in b[4]]
    for i, (x0, y0, x1, y1, txt, *_) in enumerate(body):
        t = clean(txt)
        nxt = clean(body[i + 1][4]) if i + 1 < len(body) else ""
        if t.startswith("Liens"):
            liens = CODE_RE.findall(t)
            continue
        is_title = (len(t) < 70 and not t.startswith("–") and (nxt.startswith("Liens") or t.isupper()))
        if is_title:
            if items:
                chunks.append((sous_champ, liens, items))
            sous_champ, liens, items = t.capitalize() if t.isupper() else t, [], []
            continue
        # suite d'une ligne coupée : même colonne, léger retrait (~10 pt), juste en dessous
        recent = [ln for it in items[-3:] for ln in it["lines"]]
        parent = next((ln for ln in reversed(recent)
                       if ln[2] + 5 < x0 < ln[2] + 16 and -2 <= y0 - ln[3] < 8), None)
        if parent and not t.startswith("–"):
            parent[1] += f" {t}"
            parent[3] = y1
        elif t.startswith("–") and items:
            items[-1]["lines"].append([_span(x0, x1, years), t, x0, y1])
        else:
            items.append({"lines": [[_span(x0, x1, years), t, x0, y1]]})
    if items:
        chunks.append((sous_champ, liens, items))

    out = []
    for sc, lk, its in chunks:
        for item in its:
            degrees = sorted({d for deg, *_ in item["lines"] for d in deg}, key=years.index)
            text = "\n".join(f"{'  ' if t.startswith('–') else ''}[{_label(deg)}] {t}"
                             for deg, t, *_ in item["lines"])
            out.append(Chunk(**base, sous_champ=sc, type="progression", degres=degrees, text=text,
                             liens=[f"{a} {b}" for a, b in lk], id=""))
    return out, sous_champ


def parse_attentes(blocks, base: dict, degrees: list[str]) -> list[Chunk]:
    base = {k: v for k, v in base.items() if k != "sous_champ"}
    attentes, indications = [], []
    for x0, y0, x1, y1, txt, *_ in _body(blocks):
        t = clean(txt)
        if t.startswith(("Au cours, mais au plus tard", "Attentes fondamentales", "Ressources, indices")):
            continue
        if x0 < COLUMN_SPLIT_X:
            if t.startswith("…") or not attentes:
                attentes.append([y1, t])
            else:
                attentes[-1][1] += " " + t
                attentes[-1][0] = y1
        else:
            if indications and y0 - indications[-1][0] < 6:
                indications[-1][1] += " " + t
                indications[-1][0] = y1
            else:
                indications.append([y1, t])
    out = [Chunk(**base, sous_champ="", type="attente", degres=degrees, text=f"[fin de cycle] {t}", id="")
           for _, t in attentes]
    out += [Chunk(**base, sous_champ="", type="indication", degres=degrees, text=t, id="")
            for _, t in indications if len(t) > 40]
    return out


def parse_commentaire(blocks, base: dict, degrees: list[str], max_len: int = 1200) -> list[Chunk]:
    base = {k: v for k, v in base.items() if k != "sous_champ"}
    texts = [clean(b[4]) for b in _body(blocks)]
    texts = [t for t in texts if len(t) > 30 and not re.search(r"\.{4,}|\s\d+$", t)]
    out, buf = [], ""
    for t in texts:
        if len(buf) + len(t) > max_len and buf:
            out.append(buf)
            buf = ""
        buf = f"{buf} {t}".strip()
    if buf:
        out.append(buf)
    return [Chunk(**base, sous_champ="", type="commentaire", degres=degrees, text=t, id="") for t in out]


def ingest_pdf(path: Path) -> list[Chunk]:
    label, cycle, cycle_degrees = SOURCES.get(path.stem, ("PER", 0, []))
    doc = pymupdf.open(path)
    chunks: list[Chunk] = []
    last_sous_champ = {}
    for pno, page in enumerate(doc):
        blocks = page.get_text("blocks")
        full = page.get_text()
        objectif, champ = _header(blocks)
        num = int(objectif.split()[1]) if objectif else 0
        base = dict(source=label, cycle=cycle, page=pno + 1, objectif=objectif, champ=champ,
                    discipline="maths" if objectif.startswith("MEP") else DISCIPLINES.get(num % 10 + 30, "maths"))
        if "Progression des apprentissages" in full and objectif:
            base["sous_champ"] = last_sous_champ.get(objectif, "")
            new, last = parse_progression(blocks, base, _year_columns(blocks, cycle_degrees))
            last_sous_champ[objectif] = last
            chunks += new
        elif "Attentes fondamentales" in full and objectif:
            chunks += parse_attentes(blocks, base, cycle_degrees)
        elif len(full) > 400:
            chunks += parse_commentaire(blocks, base, cycle_degrees)
    for i, c in enumerate(chunks):
        c.id = f"{path.stem}-p{c.page}-{i}"
    return chunks


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "../per/math")
    out = Path(__file__).resolve().parents[2] / "data" / "per_chunks.jsonl"
    out.parent.mkdir(exist_ok=True)
    total = 0
    with out.open("w", encoding="utf-8") as f:
        for pdf in sorted(src.glob("*.pdf")):
            chunks = ingest_pdf(pdf)
            total += len(chunks)
            print(f"{pdf.name}: {len(chunks)} chunks")
            for c in chunks:
                f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
    print(f"{total} chunks -> {out}")


if __name__ == "__main__":
    main()
