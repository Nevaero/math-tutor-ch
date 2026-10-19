# 07 — Sandbox de calcul formel

## 7.1 Objectif

Garantir que **tout** résultat mathématique affiché ou validé provient d'un calcul exécuté, pas d'une génération du LLM.

## 7.2 Périmètre fonctionnel

| Domaine | Fonctions SymPy | Exemple |
| --- | --- | --- |
| Calcul littéral | `expand`, `factor`, `simplify`, `collect` | `factor(x**2 - 9)` |
| Équations / inéquations | `solve`, `solveset`, `linsolve`, `reduce_inequalities` | `solveset(3*x+5 - (2*x-7), x)` |
| Analyse | `diff`, `integrate`, `limit`, `series` | `diff(exp(2*x)*sin(x), x)` |
| Trigonométrie | `trigsimp`, `solveset(..., Interval(0, 2*pi))` | |
| Algèbre linéaire | `Matrix`, `det`, `inv`, `rref` | |
| EDO | `dsolve` | `dsolve(f(x).diff(x) - 2*f(x))` |
| Probabilités | `binomial`, `sympy.stats` | |
| Unités physiques | `sympy.physics.units` | conversions km/h → m/s |
| Numérique / graphes | NumPy, Matplotlib (rendu PNG en mémoire) | |

## 7.3 Contrats d'outils

### `sympy_exec`
```json
// entrée
{ "code": "from sympy import *\nx = symbols('x')\nresult = factor(x**2 - 9)", "timeout_ms": 3000 }
// sortie
{ "ok": true, "result_str": "(x - 3)*(x + 3)", "result_latex": "\\left(x - 3\\right) \\left(x + 3\\right)", "stdout": "" }
```

### `verify_step`
```json
// entrée
{ "kind": "expression|equation|solution_set",
  "student": "3x+6-2x+2", "expected": "x+8", "variables": ["x"] }
// sortie
{ "equivalent": true, "student_normalized": "x + 8", "notes": [] }
```
- `expression` : `simplify(student - expected) == 0`, avec repli numérique (évaluation sur points aléatoires) si `simplify` ne conclut pas.
- `equation` : équivalence des ensembles de solutions.
- Le parsing de la saisie élève gère la notation scolaire (`3x`, `2,5`, `·`, `÷`, `√`) via un pré-parseur dédié + `parse_expr` avec transformations implicites.

## 7.4 Sécurité de la sandbox

| Exigence | Mise en œuvre |
| --- | --- |
| Isolation | Conteneur isolé (gVisor, Firecracker ou nsjail), un processus par exécution ou pool recyclé |
| Réseau | Aucun accès réseau |
| Système de fichiers | Lecture seule, `/tmp` en mémoire limité |
| Ressources | Timeout CPU (ex. 3 s), mémoire (ex. 256 Mo), nombre de processus limité |
| Imports | Liste blanche (sympy, numpy, matplotlib, math, fractions) |
| Entrée | Code généré par le LLM uniquement ; jamais de code saisi directement par l'utilisateur |
| Pas de `eval` côté backend | La saisie élève passe par le parseur, jamais par `eval`/`sympify` non contrôlé hors sandbox |

## 7.5 Gestion des échecs

| Cas | Comportement |
| --- | --- |
| Timeout | Retenter une fois avec approche alternative ; sinon le tuteur ne valide pas et le dit |
| Résultat non simplifiable | Vérification numérique ; si doute, formuler prudemment |
| Erreur de code | Le LLM corrige son code (max 2 tentatives) |
| Sandbox indisponible | Mode dégradé : pas de validation d'étape, message explicite |
