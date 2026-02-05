# Système de Gestion Automatique des Surplus de Paiement

## Vue d'ensemble

Ce système gère automatiquement les surplus de paiement des étudiants en les transférant vers les plans de paiement suivants. Quand un étudiant paie plus que nécessaire pour un plan, l'excédent est automatiquement appliqué au plan suivant.

## Fonctionnalités Principales

### 1. Détection des Surplus via PaymentInstallement

Le système utilise le modèle `PaymentInstallement` pour détecter les surplus :

1. **Calcul automatique** : `paid_amount` vs `amount` (montant requis)
2. **Propriétés utiles** :
   - `has_surplus` : Booléen indiquant la présence d'un surplus
   - `surplus_amount` : Montant exact du surplus
3. **Détection lors de la vérification** d'un paiement

### 2. Gestion Automatique des Surplus

Lorsqu'un paiement est vérifié (`payment_status = "verified"`), le système :

1. **Met à jour le PaymentInstallement** avec le total des paiements vérifiés
2. **Détecte le surplus** via `installment.paid_amount > installment.amount`
3. **Transfère automatiquement le surplus** vers le plan suivant
4. **Marque le plan comme terminé** si complètement payé
5. **Crée un nouveau paiement identique** pour le surplus

Le système utilise une logique en cascade :
- Trouve le plan suivant chronologiquement
- Applique le surplus disponible
- Si le plan est complètement payé, passe au suivant
- Continue jusqu'à épuisement du surplus

### 3. Traçabilité Complète

Chaque transfert de surplus génère :
- **Un nouveau paiement identique** avec les mêmes données (méthode, banque, bordereau, etc.)
- **Montant différent** : seulement le montant du surplus
- **Plan différent** : assigné au plan suivant chronologiquement
- **Code de transaction modifié** : `_SURPLUS` ajouté
- **Description explicite** : indique la source du transfert
- **Statut vérifié** : automatiquement marqué comme vérifié

## Utilisation

### API Endpoints

#### 1. Vérification de Paiement
```http
PATCH /api/payments/{id}/
Content-Type: application/json

{
    "payment_status": "verified"
}
```

#### 2. Résumé des Paiements d'un Étudiant
```http
GET /api/payments/student_payment_summary/?student_id={uuid}
```

#### 3. Traitement Manuel des Surplus
```http
POST /api/payments/process_surplus_payments/
Content-Type: application/json

{
    "student_id": "uuid-de-l-etudiant"
}
```

#### 4. Liste des Échéanciers avec Surplus
```http
GET /api/payment-installments/installments_with_surplus/
```

### Exemple de Flux

1. **Étudiant paie 150,000 BIF** pour un plan de 100,000 BIF
2. **Système vérifie le paiement** → surplus de 50,000 BIF détecté
3. **Plan actuel marqué comme terminé**
4. **Nouveau paiement créé** :
   - Mêmes données (méthode, banque, bordereau, date)
   - Montant : 50,000 BIF (le surplus)
   - Plan : Plan suivant (ex: 80,000 BIF)
   - Transaction : `CODE_ORIGINAL_SURPLUS`
5. **Plan suivant** a maintenant 50,000 BIF payés sur 80,000 BIF
6. **Deux paiements distincts** dans la base de données pour traçabilité

## Modèles Impliqués

### PaymentPlan
- `status`: "active" → "completed" quand totalement payé
- Méthodes: `get_plans_for_student()`

### PaymentInstallement
- `paid_amount`: Montant total payé pour ce plan
- `status`: Mis à jour automatiquement selon le montant payé

### Payment
- `payment_status`: "verified" déclenche la logique de surplus
- Méthodes: `_handle_payment_surplus()`, `_find_next_payment_plan()`

## Sécurité et Permissions

- **Vérification de paiements** : Seul `finance_service`
- **Consultation** : Étudiants voient leurs propres données
- **Traitement manuel** : Seul `finance_service`

## Messages de Retour

Le système informe automatiquement :
- "Paiement vérifié avec succès. Le surplus éventuel a été automatiquement transféré vers le plan suivant."
- Détails des surplus traités dans les réponses API

## Avantages

1. **Automatisation complète** - Pas d'intervention manuelle nécessaire
2. **Traçabilité parfaite** - Chaque transfert est documenté
3. **Flexibilité** - Gère les surplus multiples et en cascade
4. **Sécurité** - Permissions strictes et validation complète
5. **Transparence** - L'étudiant voit clairement ses paiements et transferts
