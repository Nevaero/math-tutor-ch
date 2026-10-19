# PoC Leo — tuteur de mathématiques (Phase 0)

Backend Python qui valide les risques principaux du MVP (specs/11-roadmap.md, Phase 0) :

| Risque | Ce que le PoC vérifie | Où |
| --- | --- | --- |
| Exactitude des calculs | Tout calcul passe par SymPy dans une sandbox ; chaque étape du plan est vérifiée par équivalence | `leo/sandbox*.py`, `leo/plan.py` |
| Fuite de solution | Un brouillon du tuteur qui révèle une étape non trouvée par l'élève est réécrit, sinon remplacé | `leo/leak_guard.py` |
| Qualité des modèles Infomaniak | Banc d'évaluation : plan juste, résistance aux demandes de réponse, coût, latence | `eval/run_eval.py` |
| Lecture de photos | Extraction d'énoncé par le modèle vision | `leo/extraction.py` |
| RAG sur le PER | Ingestion des PDF du PER, recherche hybride BM25 + embeddings, fusion RRF | `leo/curriculum/` |

Pas d'app Flutter à ce stade : l'API HTTP (`leo/api.py`) est le contrat que l'app consommera.

## Installation

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt      # Windows (bin/ sous macOS/Linux)
cp .env.example .env                                          # puis renseigner le jeton Infomaniak
```

## Commandes

```bash
python -m pytest -q                               # tests (sans API : faux LLM)
python -m leo.models                              # modèles disponibles sur le produit IA Infomaniak

python -m leo.curriculum.ingest ../per/math       # PDF du PER -> data/per_chunks.jsonl
python -m leo.curriculum.search --embed           # embeddings (LEO_EMBEDDING_MODEL)
python -m leo.curriculum.search "Factorise x^2-9" --degre 11H
python -m eval.run_retrieval                      # recall@5 / MRR : BM25 vs vectoriel vs hybride

python -m leo.cli "Résous 3x + 5 = 2x - 7" --degre 10H --debug       # mode Tuteur
python -m leo.cli "Réduis 3(x+2) - 2(x-1)" --copilote                 # mode Copilote
python -m leo.cli --photo eval/photos/ex1.jpg                         # depuis une photo

python -m eval.run_eval --model Qwen/Qwen3.5-122B-A10B-FP8           # banc d'évaluation d'un modèle
uvicorn leo.api:app --reload                                          # API (doc : /docs)
```

## Fonctionnement d'un tour de tuteur

1. **Plan interne** (au démarrage) : le LLM propose forme initiale, étapes, solution et code SymPy ; la sandbox
   exécute le code et vérifie que chaque étape est équivalente à l'énoncé. Une relance avec les erreurs si besoin.
2. **Analyse du message élève** : les fragments mathématiques sont extraits et comparés aux étapes du plan
   (équivalence + complexité : « x = -12 » est plus avancé que « 3x + 5 = 2x - 7 »). Le tuteur reçoit une
   note interne : juste / faux / étape atteinte. Il ne juge jamais seul.
3. **Réponse** du LLM, avec l'étape suivante (secrète) et le niveau d'indice si l'élève réclame la réponse.
4. **Anti-fuite** : si la réponse contient un résultat équivalent à une étape non atteinte et pas plus complexe,
   réécriture demandée ; si elle fuite encore, message de repli générique.

Approche délibérément **déterministe** (vérification par l'orchestrateur, pas par tool calling) : elle ne
dépend pas de la qualité du tool calling des modèles open-weight.

## Limites connues (PoC)

- Sandbox = sous-processus `python -I` + AST/builtins restreints ; production : conteneur gVisor/Firecracker sans réseau.
- ~1,5 s par appel sandbox (démarrage de SymPy) : prévoir un pool de workers chauds.
- Sessions en mémoire (production : Redis avec TTL), pas d'authentification, pas de profil d'apprentissage.
- Inéquations, systèmes, démonstrations : non vérifiés par le plan (le tuteur fonctionne, sans garantie formelle).
- Anti-fuite : un nombre de la solution présent ailleurs dans l'énoncé n'est pas détecté.
- Index PER : PDF © CIIP, usage local uniquement tant que la CIIP n'a pas donné son accord (specs/08 §8.5).
  Les formules mises en page (fractions) sont mal extraites ; l'année de début est fiable, pas la fin.
