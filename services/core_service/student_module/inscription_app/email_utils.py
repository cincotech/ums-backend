from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

STATUS_EMAIL_CONFIG = {
    "Pending": {
        "template": "emails/inscription_pending.html",
        "subject": "Inscription en attente - Action requise",
    },
    "Active": {
        "template": "emails/inscription_active.html",
        "subject": "Inscription activée - Bienvenue",
    },
    "Completed": {
        "template": "emails/inscription_completed.html",
        "subject": "Félicitations - Inscription complétée",
    },
    "Suspended": {
        "template": "emails/inscription_suspended.html",
        "subject": "Inscription suspendue - Information importante",
    },
    "Withdrawn": {
        "template": "emails/inscription_withdrawn.html",
        "subject": "Confirmation de retrait d'inscription",
    },
    "Dropped": {
        "template": "emails/inscription_dropped.html",
        "subject": "Inscription abandonnée",
    },
    "Canceled": {
        "template": "emails/inscription_canceled.html",
        "subject": "Inscription annulée",
    },
    "Replaced": {
        "template": "emails/inscription_replaced.html",
        "subject": "Changement de classe - Nouvelle inscription",
    },
    "Complement": {
        "template": "emails/inscription_complement.html",
        "subject": "Complément d'inscription requis",
    },
}


def get_inscription_context(inscription):
    """Prépare le contexte commun pour tous les emails d'inscription"""
    student = inscription.student
    user = student.user

    # Récupérer le nom de l'université
    university_name = (
        user.university.university_name
        if user.university
        else "Université polytheque de gitega"
    )

    context = {
        "student_name": user.get_full_name(),
        "matricule": student.matricule or "En attente",
        "email": user.email,
        "phone": user.phone_number or "Non renseigné",
        "birth_date": (
            user.birth_date.strftime("%d/%m/%Y") if user.birth_date else "Non renseigné"
        ),
        "birth_place": (
            f"{student.colline.colline_name}, {student.colline.zone.commune.commune_name}, {student.colline.zone.commune.province.province_name}"
            if student.colline
            else "Non renseigné"
        ),
        "address": (
            user.residence.first().colline_name
            if user.residence.exists()
            else "Non renseigné"
        ),
        "faculty": (
            inscription.class_fk.department.faculty.faculty_name
            if inscription.class_fk
            else "Non assigné"
        ),
        "department": (
            inscription.class_fk.department.department_name
            if inscription.class_fk
            else "Non assigné"
        ),
        "class_name": (
            inscription.class_fk.class_name if inscription.class_fk else "Non assigné"
        ),
        "class_group": (
            inscription.class_group.group_name
            if inscription.class_group
            else "Non assigné"
        ),
        "academic_year": str(inscription.academic_year),
        "inscription_date": inscription.date_inscription.strftime("%d/%m/%Y"),
        "status": inscription.get_regist_status_display(),
        "withdrawal_date": (
            inscription.withdrawal_date.strftime("%d/%m/%Y")
            if inscription.withdrawal_date
            else None
        ),
        "university_name": university_name,
        "payment_info": False,
        "payment_amount": "0",
        "payment_status": "En attente",
        "payment_reference": None,
        "documents": [],
        "current_year": datetime.now().year,
    }

    if hasattr(student, "files"):
        context["documents"] = [
            {
                "type": doc.get_file_type_display(),
                "status": "Vérifié" if doc.is_verified else "En attente",
                "uploaded_at": doc.uploaded_at.strftime("%d/%m/%Y"),
            }
            for doc in student.files.all()
        ]

    return context


def send_inscription_email(inscription, email_type=None):
    """
    Envoie un email basé sur le statut de l'inscription.

    Args:
        inscription: Instance du modèle Inscription
        email_type: Type d'email à envoyer (si None, utilise le statut actuel)

    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    try:
        status = email_type or inscription.regist_status
        config = STATUS_EMAIL_CONFIG.get(status)

        if not config:
            print(f"Aucune configuration d'email pour le statut: {status}")
            return False

        context = get_inscription_context(inscription)
        html_content = render_to_string(config["template"], context)
        subject = f"{config['subject']} - {inscription.student.matricule or inscription.student.user.get_full_name()}"

        email = EmailMultiAlternatives(
            subject=subject,
            body="Veuillez consulter la version HTML de cet email.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[inscription.student.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False


def send_inscription_confirmation_email(inscription):
    """Alias pour compatibilité - envoie l'email basé sur le statut"""
    return send_inscription_email(inscription)


def send_bulk_inscription_emails(inscriptions, email_type=None):
    """Envoie des emails pour plusieurs inscriptions"""
    stats = {"success": 0, "failed": 0, "total": len(inscriptions)}
    for inscription in inscriptions:
        if send_inscription_email(inscription, email_type):
            stats["success"] += 1
        else:
            stats["failed"] += 1
    return stats
