import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def send_payment_reminder(reminder):
        """Envoie un rappel de paiement par email uniquement"""
        try:
            NotificationService._send_email_reminder(reminder)
            # Créer correspondance de suivi
            NotificationService._create_correspondence_record(reminder)
        except Exception as e:
            logger.error(f"Erreur email pour {reminder.student.matricule}: {e}")
            raise

    @staticmethod
    def _send_email_reminder(reminder):
        """Envoie le rappel par email"""
        student = reminder.student

        subject_map = {
            "reminder_7": "Rappel de paiement - UMS",
            "reminder_30": "Relance de paiement - UMS",
            "formal_notice_60": "MISE EN DEMEURE - UMS",
            "final_notice": "DERNIER AVIS - UMS",
        }

        send_mail(
            subject=subject_map.get(reminder.reminder_type, "Rappel de paiement"),
            message=reminder.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.user.email],
            fail_silently=False,
        )

    @staticmethod
    def _create_correspondence_record(reminder):
        """Crée un enregistrement de correspondance"""
        from .models import CollectionCorrespondence

        CollectionCorrespondence.objects.create(
            student=reminder.student,
            correspondence_type="email",
            subject=f"Rappel automatique - {reminder.get_reminder_type_display()}",
            content=reminder.message,
            sent_by=reminder.sent_by,
        )
