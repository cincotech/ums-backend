from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


@shared_task
def notify_derogation_decision(student_email, status):
    # Notifier l'étudiant
    send_mail(
        subject="Décision Rectorale sur votre Dérogation",
        message=f"Votre demande a été : {status.upper()}",
        from_email="no-reply@ums.bi",
        recipient_list=[student_email],
    )

    # Notifier l'Agent de Recouvrement et le Comptable
    recovery_agents = User.objects.filter(role="agent_recouvrement")
    accountants = User.objects.filter(role="comptable")

    recipient_list = list(recovery_agents.values_list("email", flat=True)) + list(
        accountants.values_list("email", flat=True)
    )

    if recipient_list:
        send_mail(
            subject="Notification: Décision de Dérogation de Paiement",
            message=f"Une dérogation de paiement a été {status.upper()}. Veuillez mettre à jour le statut de l'étudiant {student_email}.",
            from_email="no-reply@ums.bi",
            recipient_list=recipient_list,
        )
