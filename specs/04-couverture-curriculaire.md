# 04 — Couverture curriculaire

> ⚠️ Cette liste est une base de travail. Elle doit être validée par des enseignant·e·s de Genève et de Vaud et alignée sur les moyens d'enseignement romands (MER) et les plans d'études cantonaux du Secondaire II, qui varient selon les cantons.

## 4.1 Cycle 3 (9H–11H) — Mathématiques (PER, domaine MSN)

| Axe PER | Notions | Exemples d'exercices |
| --- | --- | --- |
| Nombres | Entiers relatifs, fractions, puissances, racines, notation scientifique, ensembles ℕ ℤ ℚ ℝ | Comparer, ordonner, calculer avec priorités |
| Opérations / calcul littéral | Réduire, développer, factoriser (mise en évidence, identités remarquables) | `3(x+2) − 2(x−1)` ; `x² − 9` |
| Équations | 1er degré à une inconnue, mise en équation de problèmes, (11H) systèmes simples, inéquations | `3x + 5 = 2x − 7` |
| Fonctions et grandeurs | Proportionnalité, pourcentages, fonctions linéaires et affines, lecture de graphiques | Tarifs, pentes, ordonnée à l'origine |
| Espace (géométrie) | Pythagore, Thalès, isométries, aires et volumes, trigonométrie du triangle rectangle (selon canton) | Calculer une longueur, un angle |
| Grandeurs et mesures | Conversions d'unités, vitesses, masses volumiques | km/h ↔ m/s |
| Statistiques / probabilités | Moyenne, médiane, diagrammes, probabilités simples | Lancer de dés |

**Spécificités cantonales — lancement GE et VD**

Le PER est commun, mais l'organisation du Cycle 3 diffère. Le profil enregistre la voie/section pour régler profondeur et rythme. Structures à **vérifier auprès des départements cantonaux** (elles évoluent avec les réformes) :

| Canton | Établissement | Structure (à vérifier) | Valeur profil |
| --- | --- | --- | --- |
| Vaud | École obligatoire, degré secondaire | Voie prégymnasiale (VP) ; voie générale (VG) avec niveaux 1/2 en maths | `VD-VP`, `VD-VG-N1`, `VD-VG-N2` |
| Genève | Cycle d'orientation (CO) | Regroupements en 9e, puis sections en 10e–11e | `GE-<regroupement/section>` |

Les autres cantons romands seront ajoutés après le lancement ; le modèle de données doit rester générique (canton → liste de voies/niveaux en configuration, pas en code).

Secondaire II : **Gymnase** (VD) et **Collège de Genève** (GE) ; niveaux de maths (standard / renforcé) et options spécifiques à paramétrer de la même façon.

## 4.2 Cycle 3 — Physique (bases)

| Thème | Notions |
| --- | --- |
| Cinématique | Vitesse moyenne, MRU, graphiques distance-temps |
| Grandeurs | Masse, volume, masse volumique, unités SI |
| Énergie (selon canton) | Formes d'énergie, puissance |
| Optique / électricité (selon canton) | Circuits simples, loi d'Ohm |

## 4.3 Secondaire II (Gymnase / Maturité gymnasiale)

| Bloc | Notions | Outils sandbox |
| --- | --- | --- |
| Algèbre | Équations du 2e degré, systèmes, inéquations, valeur absolue | `solve`, `solveset`, `factor` |
| Fonctions | Polynômes, rationnelles, exponentielles, logarithmes, réciproques | `simplify`, `expand_log` |
| Trigonométrie | Cercle trigonométrique, identités, équations trigonométriques, sinus/cosinus dans le triangle quelconque | `trigsimp`, `solveset` sur intervalle |
| Analyse | Limites, continuité, dérivées, étude de fonction, primitives, intégrales définies, aires | `limit`, `diff`, `integrate` |
| Suites | Arithmétiques, géométriques, séries | `summation` |
| Vecteurs / géométrie analytique | Droites, plans, produit scalaire et vectoriel | `Matrix`, `dot`, `cross` |
| Algèbre linéaire (OS) | Matrices, déterminants, systèmes linéaires | `Matrix.det`, `rref` |
| Équations différentielles (OS) | EDO du 1er et 2e ordre linéaires | `dsolve` |
| Probabilités / statistiques | Combinatoire, lois binomiale et normale | `sympy.stats`, `binomial` |
| Physique | Mécanique (cinématique, dynamique, énergie), électricité, ondes | Calcul numérique + unités (`sympy.physics.units`) |

Note : la spec source mentionne « OS Maths-Physique ». Dans le canton de Vaud, c'est une **option spécifique du Cycle 3** (voie prégymnasiale, 9H–11H, objectifs MEP 31–34, document PER VD « Mathématiques et Physique ») : le profil élève vaudois doit pouvoir l'indiquer, et la recherche PER n'inclut ces objectifs que pour ces élèves. Au gymnase, l'équivalent est l'OS « Physique et applications des mathématiques » (PAM).

## 4.4 Référentiel de vocabulaire PER

Le moteur pédagogique s'appuie sur un **glossaire de termes scolaires** (stocké côté serveur, versionné), par degré, pour imposer la terminologie :

| Terme scolaire | Évite | Degré |
| --- | --- | --- |
| Réduire | « simplifier » (ambigu) | 9H+ |
| Développer | « distribuer » | 9H+ |
| Mettre en évidence | « factoriser » (en 9H) | 9H–10H |
| Ensemble des solutions `S = {…}` | « la réponse est » | 9H+ |

Ce glossaire est un livrable à produire avec un·e enseignant·e (voir [11](11-roadmap.md)).

## 4.5 Matériel de référence (RAG)

- **Éphémère** (session) : énoncés photographiés, feuilles d'objectifs.
- **Référentiels officiels** (permanent) : le **PER** (domaine MSN en priorité, puis disciplines utiles à la Phase 2), et pour le Secondaire II les **plans d'études cantonaux** (Gymnase VD, Collège de Genève), le PER s'arrêtant à la 11H. Indexés en recherche hybride, voir [06](06-architecture-technique.md) §6.6.
- **Corpus maison** (permanent) : glossaire PER, fiches de méthode rédigées en interne, pièges fréquents par notion.
- **Exclus** : manuels et moyens d'enseignement (MER, ouvrages d'éditeurs) — protégés par le droit d'auteur, jamais indexés.

### Ingestion du PER

Sources disponibles localement (`per/math/`) : PER v3.0 (août 2024) MSN cycles 1, 2 et 3, et complément VD « Mathématiques et Physique ». Ingestion implémentée dans le PoC (`poc/leo/curriculum/`).


| Étape | Détail |
| --- | --- |
| Source | Site officiel du PER (CIIP). **Conditions d'utilisation et droit de réutilisation à vérifier / autorisation à demander à la CIIP** avant ingestion (voir [08](08-donnees-conformite.md) §8.5) |
| Extraction | Contenu structuré (domaine → discipline → objectif d'apprentissage, ex. MSN 31–35 → progressions d'apprentissage → attentes fondamentales → indications pédagogiques) ; préférer le HTML structuré au PDF |
| Découpage (chunking) | Un chunk = une unité pédagogique (une progression ou une attente fondamentale) avec son contexte hiérarchique en en-tête ; pas de découpage à taille fixe |
| Métadonnées | `cycle`, `degres` (ex. 9H–11H), `domaine`, `discipline`, `code_objectif`, `axe`, `type` (progression / attente / indication), `source_url`, `version_per`, `date_ingestion` |
| Mise à jour | Ré-ingestion planifiée (ex. avant chaque rentrée scolaire), versionnée, avec diff |
| Usages | Identifier la notion PER d'un énoncé, citer l'objectif dans la fiche Copilote, vérifier qu'une notion est au programme du degré, alimenter le glossaire de vocabulaire |
