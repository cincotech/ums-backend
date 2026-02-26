# 📊 Schémas Visuels - Règles de Surplus

## Scénario 1 : Surplus Vérifié Automatiquement

```
┌─────────────────────────────────────────────────────────────────┐
│ SITUATION INITIALE                                              │
├─────────────────────────────────────────────────────────────────┤
│ Plan 2: 150 000 / 150 000 ✅ TOTALISÉ                          │
│ Plan 3:   0 000 / 200 000 ⏳ AUCUN PAIEMENT                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PAIEMENT VÉRIFIÉ                                                │
├─────────────────────────────────────────────────────────────────┤
│ Montant: 180 000 FCFA                                          │
│ Plan: Plan 2                                                   │
│ Transaction Code: TRX123                                       │
│ Status: verified ✅                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DÉTECTION SURPLUS                                               │
├─────────────────────────────────────────────────────────────────┤
│ Surplus = 180 000 - 150 000 = 30 000 FCFA                     │
│ Plan suivant: Plan 3 ✅ TROUVÉ                                 │
│ Paiements non vérifiés sur Plan 3: ❌ AUCUN                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CRÉATION SURPLUS VÉRIFIÉ                                        │
├─────────────────────────────────────────────────────────────────┤
│ ✅ Paiement Surplus:                                            │
│    - Montant: 30 000 FCFA                                      │
│    - Plan: Plan 3                                              │
│    - Transaction Code: TRX123 (copié)                          │
│    - Status: verified ✅                                       │
│    - verified_by: [finance_service]                            │
│    - verified_at: [timestamp]                                  │
│    - Description: "Surplus transféré du plan 2..."            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RÉSULTAT FINAL                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Plan 2: 150 000 / 150 000 ✅                                   │
│   └─ Paiement: 180 000 (TRX123, verified)                     │
│                                                                 │
│ Plan 3:  30 000 / 200 000 ⏳                                   │
│   └─ Paiement: 30 000 (TRX123, verified) ✅ AUTO              │
└─────────────────────────────────────────────────────────────────┘
```

## Scénario 2 : Surplus Non Vérifié (Paiements Non Vérifiés Existants)

```
┌─────────────────────────────────────────────────────────────────┐
│ SITUATION INITIALE                                              │
├─────────────────────────────────────────────────────────────────┤
│ Plan 2: 150 000 / 150 000 ✅ TOTALISÉ                          │
│ Plan 3:   0 000 / 200 000 ⏳                                   │
│   └─ Paiement: 50 000 (unverified) ⚠️                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PAIEMENT VÉRIFIÉ                                                │
├─────────────────────────────────────────────────────────────────┤
│ Montant: 180 000 FCFA                                          │
│ Plan: Plan 2                                                   │
│ Transaction Code: TRX456                                       │
│ Status: verified ✅                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DÉTECTION SURPLUS                                               │
├─────────────────────────────────────────────────────────────────┤
│ Surplus = 180 000 - 150 000 = 30 000 FCFA                     │
│ Plan suivant: Plan 3 ✅ TROUVÉ                                 │
│ Paiements non vérifiés sur Plan 3: ✅ OUI (50 000)            │
│                                                                 │
│ ⚠️ RÈGLE: Si paiements non vérifiés existent,                 │
│           le surplus sera aussi non vérifié                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CRÉATION SURPLUS NON VÉRIFIÉ                                    │
├─────────────────────────────────────────────────────────────────┤
│ ⚠️ Paiement Surplus:                                            │
│    - Montant: 30 000 FCFA                                      │
│    - Plan: Plan 3                                              │
│    - Transaction Code: TRX456 (copié)                          │
│    - Status: unverified ⚠️                                     │
│    - verified_by: None                                         │
│    - verified_at: None                                         │
│    - Description: "Surplus transféré du plan 2..."            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RÉSULTAT FINAL                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Plan 2: 150 000 / 150 000 ✅                                   │
│   └─ Paiement: 180 000 (TRX456, verified)                     │
│                                                                 │
│ Plan 3:   0 000 / 200 000 ⏳                                   │
│   ├─ Paiement 1: 50 000 (unverified) ⚠️                       │
│   └─ Paiement 2: 30 000 (TRX456, unverified) ⚠️ AUTO          │
│                                                                 │
│ 📝 Finance doit vérifier les 2 paiements manuellement          │
└─────────────────────────────────────────────────────────────────┘
```

## Scénario 3 : Surplus sur Dernier Plan

```
┌─────────────────────────────────────────────────────────────────┐
│ SITUATION INITIALE                                              │
├─────────────────────────────────────────────────────────────────┤
│ Plan 1: 100 000 / 100 000 ✅                                   │
│ Plan 2: 150 000 / 150 000 ✅                                   │
│ Plan 3: 200 000 / 200 000 ✅ DERNIER PLAN                      │
│ [Aucun Plan 4]                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PAIEMENT VÉRIFIÉ                                                │
├─────────────────────────────────────────────────────────────────┤
│ Montant: 250 000 FCFA                                          │
│ Plan: Plan 3 (dernier)                                         │
│ Transaction Code: XYZ789                                       │
│ Status: verified ✅                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DÉTECTION SURPLUS                                               │
├─────────────────────────────────────────────────────────────────┤
│ Surplus = 250 000 - 200 000 = 50 000 FCFA                     │
│ Plan suivant: ❌ AUCUN (dernier plan)                          │
│                                                                 │
│ 🛑 RÈGLE: Pas de plan suivant = Surplus reste sur le plan      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ AUCUN PAIEMENT CRÉÉ                                             │
├─────────────────────────────────────────────────────────────────┤
│ ℹ️ Le surplus reste visible dans paid_amount                   │
│ ℹ️ Aucun nouveau paiement n'est créé                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RÉSULTAT FINAL                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Plan 3: 250 000 / 200 000 ✅                                   │
│   └─ Paiement: 250 000 (XYZ789, verified)                     │
│                                                                 │
│ 💰 Surplus de 50 000 reste sur le plan                         │
│ 📊 paid_amount = 250 000 (> amount requis)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Arbre de Décision

```
                    ┌─────────────────────┐
                    │ Surplus Détecté?    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Chercher Plan       │
                    │ Suivant             │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐          ┌────────▼────────┐
        │ Plan Trouvé?   │          │ Pas de Plan     │
        │ OUI            │          │ (Dernier Plan)  │
        └───────┬────────┘          └────────┬────────┘
                │                            │
                │                    ┌───────▼────────┐
                │                    │ Surplus Reste  │
                │                    │ sur Plan Actuel│
                │                    └────────────────┘
                │
    ┌───────────▼───────────┐
    │ Vérifier Paiements    │
    │ Non Vérifiés?         │
    └───────────┬───────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────────┐      ┌──────▼──────┐
│ Aucun      │      │ Au Moins Un │
│ Unverified │      │ Unverified  │
└───┬────────┘      └──────┬──────┘
    │                      │
┌───▼────────┐      ┌──────▼──────┐
│ Créer      │      │ Créer       │
│ Surplus    │      │ Surplus     │
│ VERIFIED ✅│      │ UNVERIFIED ⚠│
└────────────┘      └─────────────┘
```

## Légende

```
✅ = Vérifié automatiquement
⚠️ = Nécessite vérification manuelle
🛑 = Action bloquée/non effectuée
💰 = Surplus visible mais non transféré
📝 = Action requise du service financier
📊 = Information de traçabilité
ℹ️ = Information
```

## Comparaison Avant/Après

### AVANT (Ancienne Logique)
```
Surplus détecté → Toujours créé avec status="verified"
Problème: Incohérence si le plan suivant a des paiements non vérifiés
```

### APRÈS (Nouvelle Logique)
```
Surplus détecté → Vérifier état du plan suivant
                ↓
    ┌───────────┴───────────┐
    │                       │
Aucun unverified    Au moins 1 unverified
    │                       │
status="verified"    status="unverified"
```

## Cas d'Usage Réels

### Cas 1 : Étudiant Paie en Avance
```
Étudiant paie 200 000 sur Plan 2 (requis: 150 000)
Plan 3 n'a aucun paiement
→ Surplus de 50 000 créé avec status="verified" ✅
→ Étudiant voit immédiatement le crédit sur Plan 3
```

### Cas 2 : Étudiant Paie Plusieurs Fois
```
Étudiant paie 100 000 sur Plan 3 (unverified)
Puis paie 200 000 sur Plan 2 (surplus: 50 000)
→ Surplus de 50 000 créé avec status="unverified" ⚠️
→ Finance doit vérifier les 2 paiements ensemble
```

### Cas 3 : Dernier Plan de l'Année
```
Étudiant paie 250 000 sur Plan 3 (dernier plan, requis: 200 000)
Pas de Plan 4
→ Surplus de 50 000 reste sur Plan 3 💰
→ Peut être remboursé ou reporté à l'année suivante
```
