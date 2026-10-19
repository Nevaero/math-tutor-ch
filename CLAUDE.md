# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

- `SPECS.md` — original product brief (source document, not to be rewritten).
- `specs/` — detailed specifications in French; `specs/README.md` lists validated decisions and `specs/12-questions-ouvertes.md` tracks open questions. When the user answers a question or changes a decision, update the relevant spec files **and** the decision tables in `specs/README.md` and `specs/12-questions-ouvertes.md`.
- `poc/` — Phase 0 Python backend proof of concept for "Leo" (maths tutor). No Flutter app yet; `poc/leo/api.py` is the HTTP contract the future app will consume.
- `per/` — Plan d'études romand PDFs (© CIIP). Git-ignored: never commit them or anything derived from them (`poc/data/`).

Product context: Swiss-romand homework tutor (GE and VD first), Socratic "Tuteur" mode for students and "Copilote" mode for parents, strict Swiss data sovereignty (Infomaniak only), no PII in pedagogical data. User-facing text, prompts, comments and specs are written in French.

## Commands (run from `poc/`)

```bash
.venv/Scripts/python -m pip install -r requirements.txt   # Windows venv (bin/ on macOS/Linux)
.venv/Scripts/python -m pytest -q                          # all tests (no API needed: FakeProvider)
.venv/Scripts/python -m pytest tests/test_tutor.py::test_session_flow_with_leak_retry_and_solution -q

python -m leo.models                              # list models on the Infomaniak AI product
python -m leo.curriculum.ingest ../per/math       # PER PDFs -> data/per_chunks.jsonl
python -m leo.curriculum.search --embed           # compute embeddings (needs LEO_EMBEDDING_MODEL)
python -m eval.run_retrieval                      # recall@5 / MRR: BM25 vs vector vs hybrid
python -m eval.run_eval --model <model-id>        # model benchmark (plan accuracy, leaks, cost, latency)
python -m leo.cli "Résous 3x + 5 = 2x - 7" --degre 10H --debug    # interactive tutor (--copilote, --photo)
uvicorn leo.api:app --reload
```

Config comes from `poc/.env` (see `.env.example`), all variables prefixed `LEO_` (`leo/config.py`). The Infomaniak API is OpenAI-compatible: base URL `https://api.infomaniak.com/2/ai/{product_id}/openai/v1`. Tests that spawn the sandbox take ~1.5 s each (SymPy import in a subprocess); the full suite takes ~45 s.

## Architecture (poc/leo)

The core design principle: **the LLM never decides mathematical truth**. Correctness is decided deterministically by SymPy in a sandbox, orchestrated by Python — not via LLM tool calling (deliberately, since open-weight models' tool calling is unreliable).

- **Sandbox** — `sandbox.py` runs `sandbox_runner.py` in a `python -I` subprocess (temp cwd, empty env, timeout). The runner must only import stdlib + SymPy (it cannot import `leo`). Two ops: `exec` (LLM-generated SymPy code, AST-checked + restricted builtins, result in variable `result`) and `analyze` (for each candidate string: equivalence and "not more complex" vs each target). `sandbox_runner.normalize` converts Swiss school notation (decimal comma, `·`, `:`, `²`, `√`, LaTeX, sets with `;`). Equations compare by solution set over a `domain` (`reels` or `positifs` for lengths).
- **Plan** — `plan.py` asks the LLM for a JSON plan (`forme_initiale`, `etapes[].math`, `solution_finale`, `code_sympy`, `domaine`), then verifies every step is equivalent to the initial form and that the SymPy result matches; one retry with the failures fed back. `Plan.targets()` = `[forme_initiale, *steps, solution_finale]` — index arithmetic elsewhere depends on this order.
- **Progress & leaks use the same rule**: a fragment "reaches" step *i* if it is equivalent to it **and** not more complex (`count_ops`). This is why restating the exercise is not a leak but `x = -12` is. `mathtext.extract_candidates` pulls math fragments from free text, accepting only single-letter variables that appear in the plan (so French "a"/"y" aren't parsed as unknowns).
- **Tutor turn** (`tutor.py`): analyze student message → internal note `[[...]]` appended to the latest user message only (never stored in history) with verification results, hint level (1–3, triggered by `HINT_REQUEST` regex) and the secret next step → LLM reply → `leak_guard.find_leaks` → one rewrite attempt → generic fallback. `session.reached` is the index of the last step found (−1 = none; `n-1` when solved).
- **Copilot** (`copilot.py`): plan + PER context → JSON sheet; the solution section is built from the verified plan, not from LLM text.
- **Prompts** live in `leo/prompts/*.md` and use `string.Template` `$vars` (not `{}`, because of LaTeX).
- **PER RAG** (`leo/curriculum/`): `ingest.py` parses PER PDFs with PyMuPDF using page geometry — on "Progression des apprentissages" pages the block's x-position gives the **starting** school year (columns 9e/10e/11e; only the start is reliable, hence "dès 10H" labels); on "Attentes fondamentales" pages the left column is attentes, the right is indications. `search.py` does BM25 (accent-stripped, French Snowball stemming) + optional embeddings, fused with RRF (k=60), filtered by degree/discipline; VD option objectives (`MEP …`) are excluded unless `options=True`. Without `data/per_chunks.jsonl` the context is simply empty, so tests don't depend on the PDFs (except one `skipif` test).
- **LLM providers** (`llm.py`): `InfomaniakProvider` (OpenAI SDK, tracks tokens/latency for cost estimates, strips `<think>` blocks) and `FakeProvider` (scripted replies, used by all tests — the reply order must match the call order: plan, opening, then one call per turn plus one per leak rewrite).
