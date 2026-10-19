# Spécifications détaillées — Tuteur méthodologique & copilote parental (Suisse romande)

Ce dossier détaille le document source [`../SPECS.md`](../SPECS.md). Il ne le remplace pas : en cas de contradiction, signaler l'écart dans [`12-questions-ouvertes.md`](12-questions-ouvertes.md).

## Décisions validées

| Sujet | Décision |
| --- | --- |
| Périmètre de détail | Phase 1 (Maths & Physique) détaillée ; Phase 2 (Langues) esquissée |
| Plateforme MVP | Application mobile native **Flutter** (iOS + Android) |
| Backend | Python **FastAPI** |
| LLM | Modèles open-weight servis par l'**API IA d'Infomaniak** (inférence en Suisse) |
| Hébergement & stockage | **Infomaniak** exclusivement (calcul, bases, stockage) |
| Comptes | Compte famille (parent + profils enfants) ; **compte autonome pour les gymnasien·ne·s majeur·e·s** |
| Accès Copilote | Protégé par le **mot de passe parent** |
| Historique | **Activé par défaut** ; sert à adapter l'agent à l'élève (niveau, difficultés, façon de s'exprimer) ; **aucune donnée personnelle identifiante (PII)** dans les données pédagogiques |
| Photos | Purgées immédiatement après extraction |
| Lancement géographique | **Genève et Vaud** d'abord |
| Physique | Décalée en Phase 1b (MVP 1a = Maths Cycle 3) |
| Rétention de l'historique | 12 mois |
| Assistants | Un par matière : **Leo** (Maths, Euler), **Albert** (Physique, Einstein) |
| Abonnement | 40 CHF/mois ou 400 CHF/an ; lancement 25 CHF/mois ou 250 CHF/an (à vie, places limitées) ; 18+ : 30 CHF/mois ou 300 CHF/an ; 3 enfants max ; 7 jours d'essai ; promo à chaque rentrée |
| Langues de l'interface | **Application polyglotte** (i18n dès le départ) |
| Nom de l'app | À trouver |
| Budget inférence | 500 CHF/mois au lancement ; GPU dédié accepté si nécessaire |
| Référentiel | PER (+ plans d'études Secondaire II GE/VD) en RAG hybride vectoriel + BM25, fusion RRF — sous réserve du droit de réutilisation |

## Hypothèses restantes (à confirmer)

Marquées **[H]** dans les documents. Détails : [`12-questions-ouvertes.md`](12-questions-ouvertes.md).

- **[H4]** Pas de publicité ; abonnement vendu via l'App Store et Google Play.

## Sommaire

| # | Document | Contenu |
| --- | --- | --- |
| 01 | [Vision & périmètre](01-vision-perimetre.md) | Problème, proposition de valeur, phases, hors-périmètre |
| 02 | [Personas & parcours](02-personas-parcours.md) | Utilisateurs cibles, parcours clés |
| 03 | [Fonctionnel Phase 1](03-phase1-fonctionnel.md) | Modes, user stories, critères d'acceptation |
| 04 | [Couverture curriculaire](04-couverture-curriculaire.md) | Notions PER (9H–11H) et Secondaire II, spécificités GE/VD |
| 05 | [Moteur pédagogique](05-moteur-pedagogique.md) | Règles socratiques, personnalisation, garde-fous, prompts |
| 06 | [Architecture technique](06-architecture-technique.md) | Composants, flux, choix techniques |
| 07 | [Sandbox de calcul](07-sandbox-calcul.md) | Exécution SymPy isolée, contrats d'outils |
| 08 | [Données & conformité](08-donnees-conformite.md) | nLPD, mineurs, absence de PII, éphémérité, LDA |
| 09 | [Exigences non fonctionnelles](09-exigences-non-fonctionnelles.md) | Performance, sécurité, accessibilité, qualité |
| 10 | [Phase 2 — Langues](10-phase2-langues.md) | Esquisse |
| 11 | [Roadmap & jalons](11-roadmap.md) | Découpage MVP, critères de sortie |
| 12 | [Questions ouvertes](12-questions-ouvertes.md) | Doutes, hypothèses, risques |
| 13 | [Offre, tarifs & budget](13-offre-tarifs.md) | Prix, argumentaire, revenu net, budget d'inférence |
| 14 | [Assistants](14-assistants.md) | Leo (Maths), Albert (Physique) |
| — | [Glossaire](glossaire.md) | Termes suisses et techniques |
