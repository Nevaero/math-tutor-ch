"""Appels à l'exécuteur isolé (`sandbox_runner.py`) dans un sous-processus.

PoC : isolation par sous-processus `python -I`, dossier temporaire, environnement vide,
timeout, AST + builtins restreints. En production : conteneur gVisor/Firecracker sans réseau,
limites mémoire/CPU (voir specs/07-sandbox-calcul.md).
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import settings
from .sandbox_runner import check_code

RUNNER = Path(__file__).with_name("sandbox_runner.py")


class SandboxError(RuntimeError):
    pass


class SandboxTimeout(SandboxError):
    pass


def run_jobs(jobs: list[dict], timeout: float | None = None) -> list[dict]:
    for job in jobs:
        if job["op"] == "exec":
            check_code(job["code"])  # refus rapide, re-vérifié dans le sous-processus
    env = {"PYTHONIOENCODING": "utf-8"}
    if os.name == "nt":
        env["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(RUNNER)],
                input=json.dumps({"jobs": jobs}),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout or settings.sandbox_timeout_s,
                cwd=tmp,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxTimeout("délai de calcul dépassé") from exc
    if proc.returncode != 0:
        raise SandboxError(proc.stderr[-500:])
    return json.loads(proc.stdout)


def exec_code(code: str, timeout: float | None = None) -> dict:
    return run_jobs([{"op": "exec", "code": code}], timeout)[0]


def analyze(candidates: list[str], targets: list[str], domain: str = "reels") -> list[dict]:
    """Pour chaque candidat : équivalence et complexité relative vis-à-vis de chaque cible.
    `domain` : « reels » ou « positifs » (longueurs, durées…)."""
    if not candidates:
        return []
    job = {"op": "analyze", "candidates": candidates, "targets": targets, "domain": domain}
    res = run_jobs([job])[0]
    if not res.get("ok"):
        raise SandboxError(res.get("error", "erreur inconnue"))
    return res["results"]
