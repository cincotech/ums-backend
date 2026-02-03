from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

# Router pour les ViewSets
router = DefaultRouter()
router.register(
    r"attributions", views.AttributionValidationViewSet, basename="attribution"
)
urlpatterns = [
    path("overview/", views.dashboard_overview, name="dashboard-overview"),
    path(
        "attributions/visiting-professors/",
        views.visiting_professors_attributions,
        name="visiting-professors-attributions",
    ),
    # path(
    # "attributions/<uuid:attribution_id>/validate/",
    # views.validate_attribution,
    #  name="validate-attribution",
    # ),
    path(
        "performance/academic/",
        views.academic_performance_report,
        name="academic-performance-report",
    ),
    path(
        "reports/generate/",
        views.generate_quality_report,
        name="generate-quality-report",
    ),
    path("reports/", views.quality_reports_list, name="quality-reports-list"),
]

# Ajouter les URLs du router
urlpatterns += router.urls
