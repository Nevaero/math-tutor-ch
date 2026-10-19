# 08 — Données & conformité

> ⚠️ Ce document décrit des exigences produit. Il ne constitue pas un avis juridique ; une validation par un·e juriste spécialisé·e (nLPD, LDA) est prévue avant lancement.

## 8.1 Principes

1. **Souveraineté** : stockage, traitement et inférence exclusivement en Suisse, chez **Infomaniak**.
2. **Minimisation** : on ne collecte que ce qui est nécessaire au tutorat et au compte.
3. **Aucune PII dans les données pédagogiques** : historique et profil d'apprentissage sont pseudonymes et filtrés.
4. **Éphémérité** des contenus photographiés.
5. **Aucune réutilisation** des données de mineurs pour entraîner ou affiner des modèles.
6. **Contrôle parental** : le parent consent, consulte, exporte, désactive, supprime.

## 8.2 Inventaire des données

| Donnée | Finalité | Stockage | Durée |
| --- | --- | --- | --- |
| E-mail, mot de passe (Argon2id) | Compte parent ou compte autonome 18+ | Base identité (Infomaniak) | Durée du compte |
| Consentements (horodatés, version) | Preuve | Base identité | Durée du compte + délai légal |
| Profil élève : pseudo, avatar, canton, degré, voie/niveau | Personnalisation | Base pédagogie | Durée du compte |
| Photos d'énoncés | Extraction | **Mémoire uniquement** | Purge immédiate après extraction |
| Énoncé extrait + conversation | Session de tutorat | Redis chiffré | TTL de session |
| Résumés de session (sans PII) | Historique | Base pédagogie | Activé par défaut ; **12 mois** après création |
| Profil d'apprentissage (sans PII) | Adaptation du tuteur | Base pédagogie | Entrée supprimée après **12 mois** sans mise à jour ; effaçable à tout moment |
| Données d'abonnement | Facturation | Stores Apple/Google + référence interne | Durée légale comptable |
| Logs techniques | Exploitation | Infomaniak, sans contenu | Ex. 30 jours |

## 8.3 Absence de PII dans les données pédagogiques

**Définition opérationnelle de PII exclue** : nom, prénom, pseudo réel d'un tiers, nom d'école, de classe, d'enseignant·e, lieu précis, adresse, téléphone, e-mail, date de naissance, identifiants de réseaux sociaux, images, voix, et toute information sur la santé, la famille ou la vie privée confiée par l'élève.

| Couche | Mécanisme |
| --- | --- |
| Conception | Profil = pseudo choisi + données scolaires génériques ; pas de prénom réel requis |
| Schéma | Profil d'apprentissage majoritairement en listes fermées (codes de notions, d'erreurs, de style) |
| Filtre avant écriture | Règles (regex : e-mails, téléphones, dates), NER francophone auto-hébergé, puis passe LLM de contrôle ; en cas de doute, le champ est supprimé |
| Prompt | Le tuteur ne demande ni ne répète d'informations personnelles |
| Séparation | Base identité / base pédagogie, liées seulement par un identifiant opaque |
| Contrôle | Tests automatisés avec conversations piégées (l'élève donne son nom, son école…) ; audit périodique d'un échantillon |

Note : même pseudonymisées, ces données restent des **données personnelles** au sens de la nLPD tant qu'elles sont rattachables à un compte. Les droits (accès, rectification, suppression) s'appliquent donc pleinement.

## 8.4 nLPD

| Exigence | Mise en œuvre |
| --- | --- |
| Information | Politique de confidentialité claire, version adaptée aux enfants ; explication de l'historique et de la personnalisation à l'onboarding |
| Protection dès la conception / par défaut (art. 7) | Historique **activé par défaut** : justifier qu'il est nécessaire à la finalité du service (tutorat personnalisé), informer clairement, permettre la désactivation en un geste **[à valider juridiquement]** |
| Analyse d'impact (AIPD, art. 22) | À réaliser avant lancement (données de mineurs + profilage pédagogique + IA) |
| Profilage | Le profil d'apprentissage constitue probablement un profilage : vérifier s'il s'agit d'un « profilage à risque élevé » et les exigences associées **[à valider juridiquement]** |
| Registre des activités de traitement | À tenir |
| Sous-traitants | Contrat de sous-traitance avec Infomaniak, couvrant l'API IA (non-rétention, non-entraînement) |
| Communication à l'étranger | Interdite pour les contenus ; attention aux SDK mobiles (analytics, crash reporting, push) et aux stores |
| Droits des personnes | Accès, export, rectification, suppression depuis l'app |
| Violations de sécurité | Procédure de notification au PFPDT |
| Mineurs | Consentement parental ; l'enfant capable de discernement conserve ses droits **[modalités à clarifier juridiquement]** |
| Comptes 18+ | Pas de consentement parental ; vérification d'âge proportionnée **[à définir]** |

## 8.5 Éphémérité des images (LDA)

Motivation : les énoncés proviennent souvent de manuels protégés par le droit d'auteur.

| Exigence | Mise en œuvre |
| --- | --- |
| Pas d'écriture disque | Upload traité en mémoire ; jamais d'Object Storage pour les images |
| Purge | Libération du buffer après extraction ; pas d'image dans les logs, traces, ni dumps |
| Pas de constitution de corpus | Les énoncés extraits ne sont pas indexés de façon permanente ni réutilisés |
| Résumés | Reformulation de la notion et de la méthode, pas copie intégrale de l'énoncé **[à valider]** |
| Vérifiabilité | Tests automatisés + audit technique démontrant l'absence de persistance |

### Référentiels indexés (PER, plans d'études cantonaux)

Le PER est publié par la CIIP. Avant de l'indexer :
- vérifier ses conditions d'utilisation et si le PER tombe sous l'exception des « actes officiels » (art. 5 LDA) — non acquis, à faire valider par un·e juriste ;
- à défaut, **demander une autorisation écrite à la CIIP** (et aux départements GE/VD pour les plans d'études du Secondaire II) ;
- citer la source (code d'objectif + lien) quand un extrait est affiché, et ne pas republier le référentiel en entier dans l'app.

## 8.6 Sécurité

- Chiffrement en transit (TLS 1.3) et au repos (bases, Redis, sauvegardes).
- Gestion des secrets dédiée ; clés hébergées chez Infomaniak.
- Séparation stricte des données par compte (contrôles d'accès testés).
- Mot de passe parent : Argon2id, limitation des tentatives, réinitialisation par e-mail.
- Tests d'intrusion avant lancement ; programme de divulgation responsable.
