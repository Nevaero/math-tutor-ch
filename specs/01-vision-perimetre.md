# 01 — Vision & périmètre

## Problème

Les devoirs à la maison sont une source récurrente de tension familiale en Suisse romande :

- Les parents ne maîtrisent plus (ou n'ont jamais appris) les notions et surtout **le vocabulaire et les méthodes** attendus par le PER (Plan d'études romand). Ils expliquent « autrement » et créent de la confusion.
- Les outils existants (solveurs photo, chatbots généralistes) **donnent la réponse** : l'élève recopie sans comprendre, et l'enseignant le détecte.
- Les familles et les écoles sont sensibles à la **protection des données des mineurs** et réticentes aux services hébergés hors de Suisse.

## Proposition de valeur

> Un tuteur qui fait **comprendre** sans faire **à la place**, qui outille le parent avec les mots de l'école, et dont les données ne quittent jamais la Suisse.

Un assistant par matière incarne le service : **Leo** pour les maths, **Albert** pour la physique (voir [14](14-assistants.md)). Positionnement prix : un mois d'abonnement coûte le prix d'une heure de cours particulier (voir [13](13-offre-tarifs.md)).

Trois piliers :

1. **Pédagogie** — méthode socratique, jamais de solution brute, vocabulaire conforme au PER.
2. **Exactitude** — tout calcul est délégué à un moteur de calcul formel (SymPy) ; le LLM ne calcule pas « de tête ».
3. **Souveraineté** — infrastructure et inférence 100 % suisses, photos éphémères, aucune réutilisation pour l'entraînement.

## Phases

| Phase | Matières | Cœur technique | Statut de ce dossier |
| --- | --- | --- | --- |
| 1 — MVP Sciences | Maths, Physique (9H → Maturité) | Vision + LLM + Sandbox SymPy + RAG éphémère | **Détaillé** |
| 2 — Langues | Allemand scolaire, puis Anglais | Voice-to-voice faible latence, feedback grammatical | Esquissé ([10](10-phase2-langues.md)) |

## Découpage interne de la Phase 1

La Phase 1 couvre deux publics très différents. Découpage validé (voir [11](11-roadmap.md)) :

- **1a** — Cycle 3 (9H–11H) Maths avec Leo, cantons de **Genève et Vaud**. Plus grand marché, notions plus stables, parents plus impliqués.
- **1b** — Physique Cycle 3 avec Albert + Secondaire II Maths (analyse, trigonométrie).
- **1c** — Secondaire II avancé : algèbre linéaire, EDO (option spécifique).

## Hors périmètre (Phase 1)

- Correction / notation de devoirs entiers ou d'examens.
- Production de corrigés téléchargeables.
- Tableau de bord enseignant, intégration aux plateformes scolaires.
- Cycles 1 et 2 (1H–8H) — à réévaluer.
- Langues autres que le français pour l'interface.
- Usage web (le MVP est mobile natif, Flutter).
- Autres cantons romands que GE et VD au lancement (FR, NE, VS, JU, Jura bernois ensuite).

## Indicateurs de succès (proposition)

| Indicateur | Cible indicative |
| --- | --- |
| Sessions où l'élève atteint la solution par lui-même | > 60 % |
| Taux de fuite de solution (audit échantillonné) | < 1 % des sessions |
| Exactitude des calculs affichés (audit) | > 99,5 % |
| Note de satisfaction parent après session Copilote | ≥ 4/5 |
| Rétention familles à 4 semaines | à définir |
