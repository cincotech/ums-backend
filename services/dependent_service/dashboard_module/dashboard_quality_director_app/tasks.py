from celery import shared_task
from django.utils import timezone

from .models import QualityReport


@shared_task
def auto_generate_quality_report():
    """Génère automatiquement un rapport de qualité quotidien"""
    from services.foundational_service.auth_module.user_app.models import User

    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            QualityReport.objects.create(
                report_title="Rapport Automatique Quotidien",
                report_period=str(timezone.now().date()),
                summary="Analyse automatique quotidienne des métriques de qualité",
                findings={"auto_generated": True, "timestamp": str(timezone.now())},
                improvement_plans=[],
                generated_by=admin_user,
            )
    except Exception as e:
        print(f"Erreur lors de la génération du rapport: {str(e)}")
