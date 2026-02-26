# 🔄 Règles de Gestion des Surplus - Version Finale

## 📋 Nouvelles Règles Implémentées

### 1. **Copie du Transaction Code** ✅
Tous les paiements automatiques (surplus et redistribution) copient le `transaction_code` du paiement original.

### 2. **Redistribution Automatique vers Plans Précédents** ✅
Quand un paiement est vérifié pour un plan suivant alors que des plans précédents ne sont pas totalisés, le système redistribue automatiquement.

### 3. **Statut Conditionnel du Surplus** ✅ NOUVEAU
Le paiement de surplus créé automatiquement aura un statut qui dépend de l'état du plan suivant :
- **verified** : Si le plan suivant n'a AUCUN paiement non vérifié
- **unverified** : Si le plan suivant a AU MOINS UN paiement non vérifié

### 4. **Dernier Plan** ✅ NOUVEAU
Si le paiement vérifié génère un surplus et qu'il n'y a pas de plan suivant (dernier plan), le surplus reste sur le plan actuel.

## 🎯 Logique Détaillée

### Scénario 1 : Surplus vers Plan Suivant (Sans Paiements Non Vérifiés)

```
SITUATION:
Plan 1: 100 000 / 100 000 ✅ (totalisé)
Plan 2: 150 000 / 150 000 ✅ (totalisé)
Plan 3:   0 000 / 200 000 ⏳ (aucun paiement)

PAIEMENT:
- Montant: 180 000 FCFA
- Plan: Plan 2
- Transaction Code: TRX123
- Status: unverified → verified

TRAITEMENT:
1. Détection surplus: 180 000 - 150 000 = 30 000
2. Recherche plan suivant: Plan 3 trouvé
3. Vérification paiements non vérifiés sur Plan 3: AUCUN
4. Création paiement surplus:
   - Montant: 30 000
   - Plan: Plan 3
   - Transaction Code: TRX123
   - Status: verified ✅ (car aucun paiement non vérifié)
   - verified_by: [finance_service]
   - verified_at: [timestamp]

RÉSULTAT:
Plan 2: 150 000 / 150 000 ✅
Plan 3:  30 000 / 200 000 ⏳ (surplus vérifié automatiquement)
```

### Scénario 2 : Surplus vers Plan Suivant (Avec Paiements Non Vérifiés)

```
SITUATION:
Plan 1: 100 000 / 100 000 ✅ (totalisé)
Plan 2: 150 000 / 150 000 ✅ (totalisé)
Plan 3:  50 000 / 200 000 ⏳ (1 paiement de 50 000 unverified)

PAIEMENT:
- Montant: 180 000 FCFA
- Plan: Plan 2
- Transaction Code: TRX456
- Status: unverified → verified

TRAITEMENT:
1. Détection surplus: 180 000 - 150 000 = 30 000
2. Recherche plan suivant: Plan 3 trouvé
3. Vérification paiements non vérifiés sur Plan 3: OUI (50 000 unverified)
4. Création paiement surplus:
   - Montant: 30 000
   - Plan: Plan 3
   - Transaction Code: TRX456
   - Status: unverified ⚠️ (car paiement non vérifié existe)
   - verified_by: None
   - verified_at: None

RÉSULTAT:
Plan 2: 150 000 / 150 000 ✅
Plan 3:   0 000 / 200 000 ⏳ (2 paiements non vérifiés: 50k + 30k)

NOTE: Le service financier devra vérifier les 2 paiements manuellement
```

### Scénario 3 : Surplus sur Dernier Plan

```
SITUATION:
Plan 1: 100 000 / 100 000 ✅ (totalisé)
Plan 2: 150 000 / 150 000 ✅ (totalisé)
Plan 3: 200 000 / 200 000 ✅ (totalisé)
[Aucun Plan 4]

PAIEMENT:
- Montant: 250 000 FCFA
- Plan: Plan 3
- Transaction Code: XYZ789
- Status: unverified → verified

TRAITEMENT:
1. Détection surplus: 250 000 - 200 000 = 50 000
2. Recherche plan suivant: AUCUN (dernier plan)
3. Le surplus reste sur Plan 3

RÉSULTAT:
Plan 3: 250 000 / 200 000 ✅ (surplus de 50 000 reste sur le plan)

NOTE: Le surplus de 50 000 reste visible dans paid_amount
```

### Scénario 4 : Redistribution + Surplus avec Statut Conditionnel

```
SITUATION:
Plan 1:  80 000 / 100 000 ⏳ (reste: 20 000)
Plan 2:   0 000 / 150 000 ⏳ (aucun paiement)
Plan 3:  40 000 / 200 000 ⏳ (1 paiement de 40 000 unverified)

PAIEMENT:
- Montant: 200 000 FCFA
- Plan: Plan 2
- Transaction Code: ABC999
- Status: unverified → verified

TRAITEMENT:
1. Redistribution vers Plan 1:
   - 20 000 → Plan 1 (code: ABC999, verified)
   - Montant restant: 180 000

2. Application au Plan 2:
   - 150 000 → Plan 2 (ajusté)
   - Surplus détecté: 30 000

3. Transfert surplus vers Plan 3:
   - Vérification: Plan 3 a 1 paiement unverified
   - Création: 30 000 → Plan 3 (code: ABC999, unverified ⚠️)

RÉSULTAT:
Plan 1: 100 000 / 100 000 ✅ (redistribution verified)
Plan 2: 150 000 / 150 000 ✅ (paiement ajusté verified)
Plan 3:   0 000 / 200 000 ⏳ (2 paiements unverified: 40k + 30k)

NOTE: Finance doit vérifier les 2 paiements sur Plan 3
```

## 🔑 Règles de Décision

### Pour le Surplus

```python
# Pseudo-code de la logique
if surplus_detected:
    next_plan = find_next_plan()

    if next_plan is None:
        # DERNIER PLAN: Surplus reste sur le plan actuel
        log("Surplus reste sur le plan actuel (dernier plan)")
        return

    has_unverified = check_unverified_payments(next_plan)

    if has_unverified:
        # Plan suivant a des paiements non vérifiés
        create_surplus_payment(status="unverified")
    else:
        # Plan suivant n'a pas de paiements non vérifiés
        create_surplus_payment(status="verified")
```

## 📊 Tableau Récapitulatif

| Situation | Plan Suivant Existe? | Paiements Non Vérifiés? | Statut Surplus | Action |
|-----------|---------------------|------------------------|----------------|---------|
| Surplus détecté | ✅ Oui | ❌ Non | verified | Surplus vérifié automatiquement |
| Surplus détecté | ✅ Oui | ✅ Oui | unverified | Finance doit vérifier manuellement |
| Surplus détecté | ❌ Non (dernier plan) | N/A | N/A | Surplus reste sur le plan actuel |

## 🎯 Avantages de cette Approche

1. **Cohérence** : Si un plan a des paiements non vérifiés, tous les paiements restent non vérifiés
2. **Contrôle** : Le service financier garde le contrôle sur la vérification
3. **Traçabilité** : Tous les paiements liés partagent le même transaction_code
4. **Flexibilité** : Gère le cas du dernier plan sans créer de paiement inutile
5. **Sécurité** : Évite la vérification automatique quand il y a des doutes

## ⚠️ Points d'Attention

1. **Dernier Plan** : Le surplus reste visible dans `paid_amount` mais ne crée pas de nouveau paiement
2. **Vérification Manuelle** : Si le plan suivant a des paiements non vérifiés, le surplus doit être vérifié manuellement
3. **Transaction Code** : Tous les paiements liés (redistribution + surplus) partagent le même code
4. **Ordre de Traitement** : Redistribution → Application → Surplus (dans cet ordre)

## 🧪 Tests Recommandés

- [ ] Surplus vers plan suivant sans paiements non vérifiés
- [ ] Surplus vers plan suivant avec paiements non vérifiés
- [ ] Surplus sur le dernier plan (pas de plan suivant)
- [ ] Redistribution + surplus avec statut conditionnel
- [ ] Vérification manuelle d'un surplus unverified
- [ ] Vérifier que le transaction_code est copié correctement
- [ ] Vérifier les logs pour chaque scénario

## 📝 Logs Attendus

```
INFO: Détection surplus de 30000 pour l'étudiant MAT123
INFO: Plan suivant trouvé: [uuid] - Troisième tranche
INFO: Le plan suivant a des paiements non vérifiés. Le surplus sera créé avec status='unverified'.
INFO: Création d'un nouveau paiement de surplus de 30000 avec status='unverified'
INFO: Paiement de surplus créé: [uuid] (status=unverified)
INFO: PaymentInstallement mis à jour: paid_amount=0
```

ou

```
INFO: Détection surplus de 30000 pour l'étudiant MAT123
WARNING: Aucun plan suivant trouvé. Le surplus de 30000 reste sur le plan actuel (dernier plan).
```
