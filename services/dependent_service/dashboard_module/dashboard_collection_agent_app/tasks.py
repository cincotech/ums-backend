from celery import shared_task
from django.utils import timezone

from .models import PaymentInstallement, PaymentReminder
from .services import NotificationService


@shared_task
def send_payment_reminders():
    """Tâche automatique pour envoyer les rappels de paiement"""
    today = timezone.now().date()

    # Récupérer tous les échéanciers en retard
    overdue_installments = PaymentInstallement.objects.filter(
        status__in=["pending", "overdue"], due_date__lt=today
    ).select_related("student", "payment_plan")

    for installment in overdue_installments:
        days_overdue = (today - installment.due_date).days
        student = installment.student

        # Déterminer le type de rappel selon les jours de retard
        reminder_type = _get_reminder_type(days_overdue)
        if not reminder_type:
            continue

        # Vérifier si ce type de rappel n'a pas déjà été envoyé
        existing_reminder = PaymentReminder.objects.filter(
            student=student, reminder_type=reminder_type, sent_at__date=today
        ).exists()

        if not existing_reminder:
            _create_and_send_reminder(installment, reminder_type, days_overdue)


def _get_reminder_type(days_overdue):
    """Détermine le type de rappel selon les jours de retard"""
    if 7 <= days_overdue < 30:
        return "reminder_7"
    elif 30 <= days_overdue < 60:
        return "reminder_30"
    elif 60 <= days_overdue < 90:
        return "formal_notice_60"
    elif days_overdue >= 90:
        return "final_notice"
    return None


def _create_and_send_reminder(installment, reminder_type, days_overdue):
    """Crée et envoie un rappel de paiement"""
    student = installment.student
    amount_due = installment.amount - installment.paid_amount

    # Messages selon le type de rappel
    messages = {
        "reminder_7": f"Rappel: Votre paiement de {amount_due}€ est en retard de {days_overdue} jours.",
        "reminder_30": f"Relance: Votre paiement de {amount_due}€ est en retard de {days_overdue} jours. Veuillez régulariser rapidement.",
        "formal_notice_60": f"MISE EN DEMEURE: Vous devez {amount_due}€ depuis {days_overdue} jours. Régularisation obligatoire sous 15 jours.",
        "final_notice": f"DERNIER AVIS: Dette de {amount_due}€ en souffrance depuis {days_overdue} jours. Action disciplinaire imminente.",
    }

    # Créer le rappel
    reminder = PaymentReminder.objects.create(
        student=student,
        reminder_type=reminder_type,
        amount_due=amount_due,
        message=messages[reminder_type],
        sent_by_id=1,  # Système automatique
        status="pending",
    )

    # Envoyer la notification
    try:
        NotificationService.send_payment_reminder(reminder)
        reminder.status = "sent"
    except Exception:
        reminder.status = "failed"

    reminder.save()


@shared_task
def update_overdue_installments():
    """Met à jour le statut des échéanciers en retard"""
    today = timezone.now().date()

    PaymentInstallement.objects.filter(due_date__lt=today, status="pending").update(
        status="overdue"
    )
