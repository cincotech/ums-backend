from django.urls import path

from . import views

urlpatterns = [
    path(
        "recteur/overview/", views.recteur_dashboard_overview, name="recteur-overview"
    ),
    path("recteur/derogations/", views.payment_derogations, name="payment-derogations"),
    path(
        "recteur/derogations/<uuid:derogation_id>/process/",
        views.process_payment_derogation,
        name="process-derogation",
    ),
    path(
        "recteur/attributions/",
        views.visiting_professor_attributions,
        name="recteur-attributions",
    ),
    path(
        "recteur/attributions/<uuid:attribution_id>/validate/",
        views.validate_course_attribution,
        name="recteur-validate-attribution",
    ),
    path(
        "recteur/payments/overview/",
        views.payment_tracking_overview,
        name="payment-overview",
    ),
    path(
        "recteur/performance/",
        views.academic_performance_supervision,
        name="academic-performance",
    ),
    path(
        "recteur/quality-reports/",
        views.quality_reports_consultation,
        name="quality-reports",
    ),
]
