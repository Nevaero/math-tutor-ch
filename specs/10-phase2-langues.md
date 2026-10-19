# 10 — Phase 2 : Langues (esquisse)

## Cible

- **Allemand scolaire** en priorité (dès 7H/9H — **[à clarifier : la spec source dit « 7H/9H »]**), principal point de décrochage familial en Suisse romande.
- **Anglais** ensuite.
- Parents souvent non germanophones : les explications sont données en français.

Chaque langue aura son assistant, sur le modèle de Leo et Albert ([14](14-assistants.md)) ; noms à définir.

## Fonctionnalités principales

| Fonctionnalité | Description |
| --- | --- |
| Tuteur vocal conversationnel | Dialogue oral en temps réel, interlocuteur patient et sans jugement, débit adaptable |
| Correction contextuelle | Explication en français des fautes récurrentes : déclinaisons, ordre des mots en subordonnée, genre, accords |
| Roleplays PER | Décrire sa journée, demander son chemin, donner une opinion simple — calibrés sur les attentes de fin de cycle |
| Vocabulaire | Révision de listes de vocabulaire (photo de la liste → exercices) |
| Feedback prosodique | Prononciation, intonation (à évaluer techniquement) |

## Garde-fous

- Tolérance bienveillante : ne pas corriger chaque faute ; prioriser 1–2 points par échange.
- Corrections progressives ; récapitulatif en fin de session.
- Mêmes principes de souveraineté et d'éphémérité ; **l'audio est une donnée sensible** (voix d'enfants) → traitement en mémoire, aucune conservation.

## Points techniques à explorer

- ASR et TTS open-source auto-hébergés en Suisse ; qualité sur voix d'enfants et accents francophones.
- Latence de bout en bout < ~800 ms pour une conversation naturelle (cible à valider).
- Le suisse allemand n'est pas visé : l'école enseigne l'allemand standard.
- Réutilisation : comptes, profils, orchestrateur, observabilité de la Phase 1.

## Questions ouvertes spécifiques

- Les manuels d'allemand romands ont un vocabulaire par unité : faut-il un corpus par manuel (risque LDA) ou des listes saisies par l'élève ?
- Mode Copilote pour les langues : quel contenu pour un parent qui ne parle pas allemand ?
