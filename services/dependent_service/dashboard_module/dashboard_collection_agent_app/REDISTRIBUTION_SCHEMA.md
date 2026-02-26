# 📊 Schéma Visuel - Redistribution Automatique

## Flux Complet de Redistribution

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ÉTUDIANT EFFECTUE UN PAIEMENT                    │
│                                                                     │
│  Paiement: 100 000 FCFA                                            │
│  Plan cible: Plan 2                                                │
│  Transaction Code: TRX123                                          │
│  Status: unverified                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FINANCE SERVICE VÉRIFIE LE PAIEMENT                    │
│                                                                     │
│  payment.payment_status = "verified"                               │
│  payment.save()  ← DÉCLENCHE LA LOGIQUE                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│           _update_payment_installment() EST APPELÉE                 │
│                                                                     │
│  1. _redistribute_to_previous_plans(student)                       │
│  2. Mise à jour de l'échéancier actuel                            │
│  3. _handle_payment_surplus(student, surplus)                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         ÉTAPE 1: REDISTRIBUTION VERS PLANS PRÉCÉDENTS               │
│                                                                     │
│  Recherche des plans précédents non totalisés:                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Plan 1 (Première tranche)                                │     │
│  │ Montant requis: 100 000 FCFA                            │     │
│  │ Montant payé:    70 000 FCFA                            │     │
│  │ Reste à payer:   30 000 FCFA  ← INCOMPLET              │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  Montant disponible: 100 000 FCFA                                 │
│  Montant à transférer: min(100 000, 30 000) = 30 000 FCFA        │
│                                                                     │
│  ✅ Création paiement redistribution:                              │
│     - Montant: 30 000 FCFA                                        │
│     - Plan: Plan 1                                                │
│     - Transaction Code: TRX123  ← COPIÉ                           │
│     - Description: "Redistribution automatique..."                │
│     - Status: verified                                            │
│                                                                     │
│  Montant restant: 100 000 - 30 000 = 70 000 FCFA                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         ÉTAPE 2: MISE À JOUR ÉCHÉANCIER PLAN ACTUEL                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Plan 2 (Deuxième tranche)                               │     │
│  │ Montant requis: 150 000 FCFA                            │     │
│  │ Montant payé:    70 000 FCFA  ← AJUSTÉ                 │     │
│  │ Reste à payer:   80 000 FCFA                            │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  Le paiement original est ajusté à 70 000 FCFA                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              ÉTAPE 3: GESTION DU SURPLUS (si existe)                │
│                                                                     │
│  Si paid_amount > amount requis:                                   │
│    surplus = paid_amount - amount                                  │
│    Transférer vers plan suivant avec même transaction_code         │
│                                                                     │
│  Dans cet exemple: 70 000 < 150 000 → Pas de surplus              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RÉSULTAT FINAL                                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Plan 1: 100 000 / 100 000 ✅ TOTALISÉ                   │     │
│  │   - Paiement 1: 70 000 (ancien)                         │     │
│  │   - Paiement 2: 30 000 (redistribution, code: TRX123)   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ Plan 2: 70 000 / 150 000 ⏳ EN COURS                    │     │
│  │   - Paiement 1: 70 000 (ajusté, code: TRX123)           │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  📝 Traçabilité: 2 paiements avec le même code TRX123              │
└─────────────────────────────────────────────────────────────────────┘
```

## Exemple avec Surplus

```
SITUATION INITIALE:
┌─────────────────────────────────────────────────────────────────┐
│ Plan 1: 100 000 / 100 000 ✅ TOTALISÉ                          │
│ Plan 2: 150 000 / 150 000 ✅ TOTALISÉ                          │
│ Plan 3:   0 000 / 200 000 ⏳ NON PAYÉ                          │
└─────────────────────────────────────────────────────────────────┘

PAIEMENT:
┌─────────────────────────────────────────────────────────────────┐
│ Montant: 180 000 FCFA                                          │
│ Plan cible: Plan 2                                             │
│ Transaction Code: XYZ999                                       │
└─────────────────────────────────────────────────────────────────┘

APRÈS VÉRIFICATION:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Redistribution: Aucun plan précédent incomplet              │
│                                                                 │
│ 2. Plan 2: 180 000 payé > 150 000 requis                      │
│    → Surplus détecté: 30 000 FCFA                             │
│                                                                 │
│ 3. Création paiement surplus:                                  │
│    - Montant: 30 000 FCFA                                     │
│    - Plan: Plan 3                                             │
│    - Transaction Code: XYZ999  ← COPIÉ                        │
│    - Description: "Surplus transféré du plan 2..."            │
└─────────────────────────────────────────────────────────────────┘

RÉSULTAT FINAL:
┌─────────────────────────────────────────────────────────────────┐
│ Plan 2: 150 000 / 150 000 ✅ (plafonné)                        │
│   - Paiement: 180 000 (code: XYZ999)                          │
│                                                                 │
│ Plan 3:  30 000 / 200 000 ⏳                                   │
│   - Paiement: 30 000 (surplus, code: XYZ999)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Exemple Complexe: Redistribution + Surplus

```
SITUATION INITIALE:
┌─────────────────────────────────────────────────────────────────┐
│ Plan 1:  80 000 / 100 000 ⏳ (reste: 20 000)                   │
│ Plan 2:   0 000 / 150 000 ⏳ (reste: 150 000)                  │
│ Plan 3:   0 000 / 200 000 ⏳ (reste: 200 000)                  │
└─────────────────────────────────────────────────────────────────┘

PAIEMENT:
┌─────────────────────────────────────────────────────────────────┐
│ Montant: 200 000 FCFA                                          │
│ Plan cible: Plan 2                                             │
│ Transaction Code: ABC555                                       │
└─────────────────────────────────────────────────────────────────┘

TRAITEMENT:
┌─────────────────────────────────────────────────────────────────┐
│ ÉTAPE 1: Redistribution vers Plan 1                            │
│   - Montant transféré: 20 000 FCFA                            │
│   - Montant restant: 180 000 FCFA                             │
│   - Code: ABC555                                               │
│                                                                 │
│ ÉTAPE 2: Application au Plan 2                                 │
│   - Montant appliqué: 150 000 FCFA                            │
│   - Surplus détecté: 30 000 FCFA                              │
│                                                                 │
│ ÉTAPE 3: Transfert surplus vers Plan 3                         │
│   - Montant transféré: 30 000 FCFA                            │
│   - Code: ABC555                                               │
└─────────────────────────────────────────────────────────────────┘

RÉSULTAT FINAL:
┌─────────────────────────────────────────────────────────────────┐
│ Plan 1: 100 000 / 100 000 ✅ TOTALISÉ                          │
│   - Paiement ancien: 80 000                                    │
│   - Paiement redistribution: 20 000 (code: ABC555)            │
│                                                                 │
│ Plan 2: 150 000 / 150 000 ✅ TOTALISÉ                          │
│   - Paiement ajusté: 150 000 (code: ABC555)                   │
│                                                                 │
│ Plan 3:  30 000 / 200 000 ⏳ EN COURS                          │
│   - Paiement surplus: 30 000 (code: ABC555)                   │
│                                                                 │
│ 📝 3 paiements créés avec le même code ABC555                  │
└─────────────────────────────────────────────────────────────────┘
```

## Légende

```
✅ = Plan totalisé (status: paid)
⏳ = Plan en cours (status: pending/overdue)
← = Copie/Transfert
→ = Direction du flux
```

## Points Clés Visuels

1. **Un seul transaction_code** pour tous les paiements liés
2. **Ordre chronologique** respecté (Plan 1 → Plan 2 → Plan 3)
3. **Redistribution prioritaire** avant application au plan cible
4. **Surplus automatique** vers le plan suivant
5. **Traçabilité complète** via description et transaction_code
