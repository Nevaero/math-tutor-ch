# 12 — Questions ouvertes, hypothèses & risques

## Décisions prises

| Question | Décision |
| --- | --- |
| Framework mobile | Flutter |
| Backend | Python FastAPI |
| Protection du mode Copilote | Mot de passe parent |
| Gymnasien·ne·s majeur·e·s | Compte autonome possible |
| Historique | Activé par défaut, sert à adapter l'agent (niveau, difficultés, façon de s'exprimer) ; aucune PII |
| Hébergement / LLM | API IA et stockage Infomaniak |
| Cantons de lancement | Genève et Vaud |
| Physique | Phase 1b |
| Référentiel | PER (+ plans d'études Secondaire II GE/VD) indexé en RAG hybride vectoriel + BM25, fusion RRF |
| Rétention de l'historique | 12 mois |
| Budget inférence | 500 CHF/mois ; GPU dédié accepté si besoin |
| Tarifs | 40 CHF/mois, 400 CHF/an ; lancement 25 CHF/mois, 250 CHF/an à vie (places limitées) ; 18+ : 30/300 CHF ; 3 enfants ; essai 7 jours ([13](13-offre-tarifs.md)) |
| Langues de l'interface | Application polyglotte |
| Assistants | Leo (Maths), Albert (Physique) ([14](14-assistants.md)) |

## Hypothèses à confirmer

| # | Hypothèse | Impact si fausse |
| --- | --- | --- |
| H4 | Pas de pub ; abonnement via les stores | Vente hors app = commission évitée mais parcours d'achat plus complexe |

## Questions produit

1. **Offre** : voir [13](13-offre-tarifs.md) §13.5 (nombre de places de lancement, matières incluses, promotions).
2. **Assistants** : voir [14](14-assistants.md) §14.5 (nom de l'app, tutoiement, noms Phase 2).
   **Polyglotte** : l'interface sera traduite (FR, DE, IT, EN ?) ; les assistants répondent-ils dans la langue de l'interface alors que le contenu suit le PER romand ? Quelles langues au lancement ?
3. **Contenu du résumé** : reformulation de la notion/méthode uniquement, ou énoncé complet (prudence LDA) ?
4. **Comptes 18+** : simple déclaration d'âge ou vérification ? Que devient un profil enfant quand l'élève atteint 18 ans (transfert vers un compte autonome) ?
5. **Mineur·e·s de 16–17 ans** : le parent voit-il tout leur historique ?
6. **Structures cantonales** : faut-il distinguer finement les sections GE et les niveaux VD dès le MVP, ou seulement le degré ?
7. **Cycle 2 (5H–8H)** : marché important — à inclure plus tard ?
8. **Phase 2** : allemand dès la 7H ou la 9H ?
9. ~~Intitulé de l'option spécifique~~ → option spécifique VD « Mathématiques et Physique » du Cycle 3 (voie prégymnasiale), voir [04](04-couverture-curriculaire.md). Équivalent genevois à identifier.
10. **Offre écoles / communes** à terme ?

## Questions techniques

11. **Catalogue API IA Infomaniak** : quels modèles vision disponibles, tool calling, sorties JSON, quotas, garanties contractuelles de non-rétention ? (à vérifier en Phase 0)
12. **Coût réel par session** à mesurer en Phase 0 pour valider que 500 CHF/mois couvrent la bêta et le lancement.
13. **Notifications push** : nécessaires ? (transitent par Apple/Google)
14. **Crash reporting / analytics** : solution auto-hébergée chez Infomaniak acceptée ?
15. **Équipe** disponible (taille, compétences Flutter / ML / backend) ?
16. **PER en RAG** : droit de réutilisation du PER (CIIP) et des plans d'études GE/VD ? Extension BM25 disponible sur PostgreSQL Infomaniak, ou faut-il OpenSearch ? Modèle d'embeddings disponible au catalogue Infomaniak ?

## Risques

| Risque | Probabilité | Impact | Mitigation |
| --- | --- | --- | --- |
| Catalogue de modèles Infomaniak insuffisant (OCR manuscrit, règles socratiques, tool calling) | Moyenne | Élevé | Benchmark Phase 0, sandbox pour l'exactitude, abstraction provider, repli GPU |
| Dépendance à un fournisseur unique (Infomaniak) | Moyenne | Moyen | IaC portable (Kubernetes), API compatible OpenAI, sauvegardes exportables |
| Quotas API insuffisants au pic du soir | Moyenne | Moyen | Test de charge, file d'attente, quotas freemium |
| Fuite de solution malgré les garde-fous | Moyenne | Élevé | Défense en profondeur ([05](05-moteur-pedagogique.md) §5.3), tests adversariaux |
| PII résiduelle dans l'historique | Moyenne | Élevé | Schéma en listes fermées, filtre multi-couches, tests piégés ([08](08-donnees-conformite.md) §8.3) |
| Historique activé par défaut contesté (privacy by default) | Faible à moyenne | Moyen | Justification de nécessité, information claire, désactivation simple, avis juridique |
| Non-conformité via SDK mobiles tiers | Moyenne | Élevé | Audit SDK, solutions auto-hébergées |
| Enfant accédant au mode Copilote (mot de passe partagé ou deviné) | Moyenne | Moyen | Ré-authentification, verrouillage après échecs, sensibilisation du parent |
| Vocabulaire PER mal respecté | Moyenne | Moyen | Glossaire validé par enseignant·e·s, évaluation automatique |
| Perception « outil de triche » par les enseignant·e·s | Moyenne | Élevé | Positionnement méthodologique clair, communication vers les écoles |
| Coût d'inférence supérieur au revenu au tarif de lancement | Moyenne | Élevé | Modèle de coût Phase 0, quota d'usage équitable, leviers d'économie ([13](13-offre-tarifs.md) §13.4) |
| Argument « 1 h de cours particulier » contesté (publicité comparative) | Faible | Moyen | Relevé de prix sourcé et daté, formulation prudente |
| Droits sur le nom / l'image d'Einstein | Faible à moyenne | Moyen | Prénom seul, avatar original, avis juridique |
