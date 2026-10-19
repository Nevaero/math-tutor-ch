# 02 — Personas & parcours

## Personas

### P1 — Le parent démuni (cœur de cible)
- Parent d'un·e élève de 9H–11H, scolarisé·e lui-même ailleurs (autre canton, autre pays) ou il y a longtemps.
- Veut aider mais craint d'« expliquer faux » ou d'utiliser une méthode différente de l'école.
- Peu de temps le soir ; usage sur smartphone, souvent dans la cuisine, 10–20 min.
- **Besoin** : comprendre rapidement l'exercice, savoir quoi demander à l'enfant, sans lui donner la réponse.

### P2 — L'élève de Cycle 3 (12–15 ans)
- Bloqué sur un exercice, frustré, peu enclin à lire de longs textes.
- Utilise le téléphone familial ou le sien, sous un profil créé par le parent.
- **Besoin** : être débloqué vite, se sentir capable, sans être jugé.

### P3 — Le/la gymnasien·ne (15–19 ans)
- Maths niveau standard ou renforcé, parfois OS Physique et applications des mathématiques.
- Plus autonome, cherche à vérifier une démarche ou comprendre une étape de calcul (dérivée, intégrale, matrice).
- Parents souvent incapables d'aider à ce niveau.
- Mineur·e : profil rattaché au compte famille. **Majeur·e (18+)** : peut créer son propre compte autonome, sans parent.
- **Besoin** : un tuteur exigeant, rigoureux sur la notation, qui vérifie ses étapes.

### P4 — Le parent prescripteur / payeur
- Gère le compte, l'abonnement, les profils, le consentement.
- **Besoin** : confiance (données en Suisse, pas de triche), visibilité légère sur l'usage.

## Parcours clés

### J1 — Onboarding famille
1. Téléchargement, création du compte parent (e-mail + mot de passe ou passkey).
2. Lecture et acceptation de la politique de confidentialité ; consentement explicite pour les profils de mineurs.
3. Création d'un ou plusieurs profils enfants : **pseudo** (pas de prénom réel exigé), avatar, canton (GE/VD), degré (9H, 10H, 11H, 1re–4e du secondaire II), voie/section/niveau (voir [04](04-couverture-curriculaire.md) §4.1).
4. Information claire : l'historique est **activé par défaut** pour personnaliser le tutorat, sans donnée identifiante ; le parent peut le désactiver ou l'effacer à tout moment.
5. Démo guidée sur un exercice exemple.

### J1bis — Onboarding gymnasien·ne majeur·e
1. Création d'un compte individuel avec déclaration d'âge (18+) **[mode de vérification à définir]**.
2. Mêmes étapes que J1, sans profil parent ; l'utilisateur·rice a accès aux deux modes et gère seul·e son historique.

### J2 — Mode Copilote Parent
1. Le parent ouvre le mode Copilote en saisissant le **mot de passe parent**, puis sélectionne le profil de l'enfant concerné (fixe le niveau et le vocabulaire).
2. Il photographie la consigne (et éventuellement la feuille d'objectifs).
3. L'app affiche l'énoncé reconnu ; le parent corrige si besoin.
4. L'app restitue une **fiche Copilote** : notion visée, déroulé pédagogique, étapes clés, pièges fréquents, 2–3 questions d'amorçage.
5. Le parent peut demander « explique-moi cette étape » ou « et si mon enfant répond X ? ».
6. Fin de session : purge de la photo ; résumé texte sans PII ajouté à l'historique du profil (sauf si désactivé).

### J3 — Mode Tuteur Socratique (Élève)
1. L'élève ouvre son profil (sans mot de passe ; seul le mode Copilote est verrouillé).
2. Photographie l'exercice ou le tape.
3. Validation de l'énoncé reconnu.
4. Le tuteur, qui connaît le profil d'apprentissage de l'élève (niveau, difficultés passées, façon de s'exprimer), demande d'abord ce que l'élève a déjà essayé.
5. Dialogue par petites étapes ; chaque étape proposée par l'élève est vérifiée (via sandbox).
6. Si l'élève demande la réponse, le tuteur refuse avec bienveillance et propose un indice gradué.
7. Clôture : récapitulatif de la méthode (pas de la solution chiffrée si non trouvée par l'élève).

### J4 — Vérification de démarche (Secondaire II)
1. L'élève photographie **sa propre résolution** manuscrite.
2. Le tuteur identifie la première étape erronée, sans la corriger : il pose une question qui amène l'élève à la trouver.
3. Les étapes justes sont confirmées explicitement.

### J5 — Gestion du compte
- Ajout / suppression de profils, export et suppression des données, gestion de l'abonnement, consultation de l'historique et du profil d'apprentissage, désactivation / effacement de l'historique. Toutes ces actions exigent le mot de passe parent.
