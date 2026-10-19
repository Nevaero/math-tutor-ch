# 06 — Architecture technique

## 6.1 Vue d'ensemble

```
┌─────────────────────────────────────────────┐
│  App mobile Flutter (iOS / Android)          │
│  Profils · Caméra · Éditeur formules · Chat  │
└──────────────────────┬──────────────────────┘
                       │ HTTPS (TLS 1.3) + SSE/WebSocket (streaming)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ Infomaniak (Suisse) — Public Cloud / Kubernetes                  │
│                                                                  │
│  ┌──────────────┐   ┌───────────────────┐   ┌─────────────────┐  │
│  │ Ingress /    │──►│ Backend FastAPI   │──►│ PostgreSQL      │  │
│  │ rate limit   │   │ comptes, sessions,│   │ comptes (PII)   │  │
│  └──────────────┘   │ orchestrateur     │   │ ─── séparé ───  │  │
│                     └──┬──────┬─────┬───┘   │ données pédago  │  │
│                        │      │     │       │ (pseudonymes)   │  │
│                        │      │     │       └─────────────────┘  │
│                        │      │     ▼                            │
│                        │      │  ┌──────────────────┐            │
│                        │      │  │ Redis (sessions  │            │
│                        │      │  │ éphémères, TTL)  │            │
│                        │      │  └──────────────────┘            │
│                        │      ▼                                  │
│                        │   ┌──────────────────────┐              │
│                        │   │ Sandbox Python       │              │
│                        │   │ SymPy / NumPy        │              │
│                        │   │ (gVisor, sans réseau)│              │
│                        │   └──────────────────────┘              │
│                        ▼                                         │
│  ┌──────────────────────────────────────────┐                    │
│  │ API IA Infomaniak (modèles open-weight)  │                    │
│  │ VLM : lecture d'énoncé                   │                    │
│  │ LLM : dialogue tuteur / copilote / résumé│                    │
│  └──────────────────────────────────────────┘                    │
│                                                                  │
│  Object Storage Infomaniak : sauvegardes chiffrées uniquement    │
│  (jamais d'images de devoirs)                                    │
└──────────────────────────────────────────────────────────────────┘
```

## 6.2 Application mobile (Flutter)

| Sujet | Choix proposé |
| --- | --- |
| Framework | Flutter (Dart), une base de code iOS/Android |
| État / architecture | Riverpod ou Bloc ; couches data / domain / presentation |
| Rendu maths | Package Flutter de rendu LaTeX natif (ex. `flutter_math_fork`) ; repli WebView KaTeX pour les cas non supportés |
| Éditeur de formules | Clavier mathématique personnalisé (fractions, puissances, racines, π, ∫), sortie en LaTeX/ASCII math |
| Caméra | `camera` + détection de bords/recadrage côté client ; compression avant envoi ; image gardée en mémoire puis libérée |
| Stockage local | Aucun stockage persistant d'images ; jetons dans Keychain / Keystore (`flutter_secure_storage`) |
| Verrou Copilote | Saisie du mot de passe parent, vérification serveur ; jeton Copilote à durée courte |
| Streaming | Affichage progressif des réponses (SSE) |
| Hors-ligne | Non supporté au MVP (message clair) |
| SDK tiers | Liste blanche ; pas de Firebase Analytics/Crashlytics (transferts hors CH) — crash reporting auto-hébergé chez Infomaniak (ex. Sentry/GlitchTip self-hosted) **[à valider]** |
| Distribution | App Store + Google Play ; déclarations « données des enfants » des stores à préparer |

## 6.3 Backend (FastAPI)

| Composant | Responsabilité |
| --- | --- |
| Auth | Comptes parents et comptes autonomes 18+ ; mot de passe (Argon2id) ; ré-authentification pour le mode Copilote et les réglages |
| Profils | Profils élèves pseudonymes, rattachés au compte par un identifiant opaque |
| Sessions de tutorat | État de la machine à états ([05](05-moteur-pedagogique.md)) dans Redis avec TTL |
| Orchestrateur | Boucle agent : LLM ↔ outils (sandbox, glossaire, profil d'apprentissage) |
| Job de fin de session | Résumé + mise à jour du profil d'apprentissage, **après** passage dans le filtre PII |
| Filtre PII | Détection/suppression des données identifiantes (règles + modèle NER francophone auto-hébergé + passe LLM de contrôle) |
| Facturation | Abonnements in-app (Apple/Google) **[H4]** |

### Séparation des données

- **Base « identité »** : e-mail, hash du mot de passe, consentements, abonnement.
- **Base « pédagogie »** : profils pseudonymes, historique, profils d'apprentissage — clé = identifiant aléatoire, sans e-mail ni nom.
- La table de correspondance compte ↔ profils est dans la base identité ; l'accès à la base pédagogie seule ne permet pas d'identifier une famille.

## 6.4 Inférence LLM — API IA Infomaniak

| Sujet | Spécification |
| --- | --- |
| Fournisseur | API IA d'Infomaniak : inférence en Suisse, modèles open-weight |
| Catalogue | Limité aux modèles proposés par Infomaniak → **benchmark sur ce catalogue** en Phase 0 (vision, raisonnement, tool calling, respect des consignes en français) **[catalogue et capacités à vérifier]** |
| Prérequis à vérifier | Support du tool/function calling, sorties structurées (JSON), entrée image, streaming, quotas et limites de débit, engagement contractuel de non-rétention et de non-entraînement sur les données |
| Architecture | 1 VLM pour l'extraction d'énoncé + 1 LLM texte pour le dialogue (ou le même modèle si suffisant) |
| Repli | Si une capacité manque (ex. pas de tool calling natif) : tool calling par sortie JSON contrainte gérée par l'orchestrateur |
| Fine-tuning | Hors MVP ; jamais sur conversations de mineurs |
| Abstraction | Interface « provider » interne (format compatible OpenAI) pour changer de modèle ou basculer vers de l'auto-hébergement GPU chez Infomaniak plus tard |
| Budget | 500 CHF/mois au lancement ; GPU dédié (vLLM sur GPU Infomaniak) accepté si la qualité ou le coût à l'échelle l'exigent — règles de bascule dans [13](13-offre-tarifs.md) §13.4 |
| Assistants | Leo et Albert partagent le même modèle ; seule la configuration change ([14](14-assistants.md)) |

**Risque principal** : qualité des modèles disponibles au catalogue (raisonnement, règles socratiques, lecture de formules manuscrites). Mitigation : la sandbox porte l'exactitude ; benchmark Phase 0 ; repli possible sur GPU Infomaniak avec un modèle de notre choix.

## 6.5 Pipeline vision / OCR

1. Réception de l'image (en mémoire uniquement, taille max, formats JPEG/HEIC/PNG).
2. Pré-traitement : redressement, contraste.
3. Extraction par le VLM (API Infomaniak).
4. Sortie structurée : `{ exercices: [{ id, enonce_texte, enonce_latex, figures: [...], donnees: {...} }] }`.
5. Purge du buffer image dès l'extraction terminée (voir [08](08-donnees-conformite.md)).
6. Si l'image contient des données identifiantes (nom de l'élève sur la feuille), elles ne sont pas reprises dans l'énoncé extrait.

## 6.6 RAG

| Type | Contenu | Stockage | Durée |
| --- | --- | --- | --- |
| Éphémère | Énoncé extrait, feuille d'objectifs | Redis (session) | TTL de session (ex. 2 h d'inactivité) |
| Permanent | PER, plans d'études Secondaire II GE/VD, glossaire PER, fiches méthodes internes, pièges, structures cantonales | PostgreSQL : pgvector + index plein texte | Versionné |
| Personnel | Profil d'apprentissage + résumés | Base pédagogie | Rétention définie |

### Recherche hybride sur le corpus permanent (vectoriel + BM25, fusion RRF)

Les référentiels mélangent langage naturel (« résoudre des équations ») et codes/termes exacts (« MSN 33 », « mise en évidence ») : la recherche lexicale rattrape ce que les embeddings ratent, et l'inverse.

```
requête (énoncé extrait / question)
   │
   ├─► filtres métadonnées (cycle, degré, canton, discipline) ── appliqués aux deux branches
   │
   ├─► Vectoriel : embedding (modèle multilingue, API Infomaniak) → pgvector (HNSW, cosinus) → top 50
   ├─► Lexical BM25 : analyseur français (élision, accents, racinisation) → top 50
   │
   ▼
Fusion RRF : score(d) = Σ 1 / (k + rang_i(d)), k = 60
   │
   ▼
(option) re-ranking par cross-encoder auto-hébergé → top 5–8 chunks injectés dans le contexte
```

| Sujet | Choix proposé |
| --- | --- |
| Stockage | Tout dans PostgreSQL (Infomaniak) : un seul système, transactions, filtres SQL |
| Vectoriel | `pgvector`, index HNSW |
| BM25 | Le `ts_rank` natif de PostgreSQL n'est pas un vrai BM25 → extension BM25 (ex. ParadeDB `pg_search`) si disponible sur l'offre Infomaniak, sinon ts_rank (approximation acceptable au MVP) ou OpenSearch auto-hébergé **[à trancher en Phase 0]** |
| Embeddings | Modèle multilingue performant en français, via l'API Infomaniak si disponible au catalogue, sinon auto-hébergé **[à vérifier]** |
| Fusion | RRF (k = 60), pondération des branches ajustable après évaluation |
| Requêtes | Le LLM reformule l'énoncé en requête courte (notion + degré) avant recherche ; les filtres métadonnées viennent du profil |
| Évaluation | Jeu de ~100 requêtes annotées (énoncé → objectif PER attendu) ; métriques recall@5, MRR ; comparaison vectoriel seul / BM25 seul / hybride |

Outil exposé au LLM : `search_curriculum(query, degre, canton, discipline)` → chunks avec `code_objectif` et `source_url`.

## 6.7 Outils exposés au LLM

| Outil | Rôle |
| --- | --- |
| `sympy_exec` | Exécution de code SymPy en sandbox ([07](07-sandbox-calcul.md)) |
| `verify_step` | Vérifie l'équivalence entre une proposition élève et l'attendu |
| `plot_function` | Génère un graphique |
| `glossary_lookup` | Terme PER pour une notion, un degré et un canton |
| `search_curriculum` | Recherche hybride dans le PER et les plans d'études (§6.6) |
| `get_learner_context` | Projection du profil d'apprentissage pour la notion en cours |

Le LLM n'a **pas** d'outil d'écriture sur le profil d'apprentissage : la mise à jour est faite par le job de fin de session, après filtrage PII.

## 6.8 Observabilité

- Logs techniques sans contenu conversationnel par défaut ; contenu uniquement en échantillonnage pseudonymisé pour audit qualité (si prévu dans la politique de confidentialité).
- Métriques : latence par étape, taux d'appels sandbox, échecs OCR, déclenchements du filtre anti-fuite et du filtre PII.
- Outils d'observabilité auto-hébergés chez Infomaniak (pas de SaaS étranger).
