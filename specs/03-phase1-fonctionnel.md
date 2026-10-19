# 03 — Spécifications fonctionnelles Phase 1

Priorités : **M** = Must (MVP), **S** = Should, **C** = Could.

## 3.1 Comptes et profils

| ID | User story | Prio |
| --- | --- | --- |
| CPT-01 | En tant que parent, je crée un compte famille avec e-mail vérifié. | M |
| CPT-02 | En tant que parent, je crée jusqu'à N profils enfants (pseudo, degré, canton GE/VD, voie/section). | M |
| CPT-03 | En tant que parent, je donne un consentement explicite et horodaté pour chaque profil mineur. | M |
| CPT-04 | En tant que parent, je peux désactiver l'historique d'un profil (activé par défaut) et l'effacer. | M |
| CPT-05 | En tant que parent, j'exporte ou supprime toutes les données d'un profil ou du compte. | M |
| CPT-06 | Le mode Copilote et les réglages du compte sont protégés par le **mot de passe parent**. | M |
| CPT-07 | Déverrouillage du mode Copilote par biométrie du parent. | S |
| CPT-08 | En tant que gymnasien·ne majeur·e, je crée un compte autonome sans parent. | M |

**Critères d'acceptation clés**
- CPT-03 : sans consentement, aucun profil enfant ne peut lancer de session.
- CPT-05 : la suppression est effective sur tous les stockages (y compris sauvegardes, selon un délai documenté) ; confirmation envoyée par e-mail.
- CPT-06 : le mot de passe est redemandé à chaque entrée dans le mode Copilote (ou après N minutes d'inactivité) ; verrouillage temporaire après plusieurs échecs ; le retour au profil enfant reverrouille le mode. Le mot de passe parent est distinct de tout code utilisé par l'enfant.
- CPT-07 : la biométrie doit être celle enregistrée sur l'appareil ; si l'enfant y a aussi enregistré son empreinte, l'option doit être déconseillée **[point d'attention]**.
- CPT-08 : un compte autonome n'a pas de mode « profils » ; l'utilisateur·rice accède directement aux deux modes.

## 3.2 Capture et compréhension de l'énoncé

| ID | User story | Prio |
| --- | --- | --- |
| CAP-01 | Je photographie un énoncé papier (imprimé ou manuscrit). | M |
| CAP-02 | Je recadre / pivote la photo avant envoi. | M |
| CAP-03 | Je vois l'énoncé reconnu (texte + formules rendues) et je peux le corriger. | M |
| CAP-04 | Je saisis un énoncé au clavier avec un éditeur de formules simple. | M |
| CAP-05 | La reconnaissance gère schémas géométriques (figures, angles, longueurs) et graphiques (axes, courbes, tableaux de valeurs). | S |
| CAP-06 | Je photographie plusieurs pages (énoncé + feuille d'objectifs) dans une même session. | S |
| CAP-07 | Je sélectionne un exercice précis sur une page qui en contient plusieurs. | M |

**Critères d'acceptation clés**
- CAP-03 : l'utilisateur doit valider l'énoncé avant que le tutorat démarre (évite de travailler sur un énoncé mal lu).
- Image floue / illisible → message explicite et conseils de prise de vue, sans appel au LLM.
- La photo n'est jamais affichée dans l'historique et n'est jamais persistée (voir [08](08-donnees-conformite.md)).

## 3.3 Mode Copilote Parent

| ID | User story | Prio |
| --- | --- | --- |
| COP-01 | Je reçois une fiche structurée : notion PER visée, prérequis, déroulé, étapes clés, pièges fréquents. | M |
| COP-02 | Je reçois 2–3 questions d'amorçage à poser à mon enfant, formulées pour son âge. | M |
| COP-03 | Je vois la solution complète **pour moi**, repliée par défaut, avec vérification sandbox. | M |
| COP-04 | Je pose des questions de suivi (« pourquoi cette étape ? », « s'il répond X ? »). | M |
| COP-05 | J'obtiens le vocabulaire « comme à l'école » (ex. « réduire », « développer », « mettre en évidence »). | M |
| COP-06 | J'obtiens une explication alternative si mon enfant ne comprend pas la première. | S |
| COP-07 | J'obtiens un exercice similaire d'entraînement (généré + vérifié par la sandbox). | C |

**Format de la fiche Copilote**

```
Notion       : <intitulé PER> — <degré>
Prérequis    : <2–4 points>
Déroulé      : <étapes numérotées, verbes d'action PER>
Pièges       : <erreurs typiques>
Questions    : 1. ... 2. ... 3. ...
Solution     : [repliée] étapes + résultat vérifié ✓
```

## 3.4 Mode Tuteur Socratique

| ID | User story | Prio |
| --- | --- | --- |
| TUT-01 | Le tuteur me demande ce que j'ai compris / essayé avant de m'aider. | M |
| TUT-02 | Le tuteur découpe le problème en sous-étapes et me fait avancer une étape à la fois. | M |
| TUT-03 | Chaque étape que je propose est vérifiée (juste / faux / partiellement juste) via calcul formel. | M |
| TUT-04 | Si je demande la réponse, le tuteur refuse et me propose un indice gradué (3 niveaux). | M |
| TUT-05 | Je peux répondre par texte, éditeur de formules ou photo de mon brouillon. | M (texte/formules), S (photo) |
| TUT-06 | Le tuteur s'adapte à mon degré (vocabulaire, notation, longueur des messages). | M |
| TUT-07 | En fin de session, je reçois un récapitulatif de la méthode. | M |
| TUT-08 | Je fais vérifier ma résolution complète (J4) : le tuteur pointe la première erreur par une question. | S |
| TUT-09 | Dictée vocale de mes réponses. | C |

**Critères d'acceptation clés**
- TUT-04 : le résultat final n'apparaît jamais dans un message du tuteur tant que l'élève ne l'a pas proposé lui-même (contrôle par filtre de sortie, voir [05](05-moteur-pedagogique.md)).
- TUT-03 : la vérification d'équivalence passe par la sandbox (`simplify(a - b) == 0` ou équivalent), pas par le jugement du LLM.
- Indices gradués : 1 = rappel de notion, 2 = piste de méthode, 3 = première étape partiellement amorcée. Jamais de niveau 4 = solution.

## 3.5 Rendu mathématique

| ID | Exigence | Prio |
| --- | --- | --- |
| REN-01 | Rendu LaTeX des formules dans tous les messages. | M |
| REN-02 | Notation suisse romande : virgule décimale, `·` pour la multiplication si l'école l'utilise, unités SI. | M |
| REN-03 | Éditeur de formules adapté au mobile (fractions, puissances, racines, π, intégrales). | M |
| REN-04 | Tracé de graphes de fonctions générés par la sandbox (image ou rendu natif). | S |
| REN-05 | Figures géométriques simples générées. | C |

## 3.6 Historique et personnalisation (activé par défaut)

| ID | User story | Prio |
| --- | --- | --- |
| HIS-01 | Le parent voit la liste des sessions par profil : date, notion, mode, durée, autonomie (indices utilisés). | M |
| HIS-02 | Le contenu conservé est un **résumé texte sans PII** (notion, méthode, erreurs commises), jamais la photo. | M |
| HIS-03 | Rétention de **12 mois** : chaque résumé est supprimé automatiquement 12 mois après sa création ; une entrée du profil d'apprentissage non mise à jour depuis 12 mois est supprimée. | M |
| HIS-04 | Le tuteur s'appuie sur un **profil d'apprentissage** pour s'adapter : niveau réel par notion, erreurs récurrentes, rythme, longueur de réponse tolérée, vocabulaire et façon de s'exprimer de l'élève, type d'indices efficaces. | M |
| HIS-05 | Le tuteur fait référence aux sessions passées (« la dernière fois, tu avais bloqué sur la mise en évidence… »). | M |
| HIS-06 | Le parent consulte le profil d'apprentissage en langage clair et peut corriger ou effacer une entrée. | S |
| HIS-07 | Vue « notions à retravailler » pour le parent. | C |

**Critères d'acceptation clés**
- HIS-02/HIS-04 : aucune donnée identifiante n'est stockée dans l'historique ou le profil d'apprentissage : pas de nom, prénom, école, enseignant·e, adresse, lieu, téléphone, e-mail, date de naissance, ni de détails de la vie privée mentionnés par l'élève (famille, santé…). Un filtre de pseudonymisation est appliqué **avant** toute écriture (voir [08](08-donnees-conformite.md) §8.3).
- HIS-04 : la « façon de s'exprimer » est stockée comme **descripteurs de style** (ex. « messages courts », « répond souvent par une seule expression », « préfère des exemples concrets »), pas comme des extraits verbatim des messages de l'élève.
- Le profil d'apprentissage est structuré (schéma défini en [05](05-moteur-pedagogique.md) §5.5), pas un texte libre accumulé.
- Historique désactivé → les sessions sont oubliées à la fin, le tuteur ne s'appuie que sur le degré et la voie du profil.

## 3.7 Assistants et abonnement

| ID | User story | Prio |
| --- | --- | --- |
| AST-01 | Je choisis mon assistant (Leo en 1a ; Albert en 1b) depuis l'écran d'accueil. | M |
| AST-02 | Si je photographie un exercice d'une autre matière, l'app me propose l'assistant adapté. | S |
| ABO-01 | En tant que parent, je m'abonne au mois (40 CHF) ou à l'année (400 CHF) via l'App Store / Google Play. | M |
| ABO-02 | Pendant la période de lancement, je vois et j'obtiens le tarif de lancement (25 CHF/mois, 250 CHF/an), garanti à vie, avec le nombre de places restantes affiché. | M |
| ABO-03 | Je vois clairement le prix, la date de renouvellement et comment résilier. | M |
| ABO-04 | Mon abonnement est reconnu sur tous les appareils de la famille. | M |
| ABO-05 | Je profite d'un essai gratuit de 7 jours, avec rappel avant la fin. | M |
| ABO-06 | Un abonnement famille couvre jusqu'à 3 profils enfants. | M |
| ABO-07 | En tant que majeur·e, je m'abonne seul·e (30 CHF/mois, 300 CHF/an) ou je reste sur le compte de mes parents. | M |

Détails : [13](13-offre-tarifs.md), [14](14-assistants.md). Les achats et la gestion d'abonnement exigent le mot de passe parent.

## 3.8 Garde-fous de contenu

| ID | Exigence | Prio |
| --- | --- | --- |
| GF-01 | Le tuteur reste dans le périmètre scolaire Maths/Physique ; les demandes hors sujet sont recadrées poliment. | M |
| GF-02 | Détection de signaux de détresse (harcèlement, idées noires) → message bienveillant + orientation (147 Pro Juventute). | M |
| GF-03 | Le tuteur ne demande jamais de données personnelles (nom, école, adresse…) et, si l'élève en donne, ne les reprend pas et ne les mémorise pas. | M |
| GF-04 | Détection de situations d'examen (« j'ai un test en ligne maintenant ») → refus. | S |
