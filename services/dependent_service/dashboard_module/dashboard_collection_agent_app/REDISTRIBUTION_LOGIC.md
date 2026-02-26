# 🔄 Logique de Redistribution Automatique des Paiements

## 📋 Vue d'ensemble

Le système gère maintenant automatiquement la redistribution des paiements vers les plans précédents non totalisés, avec copie du `transaction_code` pour la traçabilité.

## ✨ Nouvelles Fonctionnalités

### 1. **Copie du Transaction Code**
Tous les paiements automatiques (surplus et redistribution) copient le `transaction_code` du paiement original.

```python
surplus_payment = Payment(
    # ... autres champs ...
    transaction_code=self.transaction_code,  # ← COPIE DU CODE
    description="Surplus transféré du plan X"
)
```

### 2. **Redistribution Automatique vers Plans Précédents**

Quand un étudiant paie un plan suivant alors que des plans précédents ne sont pas totalisés, le système redistribue automatiquement.

#### Exemple Concret

**Situation :**
- Plan 1 (Première tranche) : 100 000 FCFA - Payé : 70 000 FCFA (reste 30 000)
- Plan 2 (Deuxième tranche) : 150 000 FCFA - Payé : 0 FCFA
- Étudiant paie 50 000 FCFA sur le Plan 2

**Résultat Automatique :**

1. **Détection** : Le système détecte que le Plan 1 n'est pas totalisé
2. **Redistribution** :
   - 30 000 FCFA → Plan 1 (pour le compléter)
   - 20 000 FCFA → Plan 2 (le reste)
3. **Traçabilité** :
   - Paiement original : 50 000 FCFA sur Plan 2 (code: TRX123)
   - Paiement redistribution : 30 000 FCFA sur Plan 1 (code: TRX123)
   - Montant effectif Plan 2 : 20 000 FCFA

## 🔧 Flux Technique

### Étape 1 : Création du Paiement
```python
# L'étudiant ou finance_service crée un paiement
payment = Payment(
    paymentplan=plan_2,
    amount_paid=50000,
    transaction_code="TRX123",
    payment_status="unverified"
)
payment.save()
```

### Étape 2 : Vérification du Paiement
```python
# Finance_service vérifie le paiement
payment.payment_status = "verified"
payment.save()
```

### Étape 3 : Redistribution Automatique
```python
def _update_payment_installment(self, old_amount=0):
    # 1. Vérifier et redistribuer vers plans précédents
    self._redistribute_to_previous_plans(student)

    # 2. Mettre à jour l'échéancier actuel
    # 3. Gérer le surplus vers plan suivant si nécessaire
```

### Étape 4 : Logique de Redistribution
```python
def _redistribute_to_previous_plans(self, student):
    # Trouver tous les plans précédents non totalisés
    previous_unpaid = PaymentInstallement.objects.filter(
        student=student,
        payment_plan__start_date__lt=self.paymentplan.start_date,
        status__in=["pending", "overdue"],
    ).order_by("payment_plan__start_date")

    available_amount = self.amount_paid

    for prev_installment in previous_unpaid:
        if available_amount <= 0:
            break

        remaining = prev_installment.amount - prev_installment.paid_amount
        amount_to_transfer = min(available_amount, remaining)

        # Créer paiement de redistribution avec MÊME transaction_code
        redistribution_payment = Payment(
            paymentplan=prev_installment.payment_plan,
            amount_paid=amount_to_transfer,
            transaction_code=self.transaction_code,  # ← COPIE
            description=f"Redistribution automatique du paiement #{self.id}",
            payment_status="verified",
        )
        redistribution_payment.save(_skip_surplus_handling=True)

        available_amount -= amount_to_transfer

    # Ajuster le montant du paiement actuel
    self.amount_paid = available_amount
```

## 📊 Scénarios d'Utilisation

### Scénario 1 : Paiement avec Plans Précédents Incomplets

**Données :**
- Plan 1 : 100 000 (payé: 60 000, reste: 40 000)
- Plan 2 : 150 000 (payé: 0)
- Plan 3 : 200 000 (payé: 0)
- Paiement : 100 000 sur Plan 3 (code: ABC789)

**Résultat :**
1. 40 000 → Plan 1 (code: ABC789, description: "Redistribution...")
2. 60 000 → Plan 2 (code: ABC789, description: "Redistribution...")
3. 0 → Plan 3 (montant ajusté)

**État Final :**
- Plan 1 : 100 000 / 100 000 ✅ (status: paid)
- Plan 2 : 60 000 / 150 000 (status: pending)
- Plan 3 : 0 / 200 000 (status: pending)

### Scénario 2 : Paiement avec Surplus

**Données :**
- Plan 1 : 100 000 (payé: 100 000) ✅
- Plan 2 : 150 000 (payé: 0)
- Paiement : 180 000 sur Plan 2 (code: XYZ456)

**Résultat :**
1. 150 000 → Plan 2 (paiement original)
2. 30 000 → Plan 3 (code: XYZ456, description: "Surplus transféré...")

**État Final :**
- Plan 2 : 150 000 / 150 000 ✅ (status: paid)
- Plan 3 : 30 000 / 200 000 (status: pending)

### Scénario 3 : Combinaison Redistribution + Surplus

**Données :**
- Plan 1 : 100 000 (payé: 80 000, reste: 20 000)
- Plan 2 : 150 000 (payé: 0)
- Plan 3 : 200 000 (payé: 0)
- Paiement : 200 000 sur Plan 2 (code: DEF123)

**Résultat :**
1. 20 000 → Plan 1 (redistribution, code: DEF123)
2. 150 000 → Plan 2 (montant ajusté)
3. 30 000 → Plan 3 (surplus, code: DEF123)

**État Final :**
- Plan 1 : 100 000 / 100 000 ✅ (status: paid)
- Plan 2 : 150 000 / 150 000 ✅ (status: paid)
- Plan 3 : 30 000 / 200 000 (status: pending)

## 🔍 Traçabilité

Tous les paiements automatiques sont traçables via :

1. **Transaction Code** : Identique au paiement original
2. **Description** : Indique l'origine (redistribution ou surplus)
3. **Logs** : Enregistrement détaillé de chaque opération

### Exemple de Requête pour Tracer

```python
# Trouver tous les paiements liés à un transaction_code
payments = Payment.objects.filter(
    transaction_code="TRX123"
).order_by("paymentplan__start_date")

for payment in payments:
    print(f"Plan: {payment.paymentplan.description}")
    print(f"Montant: {payment.amount_paid}")
    print(f"Description: {payment.description}")
```

## ⚠️ Points Importants

1. **Ordre Chronologique** : La redistribution se fait toujours vers les plans les plus anciens en premier
2. **Atomicité** : Toutes les opérations sont dans une transaction pour garantir la cohérence
3. **Pas de Validation Bloquante** : Les étudiants peuvent maintenant payer n'importe quel plan
4. **Vérification Obligatoire** : La redistribution ne se fait qu'après vérification du paiement
5. **Flag Anti-Récursion** : `_skip_surplus_handling=True` évite les boucles infinies

## 🚀 Avantages

- ✅ Flexibilité pour les étudiants
- ✅ Traçabilité complète via transaction_code
- ✅ Gestion automatique sans intervention manuelle
- ✅ Respect de l'ordre chronologique des plans
- ✅ Prévention des erreurs de saisie
- ✅ Logs détaillés pour audit

## 📝 Modifications Apportées

### Fichier : `models.py`

1. **Nouvelle méthode** : `_redistribute_to_previous_plans()`
2. **Modification** : `_handle_payment_surplus()` - Ajout de `transaction_code`
3. **Suppression** : Validation bloquante dans `save()`

### Fichier : `serializers.py`

1. **Simplification** : `validate()` - Suppression de la validation des plans précédents

## 🧪 Tests Recommandés

1. Payer un plan suivant avec plans précédents incomplets
2. Vérifier que le transaction_code est copié
3. Vérifier la redistribution correcte des montants
4. Tester avec plusieurs plans précédents incomplets
5. Tester la combinaison redistribution + surplus
6. Vérifier les logs de traçabilité
