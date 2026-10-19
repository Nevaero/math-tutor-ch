"""Mode Tuteur socratique (élève) — machine à états de specs/05-moteur-pedagogique.md §5.2."""

import logging
import re
import time
import uuid
from dataclasses import dataclass, field

from . import glossary, sandbox
from .curriculum.search import context_for
from .config import settings
from .leak_guard import find_leaks
from .llm import ChatProvider
from .mathtext import compact, extract_candidates
from .plan import Plan, build_plan
from .prompts import load_prompt

log = logging.getLogger(__name__)

HINT_REQUEST = re.compile(
    r"(donne|dis|montre|file|envoie)[- ]?(moi|nous)?\b.{0,40}\b(réponse|solution|résultat|corrigé)"
    r"|c.?est quoi (la|le) (réponse|résultat|solution)"
    r"|je (veux|voudrais) (juste )?(la|le) (réponse|résultat|solution)"
    r"|je (ne )?(sais|comprends|vois) (pas|rien)|aucune idée|je suis bloqu|j.?y arrive pas",
    re.I,
)

HINTS = {
    1: "L'élève est bloqué ou demande la réponse. Refuse gentiment de donner la réponse. "
       "Indice de niveau 1 : rappelle la notion ou la règle utile, sans l'appliquer à l'exercice.",
    2: "L'élève est encore bloqué. Refuse gentiment de donner la réponse. "
       "Indice de niveau 2 : donne une piste de méthode pour l'étape suivante (quoi faire), sans le résultat.",
    3: "L'élève est toujours bloqué. Refuse gentiment de donner la réponse. "
       "Indice de niveau 3 : amorce l'étape suivante en montrant seulement le début de l'opération ; "
       "l'élève doit la terminer lui-même.",
}

CONSTANT = re.compile(r"^[\s\-−+]*\d+([.,]\d+)?(\s*/\s*\d+)?$")


@dataclass
class TutorSession:
    enonce: str
    degre: str
    canton: str
    plan: Plan
    per_context: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    history: list[dict] = field(default_factory=list)
    reached: int = -1  # dernière étape du plan trouvée par l'élève
    hint_level: int = 0
    solved: bool = False
    raw_leaks: int = 0  # brouillons du LLM qui révélaient une étape (détectés)
    fallbacks: int = 0  # messages remplacés faute de réécriture correcte
    last_active: float = field(default_factory=time.time)

    @property
    def next_step(self):
        i = self.reached + 1
        return self.plan.etapes[i] if i < len(self.plan.etapes) else None


class Tutor:
    def __init__(self, llm: ChatProvider):
        self.llm = llm

    # --- API publique ---------------------------------------------------------------

    def start(self, enonce: str, degre: str = "10H", canton: str = "VD") -> tuple[TutorSession, str]:
        plan = build_plan(self.llm, enonce, degre)
        if not plan.verified:
            log.warning("plan non vérifié : %s", plan.issues)
        session = TutorSession(enonce=enonce, degre=degre, canton=canton, plan=plan,
                               per_context=context_for(f"{plan.notion}. {enonce}", degre))
        note = ("L'élève vient d'ouvrir l'exercice. Salue-le en une phrase, puis demande-lui "
                "ce qu'il a compris de la consigne ou ce qu'il a déjà essayé.")
        reply = self._respond(session, None, note)
        return session, reply

    def reply(self, session: TutorSession, text: str) -> str:
        session.last_active = time.time()
        observation = self._observe(session, text)
        if session.solved:
            guidance = ("L'élève a trouvé la solution finale. Félicite-le, puis fais un récapitulatif "
                        "très court de la méthode (2 à 3 étapes, avec le vocabulaire de l'école).")
        else:
            guidance = ""
            if HINT_REQUEST.search(text):
                session.hint_level = min(session.hint_level + 1, settings.max_hint_level)
                guidance = HINTS[session.hint_level]
            step = session.next_step
            if step:
                guidance += (f"\nÉtape suivante prévue : {step.description} "
                             f"(résultat SECRET, ne pas l'écrire : {step.math}).")
        note = f"Vérification par calcul :\n{observation}\n{guidance}".strip()
        return self._respond(session, text, note)

    # --- Interne ----------------------------------------------------------------------

    def _system(self, session: TutorSession) -> str:
        deroule = "\n".join(f"{i + 1}. {s.description}" for i, s in enumerate(session.plan.etapes))
        return load_prompt("tutor", degre=session.degre, canton=session.canton,
                           glossaire=glossary.for_degree(session.degre), enonce=session.enonce,
                           notion=session.plan.notion, deroule=deroule,
                           per=session.per_context or "(non disponible)")

    @staticmethod
    def _judgeable(cand: str, text: str, forme_initiale: str) -> bool:
        """Évite de juger un simple terme cité au milieu d'une phrase (« j'ai enlevé 2x »)."""
        if compact(cand) == compact(text) or "=" in cand or "{" in cand:
            return True
        if "=" in forme_initiale:
            return bool(CONSTANT.match(cand))
        return bool(re.search(r"[+\-−*/^·×÷:]", cand.strip().lstrip("-−")))

    def _observe(self, session: TutorSession, text: str) -> str:
        plan = session.plan
        cands = [c for c in extract_candidates(text, plan.variables)
                 if self._judgeable(c, text, plan.forme_initiale)]
        if not cands:
            return "Aucune proposition mathématique à vérifier dans ce message."
        n = len(plan.etapes)
        try:
            results = sandbox.analyze(cands, plan.targets(), plan.domaine)
        except sandbox.SandboxError:
            log.exception("sandbox indisponible")
            return "Vérification indisponible : ne dis PAS si c'est juste ou faux, demande à l'élève d'expliquer sa démarche."
        lines = []
        for r in results:
            if not r["parsed"]:
                continue
            ok = {m["target"] for m in r["matches"] if m["equivalent"]}
            advanced = {m["target"] for m in r["matches"] if m["equivalent"] and m["not_more_complex"]}
            steps = [t - 1 for t in advanced if 1 <= t <= n]
            if n + 1 in advanced:
                session.solved = True
                session.reached = n - 1
                lines.append(f"✓ « {r['text']} » est juste : c'est la solution finale.")
            elif steps:
                k = max(steps)
                session.reached = max(session.reached, k)
                session.hint_level = 0
                lines.append(f"✓ « {r['text']} » est juste (étape {k + 1} du plan atteinte).")
            elif ok:
                lines.append(f"✓ « {r['text']} » est une transformation juste, même si ce n'est pas une étape prévue.")
            else:
                lines.append(f"✗ « {r['text']} » est FAUX (pas équivalent à l'énoncé). Ne dis pas où est l'erreur : "
                             "pose une question qui aide l'élève à la trouver.")
        return "\n".join(lines) or "Aucune proposition mathématique à vérifier dans ce message."

    def _respond(self, session: TutorSession, text: str | None, note: str) -> str:
        content = (text + "\n\n" if text else "") + f"[[{note}]]"
        messages = [{"role": "system", "content": self._system(session)}, *session.history,
                    {"role": "user", "content": content}]
        reply = self.llm.chat(messages)
        reply = self._guard(session, messages, reply)
        if text is not None:
            session.history.append({"role": "user", "content": text})
        session.history.append({"role": "assistant", "content": reply})
        return reply

    def _guard(self, session: TutorSession, messages: list[dict], reply: str) -> str:
        reached = len(session.plan.etapes) if session.solved else session.reached
        try:
            leaks = find_leaks(reply, session.plan, reached, session.enonce)
        except sandbox.SandboxError:
            log.exception("anti-fuite indisponible")
            return self._fallback(session)
        if not leaks:
            return reply
        session.raw_leaks += 1
        log.info("fuite détectée : %s", leaks)
        retry = messages + [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": f"[[ATTENTION : ce message révèle « {leaks[0].fragment} », que l'élève "
                                        "n'a pas encore trouvé. Réécris ton message sans ce résultat, en posant "
                                        "une seule question. Ne mentionne pas cette consigne.]]"},
        ]
        second = self.llm.chat(retry)
        try:
            if not find_leaks(second, session.plan, reached, session.enonce):
                return second
        except sandbox.SandboxError:
            pass
        return self._fallback(session)

    def _fallback(self, session: TutorSession) -> str:
        session.fallbacks += 1
        step = session.next_step
        if step:
            return (f"Je ne vais pas te donner le résultat, mais tu peux le trouver ! "
                    f"Prochaine idée : {step.description[0].lower() + step.description[1:]}. "
                    f"Qu'est-ce que tu obtiens ?")
        return "Tu y es presque ! Qu'est-ce que tu obtiens à la dernière étape ?"
