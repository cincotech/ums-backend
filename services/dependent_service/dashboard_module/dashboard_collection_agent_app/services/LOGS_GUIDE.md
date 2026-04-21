# 📋 Guide des Logs - PaymentService

## 🎯 Objectif
Ce fichier explique comment lire et interpréter les logs du système de paiement.

## 📊 Niveaux de logs

### ✅ INFO (logger.info)
- Opérations normales
- Étapes de traitement
- Succès des opérations

### ❌ ERROR (logger.error)
- Erreurs et exceptions
- Échecs de validation
- Problèmes de traitement

## 🔍 Symboles utilisés

| Symbole | Signification |
|---------|---------------|
| 🔵 | Début d'opération principale |
| ✅ | Succès |
| ❌ | Erreur |
| 📋 | Création/Préparation |
| 💰 | Distribution d'argent |
| 🎯 | Application au plan cible |
| 💸 | Gestion de surplus |
| 🔍 | Recherche |
| 🗑️ | Suppression |
| 🔄 | Changement de statut |
| 📊 | Recalcul |
| ⏭️ | Passage à l'élément suivant |
| 🚫 | Arrêt/Fin |

## 📝 Exemples de logs

### 1. CREATE_PAYMENT

```
================================================================================
🔵 CREATE_PAYMENT - Début
Étudiant: John Doe (MAT001)
Plan cible: Trimestre 2
Montant: 300
Méthode: bank_deposit
================================================================================

📋 Étape 0: Création des installments précédents

💰 Étape 1: Distribution aux plans précédents
  🔍 Recherche des plans précédents impayés...
  📊 1 plan(s) précédent(s) trouvé(s)
  💵 Trimestre 1 - Paiement de 100
  ✅ Payment créé: abc-123-def
Montant restant après distribution: 200

🎯 Étape 2: Application au plan cible
  💵 Paiement principal créé: xyz-456-uvw

  💸 HANDLE_SURPLUS - Début
  Surplus: 50
  Plan actuel: Trimestre 2

  🔄 Itération 1 - Surplus restant: 50
  🎯 Plan suivant trouvé: Trimestre 3
  💵 Transfert de 50 vers Trimestre 3
  ✅ Payment surplus créé: mno-789-pqr

  ✅ HANDLE_SURPLUS - Terminé

✅ CREATE_PAYMENT - Succès
================================================================================
```

### 2. VERIFY_PAYMENT

```
================================================================================
✅ VERIFY_PAYMENT - Début
Payment ID: abc-123-def
Montant: 200
Vérifié par: Finance User
================================================================================

✅ Paiement vérifié

💸 Surplus détecté: 50

  💸 HANDLE_SURPLUS - Début
  ...
  ✅ HANDLE_SURPLUS - Terminé

✅ VERIFY_PAYMENT - Succès
================================================================================
```

### 3. UNVERIFY_PAYMENT

```
================================================================================
❌ UNVERIFY_PAYMENT - Début
Payment ID: abc-123-def
Rejeté par: Finance User
================================================================================

🔍 Recherche des paiements automatiques...
🗑️ Suppression de 3 paiements automatiques
🔄 Changement du statut en 'unverified'
📊 Recalcul des installments...
  - Trimestre 1: 0
  - Trimestre 2: 0
  - Trimestre 3: 0

✅ UNVERIFY_PAYMENT - Succès
================================================================================
```

### 4. Erreur

```
================================================================================
🔵 CREATE_PAYMENT - Début
Étudiant: John Doe (MAT001)
Plan cible: Trimestre 2
Montant: 300
Méthode: bank_deposit
================================================================================

❌ CREATE_PAYMENT - Erreur: Insufficient funds
================================================================================
```

## 🛠️ Configuration des logs

Pour voir les logs dans la console Django, assurez-vous que votre `settings.py` contient :

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'services.dependent_service.dashboard_module.dashboard_collection_agent_app.services.paymentService': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## 🔧 Changer le niveau de log

- **DEBUG** : Tous les détails (très verbeux)
- **INFO** : Opérations normales (recommandé)
- **WARNING** : Avertissements uniquement
- **ERROR** : Erreurs uniquement

## 📌 Notes importantes

1. Les logs sont **atomiques** : si une transaction échoue, tout est annulé
2. Chaque paiement créé a un **ID unique** affiché dans les logs
3. Les **montants** sont toujours affichés pour faciliter le débogage
4. Les **descriptions** des paiements automatiques sont tracées

## 🐛 Débogage

Si vous rencontrez un problème :

1. Cherchez le symbole ❌ dans les logs
2. Regardez le message d'erreur
3. Remontez dans les logs pour voir les étapes précédentes
4. Vérifiez les montants et les IDs des paiements

## 📞 Support

Pour toute question sur les logs, contactez l'équipe de développement.
