# TODO - Implémentation Validation Attribution & Suggestions

## Étape 1: Modifier teacher_app/models.py
- [ ] Ajouter champs de validation au modèle Attribution
  - validation_status (pending/approved/rejected)
  - validated_by (FK to User)
  - validation_date (DateTimeField)
  - validation_comments (TextField)

## Étape 2: Supprimer dashboard_academic_app/models.py
- [ ] Supprimer le fichier models.py (pas nécessaire)

## Étape 3: Réécrire dashboard_academic_app/serializers.py
- [ ] AttributionSerializer
- [ ] AttributionValidationSerializer
- [ ] AcademicOverviewSerializer
- [ ] SuggestionSerializer

## Étape 4: Implémenter dashboard_academic_app/views.py
- [ ] dashboard_overview() - Stats académiques
- [ ] validate_attribution() - POST valider/rejeter
- [ ] pending_attributions() - GET liste en attente
- [ ] add_suggestion() - POST ajouter suggestion
- [ ] visiting_professors() - GET profs visiteurs

## Étape 5: Mettre à jour dashboard_academic_app/services.py
- [ ] get_attribution_stats()
- [ ] get_suggestion_stats()
- [ ] get_academic_overview()
- [ ] get_visiting_professors()

## Étape 6: Mettre à jour dashboard_academic_app/urls.py
- [ ] Vérifier les endpoints existants

## Étape 7: Migration
- [ ] Créer migration
- [ ] Appliquer migration

## Étape 8: Nettoyage
- [ ] Supprimer dashboard_academic_app/models.py

