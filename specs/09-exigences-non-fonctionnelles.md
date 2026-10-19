# 09 — Exigences non fonctionnelles

Les valeurs chiffrées sont des cibles initiales à ajuster après le benchmark modèle.

## Performance

| Exigence | Cible |
| --- | --- |
| Extraction d'énoncé (photo → texte validable) | p95 < 8 s |
| Premier token d'une réponse du tuteur | p95 < 2 s |
| Réponse complète du tuteur (avec appel sandbox) | p95 < 6 s |
| Exécution sandbox | p95 < 1 s, timeout 3 s |
| Sessions simultanées au lancement | à dimensionner (ex. 200 en pic 17h–20h) |

Le pic d'usage est très concentré (soirs de semaine, dimanche soir) : vérifier que les quotas et limites de débit de l'API IA Infomaniak tiennent ce pic ; sinon prévoir une file d'attente avec message d'attente honnête.

## Disponibilité

- Cible 99,5 % sur les plages 16h–21h (heure suisse) en période scolaire.
- Maintenances planifiées hors de ces plages et pendant les vacances scolaires.

## Sécurité

Voir [08](08-donnees-conformite.md) §8.5 et [07](07-sandbox-calcul.md) §7.4.

## Accessibilité & UX

- Conformité WCAG 2.2 AA pour les écrans de l'app (tailles dynamiques, contraste, lecteurs d'écran VoiceOver/TalkBack ; formules annotées pour la lecture vocale).
- Mode sombre.
- Prise en compte de la dyscalculie / dyslexie : police lisible, possibilité d'étapes plus petites **[S]**.
- Messages courts pour le Cycle 3.

## Compatibilité

- iOS : 2 dernières versions majeures.
- Android : versions couvrant ≥ 90 % du parc suisse.
- Appareils d'entrée de gamme (le téléphone familial n'est pas forcément récent).

## Qualité pédagogique & IA

| Exigence | Mise en œuvre |
| --- | --- |
| Jeu d'évaluation | ≥ 300 exercices annotés couvrant [04](04-couverture-curriculaire.md), avec photos réelles (manuscrites et imprimées, éclairage variable) — photos produites en interne pour éviter le problème LDA |
| Métriques | Exactitude OCR, exactitude des calculs, taux de fuite de solution, respect du vocabulaire PER, longueur des messages, **taux de PII résiduelle dans l'historique (cible : 0)**, pertinence de la personnalisation |
| Tests adversariaux | Tentatives d'obtention de la réponse, de sortie de périmètre, d'injection via l'image |
| Gate de déploiement | Aucun changement de modèle ou de prompt en production sans passage du jeu d'évaluation |
| Revue humaine | Échantillonnage régulier par un·e enseignant·e (sur données consenties ou synthétiques) |

## Maintenabilité

- Prompts, glossaire et fiches méthodes versionnés hors code applicatif.
- Infrastructure décrite en code (IaC).
- Abstraction du fournisseur de modèle.
