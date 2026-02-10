# Guide d'Affichage des Paiements - Traçabilité Optimale

## 🎯 Stratégie d'Affichage

### Principe de Base
- **PaymentInstallement** = Vue consolidée des paiements VÉRIFIÉS par plan
- **Payment** = Vue détaillée de TOUS les paiements (vérifiés et non vérifiés)

## 📊 Cas d'Usage

### 1. Afficher l'État des Paiements d'un Étudiant (Vue Consolidée)

**Utiliser : PaymentInstallement**

```http
GET /api/payment-installments/?student={student_id}
```

**Réponse :**
```json
{
  "data": [
    {
      "payment_plan": {
        "id": "6b660aab...",
        "description": "Bulletin",
        "total_amount": 10000
      },
      "financial_info": {
        "amount": 10000,
        "paid_amount": 13000,        // ← Paiements vérifiés uniquement
        "remaining_amount": -3000,   // ← Négatif = surplus
        "completion_percentage": 130.0
      },
      "status_info": {
        "status": "paid",
        "status_display": "Payé"
      }
    },
    {
      "payment_plan": {
        "id": "460bcb30...",
        "description": "Inscription",
        "total_amount": 52000
      },
      "financial_info": {
        "amount": 52000,
        "paid_amount": 3000,         // ← Surplus transféré (vérifié)
        "remaining_amount": 49000,
        "completion_percentage": 5.77
      },
      "status_info": {
        "status": "pending",
        "status_display": "En Attente"
      }
    }
  ]
}
```

**Quand l'utiliser :**
- ✅ Dashboard étudiant
- ✅ Vue d'ensemble des plans
- ✅ Calcul des montants dus
- ✅ Statistiques de paiement

---

### 2. Afficher les Paiements en Attente de Vérification

**Utiliser : Payment avec filtre status=unverified**

```http
GET /api/payments/?student={student_id}&payment_status=unverified
```

**Réponse :**
```json
{
  "data": [
    {
      "id": "abc123...",
      "paymentplan_info": {
        "description": "Inscription",
        "total_amount": 52000
      },
      "amount_paid": 20000,
      "payment_date": "2026-02-15",
      "payment_method": "bank_deposit",
      "payment_status": "unverified",  // ← En attente
      "verified_by": null,
      "verified_at": null,
      "remittance_slip": "payment_slips/receipt_123.jpg"
    }
  ]
}
```

**Quand l'utiliser :**
- ✅ Interface du service financier
- ✅ Liste des paiements à vérifier
- ✅ Validation des bordereaux

---

### 3. Afficher l'Historique Complet des Transactions

**Utiliser : Payment (tous les statuts)**

```http
GET /api/payments/?student={student_id}
```

**Réponse :**
```json
{
  "data": [
    {
      "id": "ef4a659a...",
      "paymentplan_info": {
        "description": "Bulletin"
      },
      "amount_paid": 13000,
      "payment_status": "verified",
      "verified_by_info": {
        "first_name": "Edward",
        "last_name": "West",
        "role": "finance_service"
      },
      "verified_at": "2026-02-10T11:14:03Z",
      "description": null
    },
    {
      "id": "d57e1769...",
      "paymentplan_info": {
        "description": "Inscription"
      },
      "amount_paid": 3000,
      "payment_status": "verified",
      "description": "Surplus transféré du plan 6b660aab... (Paiement #ef4a659a...)"
    },
    {
      "id": "abc123...",
      "paymentplan_info": {
        "description": "Inscription"
      },
      "amount_paid": 20000,
      "payment_status": "unverified",
      "verified_by": null,
      "description": null
    }
  ]
}
```

**Quand l'utiliser :**
- ✅ Historique complet
- ✅ Audit et traçabilité
- ✅ Recherche de transactions spécifiques
- ✅ Export comptable

---

## 🎨 Exemples d'Interface Utilisateur

### Dashboard Étudiant

```
┌─────────────────────────────────────────────────────────┐
│ Mes Plans de Paiement                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📋 Plan Bulletin                                        │
│    Montant requis:    10,000 FBU                        │
│    Montant payé:      13,000 FBU ✅                     │
│    Statut: Payé                                         │
│    Surplus: 3,000 FBU → Transféré à Inscription        │
│                                                          │
│ 📋 Plan Inscription                                     │
│    Montant requis:    52,000 FBU                        │
│    Montant payé:       3,000 FBU (surplus reçu)        │
│    Reste à payer:     49,000 FBU                        │
│    Statut: En cours (5.77%)                             │
│                                                          │
│ ⏳ Paiements en attente de vérification                 │
│    • 20,000 FBU - Inscription - 15/02/2026             │
│      [Voir bordereau]                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Interface Service Financier

```
┌─────────────────────────────────────────────────────────┐
│ Paiements à Vérifier (3)                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 🔍 Stephen Cowan (F2025/00005)                          │
│    Plan: Inscription                                    │
│    Montant: 20,000 FBU                                  │
│    Date: 15/02/2026                                     │
│    Méthode: Dépôt bancaire                              │
│    [Voir bordereau] [Vérifier] [Rejeter]               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Flux de Données

```
1. Étudiant crée un Payment
   ↓
   payment_status = "unverified"
   ↓
2. Affichage dans "Paiements en attente"
   (via Payment avec filter status=unverified)
   ↓
3. Service financier vérifie
   ↓
   payment_status = "verified"
   verified_by = user
   verified_at = now()
   ↓
4. Création/Mise à jour PaymentInstallement
   ↓
5. Gestion automatique du surplus
   ↓
6. Affichage dans PaymentInstallement
   (vue consolidée par plan)
```

---

## 📌 Résumé des Endpoints

| Besoin | Endpoint | Filtre |
|--------|----------|--------|
| Vue consolidée par plan | `/api/payment-installments/` | `student={id}` |
| Paiements non vérifiés | `/api/payments/` | `student={id}&payment_status=unverified` |
| Historique complet | `/api/payments/` | `student={id}` |
| Paiements vérifiés | `/api/payments/` | `student={id}&payment_status=verified` |
| Paiements rejetés | `/api/payments/` | `student={id}&payment_status=rejected` |

---

## ✅ Avantages de cette Approche

1. **Séparation claire** : Vérifié vs Non vérifié
2. **Traçabilité complète** : Tous les paiements enregistrés
3. **Vue consolidée** : PaymentInstallement pour l'état global
4. **Vue détaillée** : Payment pour les transactions individuelles
5. **Flexibilité** : Différentes vues pour différents besoins
6. **Audit facile** : Historique complet accessible

---

## 🎯 Bonnes Pratiques

### Pour l'Étudiant
- Afficher **PaymentInstallement** pour voir l'état de ses plans
- Afficher **Payment (unverified)** pour voir ses paiements en attente

### Pour le Service Financier
- Afficher **Payment (unverified)** pour la liste des paiements à vérifier
- Afficher **PaymentInstallement** pour voir l'état global d'un étudiant

### Pour les Rapports
- Utiliser **PaymentInstallement** pour les statistiques par plan
- Utiliser **Payment** pour les rapports de transactions détaillés
