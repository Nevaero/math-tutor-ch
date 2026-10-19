"""Discuter avec Leo dans le terminal.

    python -m leo.cli "Résous l'équation 3x + 5 = 2x - 7" --degre 10H
    python -m leo.cli "Réduis 3(x+2) - 2(x-1)" --copilote
    python -m leo.cli --photo exercice.jpg
"""

import argparse
import logging
import mimetypes
from pathlib import Path

from . import copilot
from .extraction import extract_exercises
from .llm import InfomaniakProvider
from .tutor import Tutor


def main() -> None:
    parser = argparse.ArgumentParser(description="PoC Leo")
    parser.add_argument("enonce", nargs="?", help="énoncé de l'exercice")
    parser.add_argument("--photo", type=Path, help="photo de l'exercice (au lieu de l'énoncé)")
    parser.add_argument("--degre", default="10H")
    parser.add_argument("--canton", default="VD", choices=["GE", "VD"])
    parser.add_argument("--copilote", action="store_true", help="mode Copilote Parent")
    parser.add_argument("--debug", action="store_true", help="affiche le plan et l'état de session")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.debug else logging.WARNING)

    llm = InfomaniakProvider()
    enonce = args.enonce
    if args.photo:
        mime = mimetypes.guess_type(args.photo.name)[0] or "image/jpeg"
        data = extract_exercises(llm, args.photo.read_bytes(), mime)
        exercices = data.get("exercices", [])
        if not data.get("lisible", True) or not exercices:
            print("Photo illisible :", data.get("remarque"))
            return
        for i, ex in enumerate(exercices):
            print(f"[{i}] {ex['id']} — {ex['enonce']}")
        choice = int(input("Quel exercice ? ") or 0) if len(exercices) > 1 else 0
        enonce = exercices[choice]["enonce"]
        enonce = input(f"Énoncé reconnu (Entrée pour valider, ou corrige) :\n{enonce}\n> ") or enonce
    if not enonce:
        parser.error("énoncé ou --photo requis")

    if args.copilote:
        sheet = copilot.build_sheet(llm, enonce, args.degre, args.canton)
        print(sheet.markdown())
        while (q := input("\nVotre question (vide pour quitter) > ").strip()):
            print("\nLeo :", copilot.follow_up(llm, sheet, enonce, q))
    else:
        tutor = Tutor(llm)
        session, opening = tutor.start(enonce, args.degre, args.canton)
        if args.debug:
            p = session.plan
            print(f"[plan vérifié={p.verified}] {p.forme_initiale} -> "
                  + " -> ".join(s.math for s in p.etapes) + f" | {p.issues}")
        print("\nLeo :", opening)
        while not session.solved and (text := input("\nToi > ").strip()):
            print("\nLeo :", tutor.reply(session, text))
            if args.debug:
                print(f"[étape {session.reached + 1}/{len(session.plan.etapes)} · indice {session.hint_level} "
                      f"· fuites bloquées {session.raw_leaks} · replis {session.fallbacks}]")

    u = llm.usage
    print(f"\n— {u.calls} appels LLM, {u.tokens_in} tokens entrée, {u.tokens_out} sortie, ≈ {u.cost_chf():.4f} CHF")


if __name__ == "__main__":
    main()
