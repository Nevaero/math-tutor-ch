\## Spécifications fonctionnelles et techniques du produit



L'application est conçue comme un \*\*tuteur méthodologique et copilote parental\*\*, pensé en priorité pour soulager les tensions lors des devoirs à domicile en Suisse romande, avec un ancrage fort sur la souveraineté des données.



\---



\### 1. Vision générale et périmètre par phases



```text

\[PHASE 1 : MVP Sciences dures]           \[PHASE 2 : Extension Langues]

&#x20; • Maths \& Physique (9H à Maturité)      • Allemand scolaire \& Anglais

&#x20; • Vision + Sandbox Python (SymPy)        • Audio bidirectionnel faible latence

&#x20; • RAG à la volée (OCR devoirs)           • Feedback prosodique \& grammaire

&#x20; • Mode Copilote Parent \& Tuteur Socratique • Mises en situation orales PER



```



\---



\### 2. Spécifications fonctionnelles — Phase 1 : Sciences dures (Maths \& Physique)



\* \*\*Publics cibles :\*\*

\* \*Cycle 3 (9H–11H) :\* Arithmétique relationnelle, calcul littéral, équations du 1er degré, théorèmes de géométrie, bases de cinématique.

\* \*Secondaire II / Gymnase :\* Analyse (dérivées, intégrales, exponentielles, logarithmes), trigonométrie, puis algèbre linéaire (matrices) et équations différentielles (OS Maths-Physique).





\* \*\*Modes d'interaction :\*\*

\* \*\*Mode « Copilote Parent » :\*\* Le parent scanne la consigne de l'exercice ; l'application lui fournit le déroulé pédagogique (termes conformes au PER), les étapes clés du calcul et 2 ou 3 questions d'amorçage à poser à l'enfant.

\* \*\*Mode « Tuteur Socratique » (Élève) :\*\* L'élève interagit directement avec l'agent, qui applique une règle stricte : \*\*interdiction de donner la solution brute\*\*. L'agent décompose le blocage en sous-problèmes et valide chaque étape intermédiaire.





\* \*\*Fonctionnalités clés :\*\*

\* \*Scan multimodal :\* Prise de vue photo de l'énoncé papier, de schémas géométriques ou de graphiques physiques.

\* \*RAG éphémère à la volée :\* Extraction du contexte immédiat (feuille d'objectifs, énoncé) pour la session courante sans indexation permanente.

\* \*Garantie d'exactitude formelle :\* Délégation automatique de tout calcul, dérivation ou factorisation à un interpréteur de code interne.







\---



\### 3. Spécifications fonctionnelles — Phase 2 : Langues (Allemand \& Anglais)



\* \*\*Publics cibles :\*\* Priorité à l'\*\*allemand scolaire (dès la 7H/9H)\*\*, principal point de décrochage familial en Suisse romande, puis à l'anglais.

\* \*\*Fonctionnalités clés :\*\*

\* \*Tuteur vocal conversationnel :\* Entraînement oral fluide en temps réel (interlocuteur patient, dénué de jugement).

\* \*Correction linguistique contextuelle :\* Explication des fautes récurrentes (déclinaisons, ordre des mots en subordonnée allemande, accords) traduites et expliquées en français pour le parent ou l'élève.

\* \*Mises en situation (Roleplay) :\* Simulations calquées sur les attentes de fin de cycle (décrire sa journée, demander son chemin, soutenir une opinion simple).







\---



\### 4. Architecture technique et souveraineté suisse



```text

┌────────────────────────────────────────────────────────┐

│             INTERFACE UTILISATEUR (Web / Mobile)       │

│        Vue Parent (Guide)  |  Vue Élève (Socratique)   │

└───────────────────────────┬────────────────────────────┘

&#x20;                           │ Requêtes chiffrées (TLS)

&#x20;                           ▼

┌────────────────────────────────────────────────────────┐

│         INFRASTRUCTURE 100% SUISSE (Exoscale /         │

│          Infomaniak / Régions Suisses Hyperscalers)    │

│                                                        │

│  ┌───────────────────────┐   ┌──────────────────────┐  │

│  │   Orchestrateur LLM   │◄─►│   Sandbox Python     │  │

│  │ (Modèle Multimodal)   │   │  (SymPy, NumPy,      │  │

│  └───────────┬───────────┘   │   Calcul formel)     │  │

│              │               └──────────────────────┘  │

│              ▼                                         │

│  ┌───────────────────────┐                             │

│  │ Pipeline RAG Éphémère │ (Suppression mémoire vive    │

│  │  (Vision \& OCR local) │  immédiatement après usage) │

│  └───────────────────────┘                             │

└────────────────────────────────────────────────────────┘



```



\* \*\*Exécution symbolique sécurisée :\*\*

Un bac à sable Python isolé exécutant `SymPy` pour :

\* La factorisation et résolution d'équations ($ax+b=c$, second degré, systèmes).

\* L'analyse gymnasiale (dérivées $f'(x)$, primitives $\\int f(x)dx$, limites).

\* Les matrices, déterminants et équations différentielles ordinaires (EDO).





\* \*\*Hébergement et conformité réglementaire :\*\*

\* Serveurs et inférences LLM situés exclusivement sur le territoire suisse.

\* \*\*Conformité nLPD stricte :\*\* Aucun transfert transfrontalier de données, zéro utilisation des données des mineurs pour réentraîner des modèles.

\* Politique d'éphémérité : les photos de devoirs sont traitées en mémoire et purgées immédiatement pour écarter tout litige sur le droit d'auteur des manuels scolaires (LDA).







\---



\### 5. Grille de synthèse des spécifications



| Brique | Phase 1 (Sciences) | Phase 2 (Langues) |

| --- | --- | --- |

| \*\*Matières\*\* | Maths, Physique | Allemand, Anglais |

| \*\*Moteur sous-jacent\*\* | LLM Multimodal + Sandbox Python (`SymPy`) | LLM Multimodal + Voice-to-Voice (ASR/TTS) |

| \*\*Objectif pédagogique\*\* | Compréhension conceptuelle \& méthodologie sans calcul erroné | Fluidité orale, automatismes grammaticaux et vocabulaire |

| \*\*Garde-fous\*\* | Pas de corrigé direct ; vérification des étapes | Tolérance bienveillante aux erreurs ; corrections progressives |

| \*\*Hébergement\*\* | Suisse exclusif (nLPD, Swiss Made) | Suisse exclusif (nLPD, Swiss Made) |

