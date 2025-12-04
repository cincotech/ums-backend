from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


@shared_task
def notify_attribution_validation(attribution_id, validation_status):
    """Notifier les parties prenantes de la validation d'attribution."""
    from .models import AttributionValidation

    try:
        validation = AttributionValidation.objects.get(id=attribution_id)
        teacher = validation.attribution.user

        # Notifier l'enseignant
        send_mail(
            subject="Attribution de Cours - Décision",
            message=f"Votre attribution de cours a été {validation_status.upper()}.",
            from_email="no-reply@ums.bi",
            recipient_list=[teacher.email],
        )

        # Notifier les doyens
        deans = User.objects.filter(role="doyen")
        dean_emails = list(deans.values_list("email", flat=True))

        if dean_emails:
            send_mail(
                subject="Attribution de Cours Validée",
                message=f"L'attribution de cours pour {teacher.get_full_name()} a été {validation_status.upper()}.",
                from_email="no-reply@ums.bi",
                recipient_list=dean_emails,
            )
    except AttributionValidation.DoesNotExist:
        pass


@shared_task
def generate_quality_report(report_type, title, data):
    """Générer un rapport de qualité."""
    from .models import QualityReport

    QualityReport.objects.create(
        report_type=report_type,
        title=title,
        data=data,
        generated_by_id=None,
    )
