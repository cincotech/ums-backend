# Logique de Gestion des Surplus de Paiement

## Vue d'ensemble
Lorsqu'un étudiant paie un montant supérieur au total requis pour un plan de paiement, le surplus est automatiquement transféré vers le plan suivant.

## Flux de Traitement

### 1. Création/Vérification d'un Paiement
```python
# Lors de la sauvegarde d'un Payment avec status="verified"
payment.save()  # Déclenche automatiquement la logique
```

### 2. Mise à Jour du PaymentInstallement
- Calcule le total des paiements vérifiés pour le plan
- Met à jour `paid_amount` dans PaymentInstallement
- Détecte si `paid_amount > amount` (surplus)

### 3. Gestion du Surplus
Si surplus détecté :
1. **Recherche du plan suivant** : Utilise `get_plans_for_student()` avec filtre chronologique
2. **Création/Mise à jour** : Crée ou récupère le PaymentInstallement du plan suivant
3. **Transfert** : Ajoute le surplus au `paid_amount` du plan suivant
4. **Traçabilité** : Crée un Payment automatique avec description explicite

### 4. Transaction Atomique
Toutes les opérations sont encapsulées dans une transaction pour garantir la cohérence.

## Exemple Concret

```python
# Plan 1 : Montant requis = 1000€
# Étudiant paie 1200€
# Surplus = 200€

# Résultat :
# - Plan 1 : paid_amount = 1200€, status = "paid"
# - Plan 2 : paid_amount = 200€ (transféré automatiquement)
# - Payment créé pour traçabilité avec description "Surplus transféré du plan X"
```

## Méthodes Utilitaires

### `get_plan_balance(payment_plan, student)`
Retourne le solde d'un plan :
- **Négatif** : Surplus (trop payé)
- **Positif** : Reste à payer
- **Zéro** : Plan totalisé exactement

```python
balance = Payment.get_plan_balance(plan, student)
if balance < 0:
    print(f"Surplus de {abs(balance)}€")
elif balance > 0:
    print(f"Reste {balance}€ à payer")
```

## Sécurité et Cohérence

✅ **Transactions atomiques** : Rollback automatique en cas d'erreur
✅ **Traçabilité complète** : Chaque surplus génère un Payment
✅ **Pas de duplication** : Utilise `get_or_create` pour les installments
✅ **Recherche hiérarchique** : Réutilise la logique existante de PaymentPlan
✅ **Protection contre récursion** : Flag `_skip_surplus_handling` pour éviter les boucles infinies
✅ **Compatible Django Admin** : Fonctionne automatiquement lors des modifications

## Comportement avec Django Admin

### Modification d'un paiement existant
Lorsque vous modifiez un Payment via Django Admin :

1. **Changement de montant** : Le système recalcule automatiquement le surplus
2. **Changement de statut** : Si vous passez de "unverified" à "verified", le surplus est géré
3. **Mise à jour du surplus** : Si un surplus existe déjà, il est mis à jour (pas de doublon)
4. **Remplissage automatique** : `verified_by` et `verified_at` sont remplis automatiquement

### Exemple de modification
```python
# Via Django Admin, vous modifiez :
# Payment #123 : amount_paid passe de 1000€ à 1200€
# Status : verified

# Résultat automatique :
# - Plan 1 : Recalcul du paid_amount
# - Détection du surplus de 200€
# - Mise à jour ou création du paiement de surplus sur Plan 2
# - Pas de duplication même si vous sauvegardez plusieurs fois
# - verified_by = utilisateur actuel (automatique)
# - verified_at = date/heure actuelle (automatique)
```

### Comportement avec API REST
Lorsque vous utilisez l'API pour créer/modifier un paiement :

```json
// Requête PATCH/PUT
{
  "payment_status": "verified",
  "amount_paid": "13000.00"
}

// Réponse automatique
{
  "payment_status": "verified",
  "verified_by": "<user_id>",  // Rempli automatiquement
  "verified_at": "2025-02-10T14:30:00Z",  // Rempli automatiquement
  // ... surplus géré automatiquement
}
```

### Suppression d'un paiement
La méthode `delete()` recalcule automatiquement tous les installments affectés.

## Notes Importantes

- Le surplus n'est transféré que si un plan suivant existe
- Si pas de plan suivant, le surplus reste sur le plan actuel
- Les paiements de surplus sont automatiquement vérifiés
- La méthode `payment_method` du surplus est "other" pour distinction
