# 14 — Assistants par matière

Chaque matière a son assistant, avec un nom, une personnalité et une spécialité. Le moteur technique est partagé (orchestrateur, sandbox, RAG, profil d'apprentissage).

## 14.1 Les assistants

| | **Leo** | **Albert** |
| --- | --- | --- |
| Matière | Mathématiques | Physique |
| Inspiration | Leonhard Euler (1707–1783), mathématicien bâlois | Albert Einstein, qui a travaillé à l'Office des brevets de Berne et y a publié ses articles de 1905 |
| Lien suisse | Né à Bâle | Années bernoises |
| Phase | 1a (MVP) | 1b |
| Personnalité (proposition) | Curieux, méthodique, aime les « astuces » et la notation propre | Pose des « expériences de pensée », part toujours d'une situation concrète |
| Signature pédagogique | « Qu'est-ce qu'on cherche ? Qu'est-ce qu'on sait ? » | « Imagine que tu es dans le train… », schéma et unités d'abord |
| Outils spécifiques | Sandbox SymPy, tracés de fonctions | Sandbox SymPy + unités physiques (`sympy.physics.units`), schémas de forces, graphiques position-temps |

Les deux appliquent les mêmes règles : méthode socratique, jamais de solution brute en mode Élève, calculs délégués à la sandbox, vocabulaire PER, aucune donnée personnelle.

## 14.2 Mise en œuvre

| Élément | Spécification |
| --- | --- |
| Configuration | Un assistant = un fichier de configuration versionné : nom, matière, prompt de personnalité, outils autorisés, glossaire, filtres RAG (discipline), exemples de dialogue |
| Prompt | Prompt commun (règles, sécurité, PII) + couche personnalité de l'assistant. La personnalité ne peut jamais assouplir une règle commune |
| Profil d'apprentissage | Un seul profil par élève, sections par matière ; Albert peut voir que l'élève est « fragile » en équations (info de Leo) |
| Mode Copilote | Disponible pour chaque assistant ; ton adulte, même personnalité discrète |
| Évaluation | Jeu d'évaluation par assistant (voir [09](09-exigences-non-fonctionnelles.md)) |
| Ajout futur | Ajouter un assistant (ex. allemand en Phase 2) = nouvelle configuration, sans changer le code de l'orchestrateur |

## 14.3 Choix et transfert d'assistant

| Cas | Comportement |
| --- | --- |
| Écran d'accueil | L'utilisateur choisit Leo ou Albert |
| Photo d'énoncé | Détection de la matière ; si elle ne correspond pas à l'assistant ouvert, proposition de passer à l'autre |
| Exercice de physique avec un blocage mathématique (ex. isoler une variable) | Albert aide directement, avec le vocabulaire des maths, sans changer d'assistant (pas de transfert en cours d'exercice) |
| Albert pas encore disponible (Phase 1a) | Affiché « bientôt » ; Leo ne traite pas la physique, il l'explique gentiment |

## 14.4 Identité visuelle

- Avatar illustré propre à chaque assistant, style cohérent, adapté aux 12–19 ans.
- **Ne pas reproduire les traits d'Einstein** (visage, moustache, langue tirée) ni utiliser « Einstein » comme nom : les droits sur le nom et l'image d'Einstein sont gérés et défendus activement. « Albert » seul, avec un avatar original, limite le risque ; formulation de l'hommage à faire valider **[à vérifier juridiquement]**.
- Euler : pas de contrainte connue (décédé en 1783), mais même principe d'avatar original.
- Les assistants se présentent clairement comme des IA (pas de faux humain).
- Vérifier la disponibilité des noms et marques (« Leo », « Albert » sont courants dans l'éducation et la tech) pour le nom de l'app et les stores.

## 14.5 Questions ouvertes

1. Nom de l'application elle-même (distinct de Leo et Albert) ?
2. Leo et Albert se tutoient avec l'élève ? (proposition : tutoiement en mode Élève, vouvoiement en mode Copilote)
3. Noms des assistants de la Phase 2 (allemand, anglais) ?
