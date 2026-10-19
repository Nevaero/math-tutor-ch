# 13 — Offre, tarifs & budget

## 13.1 Grille tarifaire

| Offre | Mensuel | Annuel | Équivalence annuelle |
| --- | --- | --- | --- |
| **Tarif standard** | 40 CHF / mois | 400 CHF / an | 10 mois payés : **2 mois offerts** (les vacances scolaires) |
| **Offre de lancement** | 25 CHF / mois | 250 CHF / an | 10 mois payés : 2 mois offerts |
| **Compte autonome 18+** | 30 CHF / mois | 300 CHF / an | 10 mois payés : 2 mois offerts |

Prix TTC, TVA suisse incluse (8,1 %).

### Règles de l'offre

| Règle | Détail |
| --- | --- |
| Périmètre famille | Jusqu'à **3 profils enfants** par abonnement |
| Essai gratuit | **7 jours**, via le mécanisme d'essai des stores (sans engagement, rappel avant la fin) |
| Offre de lancement | **Prix garanti à vie** tant que l'abonnement reste actif, pour un **nombre limité de places** (compteur visible) **[nombre de places à définir]** |
| Résiliation lancement | Un abonné qui résilie perd le tarif de lancement **[à confirmer]** |
| Promotions | Campagne à **chaque rentrée scolaire** (fin août), éventuellement code promo ou offre d'essai prolongée |
| Comptes 18+ | Pas la cible principale ; un·e jeune majeur·e peut aussi **rester sur le compte famille** de ses parents (compte dans les 3 profils) |

Mise en œuvre store : prix de lancement = produit d'abonnement distinct (« lancement ») fermé à la vente quand les places sont épuisées ; les abonnés existants le conservent. Promotions de rentrée = offres promotionnelles / codes d'offre des stores. Le compteur de places doit être **réel** (pas de fausse rareté, loi contre la concurrence déloyale).

## 13.2 Argumentaire

> **40 CHF, c'est le prix moyen d'une heure de cours particulier.**
> Avec Leo et Albert, c'est un mois entier de cours particuliers, 24 h/24 et 7 j/7.

Points d'appui :
- Disponible au moment du blocage (le dimanche soir, la veille du test), pas seulement au créneau du répétiteur.
- Formule annuelle : on ne paie pas les vacances scolaires.
- Hébergé en Suisse, sans revente ni réutilisation des données des enfants.

Points de vigilance (publicité comparative, loi contre la concurrence déloyale) :
- Le « prix moyen d'une heure de cours particulier » doit être **sourcé** (relevé de tarifs à GE et VD, conservé et daté).
- « Cours particuliers 24/24 » : formuler comme une image (« comme un répétiteur disponible 24 h/24 ») et ne pas laisser croire à un humain. Le service doit aussi tenir la promesse de disponibilité (voir [09](09-exigences-non-fonctionnelles.md)).

## 13.3 Revenu net par abonné

Hypothèse : abonnement vendu via l'App Store et Google Play (obligatoire pour un abonnement numérique dans l'app).

| Offre | TTC | HT (÷ 1,081) | Commission store | Net / mois |
| --- | --- | --- | --- | --- |
| Lancement mensuel | 25,00 | 23,13 | 15 % → 3,47 | **≈ 19,66 CHF** |
| Lancement annuel | 20,83 / mois | 19,27 | 15 % → 2,89 | **≈ 16,38 CHF** |
| Standard mensuel | 40,00 | 37,00 | 15 % → 5,55 | **≈ 31,45 CHF** |
| Standard annuel | 33,33 / mois | 30,84 | 15 % → 4,63 | **≈ 26,21 CHF** |

Commission de 15 % = taux réduit des programmes petites entreprises / abonnements longs ; elle peut atteindre **30 %** selon le statut et l'ancienneté de l'abonnement. À vérifier au moment de l'inscription aux stores.

## 13.4 Budget d'inférence

| Paramètre | Valeur |
| --- | --- |
| Budget mensuel au lancement | **500 CHF / mois** (API Infomaniak, éventuellement GPU) |
| GPU dédié | Accepté si nécessaire (qualité ou coût à l'échelle) |

### Modèle de coût à remplir en Phase 0

```
coût_session  = appels_vision × prix_vision
              + Σ tours (tokens_entrée × prix_entrée + tokens_sortie × prix_sortie)
              + embeddings RAG (négligeable)
sessions_max  = 500 CHF / coût_session
coût_abonné   = sessions_par_abonné_par_mois × coût_session
```

Hypothèses de travail à mesurer : ~15–25 tours par session Tuteur, ~4–8 k tokens d'entrée par tour (prompt, profil, RAG, historique de la session), ~8–15 sessions par mois et par famille.

### Règles de pilotage

- **Cible** : coût d'inférence ≤ **15 %** du revenu net par abonné (≈ 3 CHF/mois au tarif de lancement) **[cible à valider]**.
- Le budget de 500 CHF couvre la **bêta et le lancement** ; au-delà, il évolue avec le nombre d'abonnés.
- **Bascule GPU** : un GPU dédié 24 h/24 coûte un montant fixe qui dépasse probablement 500 CHF/mois **[tarifs Infomaniak à vérifier]**. Il ne devient rentable qu'au-delà d'un volume à calculer : comparer coût fixe GPU et coût API au volume réel. Avant ce seuil : API uniquement, ou GPU uniquement aux heures de pointe.
- Leviers d'économie : cache des fiches Copilote pour un même énoncé, profil d'apprentissage transmis en projection courte, historique de session résumé au-delà de N tours, modèle plus petit pour le résumé et le filtre PII.
- Garde-fou : quota d'usage équitable par famille (ex. sessions par jour) pour éviter les abus, sans pénaliser un usage normal **[à définir]**.

## 13.5 Questions ouvertes sur l'offre

1. **Nombre de places** au tarif de lancement à vie ?
2. Un abonné de lancement qui résilie puis revient garde-t-il son tarif ?
3. **Matières incluses** : Leo et Albert dans le même abonnement ? La Phase 2 (langues) sera-t-elle incluse ou en option ?
4. **Mécanique des promotions de rentrée** : réduction sur le premier mois/année, essai prolongé, ou les deux ?
