# TODO - Implémentation de la logique de paiement prioritaire

## Objectif
Quand un paiement arrive (quel que soit le montant et le plan cible), l'argent doit toujours être affecté en priorité aux dettes les plus anciennes.

## Ordre strict:
1. Tous les plans précédents au plan cible (du plus ancien → le plus récent)
2. Le plan cible lui-même
3. Les plans suivants (si tout le passé et le présent sont soldés)

## Tâches:

- [ ] 1. Créer la méthode `_get_all_student_plans()` - Récupère tous les plans de l'étudiant triés par date
- [ ] 2. Créer la méthode `_get_unpaid_plans()` - Retourne les plans impayés dans l'ordre chronologique
- [ ] 3. Créer la méthode `_distribute_payment()` - Logique principale de distribution
- [ ] 4. Modifier la méthode `create_payment()` pour utiliser la nouvelle logique
- [ ] 5. Modifier la méthode `verify_payment()` pour utiliser la nouvelle logique
- [ ] 6. Tester la logique avec différents scénarios

## Fichier à modifier:
- `services/dependent_service/dashboard_module/dashboard_collection_agent_app/services/paymentService.py`
