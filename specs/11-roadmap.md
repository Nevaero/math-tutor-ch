# 11 — Roadmap & jalons

Durées non estimées volontairement : elles dépendent de l'équipe (inconnue à ce stade).

## Phase 0 — Fondations & levée des risques

**PoC démarré** (`poc/`, 19.10.2026) : sandbox SymPy + vérification d'équivalence, plan interne vérifié, tuteur socratique avec anti-fuite, Copilote, extraction photo, ingestion du PER + recherche hybride, bancs d'évaluation. En attente : jeton API Infomaniak pour le benchmark des modèles.


| Livrable | Critère de sortie |
| --- | --- |
| Benchmark des modèles du catalogue de l'API IA Infomaniak (vision + dialogue) | Choix argumenté ; seuils atteints sur OCR, respect socratique, latence ; capacités vérifiées (tool calling, JSON, image, quotas) |
| Prototype sandbox + `verify_step` | Couverture des notions 9H–11H ; parseur de notation scolaire |
| Jeu d'évaluation v1 | ≥ 100 exercices Cycle 3 avec photos internes |
| Glossaire PER v1 + structures cantonales GE/VD | Validés par des enseignant·e·s GE et VD |
| Contrat Infomaniak (cloud + API IA) + modèle de coût ([13](13-offre-tarifs.md) §13.4) | Coût par session mesuré ; coût d'inférence par abonné ≤ 15 % du revenu net ; seuil de bascule GPU calculé ; clauses de non-rétention/non-entraînement |
| Relevé des tarifs de cours particuliers à GE et VD | Source datée pour l'argument « 40 CHF = 1 h de cours » |
| Identité de Leo et Albert | Avatars originaux, noms vérifiés (marques), avis juridique sur l'hommage à Einstein |
| Filtre PII v1 | 0 PII résiduelle sur le jeu de conversations piégées |
| Autorisation CIIP + ingestion du PER (MSN) + recherche hybride | Droit de réutilisation obtenu ; recall@5 hybride > vectoriel seul et BM25 seul sur le jeu de requêtes annotées |
| AIPD initiale + revue juridique (nLPD, LDA, mineurs) | Feu vert sur le modèle de données |

## Phase 1a — MVP Cycle 3 Maths (Genève et Vaud)

- App Flutter iOS/Android, backend FastAPI sur Infomaniak.
- Comptes famille, profils, consentement, mot de passe parent, comptes 18+ (CPT-01→06, 08).
- Capture + validation d'énoncé (CAP-01→04, 07).
- Assistant **Leo** : mode Copilote (COP-01→05) et Tuteur (TUT-01→07) ; Albert affiché « bientôt ».
- Abonnements in-app au tarif de lancement (ABO-01→04).
- Rendu maths (REN-01→03), historique activé + profil d'apprentissage (HIS-01→05), garde-fous (GF-01→03).
- Bêta fermée avec des familles genevoises et vaudoises.

**Critères de sortie** : taux de fuite < 1 %, exactitude calcul > 99,5 %, satisfaction parent ≥ 4/5, pentest réalisé.

## Phase 1b — Albert (Physique Cycle 3) + Secondaire II Maths

- Lancement d'**Albert** (configuration, glossaire et jeu d'évaluation physique) ; détection de matière (AST-02).
- Schémas et graphiques (CAP-05), multi-pages (CAP-06), tracés (REN-04).
- Analyse, trigonométrie, unités physiques.
- Vérification de démarche (TUT-08).

## Phase 1c — Secondaire II avancé

- Algèbre linéaire, EDO, probabilités.
- Vues parent sur le profil d'apprentissage (HIS-06, HIS-07).
- Ouverture aux autres cantons romands.

## Phase 2 — Langues

Voir [10](10-phase2-langues.md). Démarrage conditionné à un spike technique voix (ASR/TTS CH, latence).
