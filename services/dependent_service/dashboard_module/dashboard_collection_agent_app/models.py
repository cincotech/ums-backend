import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class PaymentInstallment(models.Model):
    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("paid", "Payé"),
        ("overdue", "En Retard"),
        ("deferred", "Reporté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_installments"


class PaymentReminder(models.Model):
    REMINDER_TYPES = (
        ("reminder_7", "Rappel J+7"),
        ("reminder_30", "Relance J+30"),
        ("formal_notice_60", "Mise en Demeure J+60"),
        ("final_notice", "Dernier Avis"),
    )

    STATUS_CHOICES = (
        ("sent", "Envoyé"),
        ("delivered", "Livré"),
        ("failed", "Échec"),
        ("pending", "En Attente"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=50, choices=REMINDER_TYPES)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    sent_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_reminders"


class PaymentPlan(models.Model):
    STATUS_CHOICES = (
        ("active", "Actif"),
        ("completed", "Terminé"),
        ("defaulted", "En Défaut"),
        ("cancelled", "Annulé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_plans"


class PaymentPromise(models.Model):
    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("kept", "Respecté"),
        ("broken", "Non Respecté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    promised_amount = models.DecimalField(max_digits=10, decimal_places=2)
    promised_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(null=True, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_promises"


class CollectionCorrespondence(models.Model):
    CORRESPONDENCE_TYPES = (
        ("email", "Email"),
        ("sms", "SMS"),
        ("letter", "Courrier"),
        ("phone", "Téléphone"),
        ("meeting", "Rencontre"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    correspondence_type = models.CharField(max_length=20, choices=CORRESPONDENCE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    response = models.TextField(null=True, blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "collection_correspondence"


class LegalCase(models.Model):
    STATUS_CHOICES = (
        ("prepared", "Préparé"),
        ("submitted", "Soumis"),
        ("in_progress", "En Cours"),
        ("resolved", "Résolu"),
        ("closed", "Fermé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_debt = models.DecimalField(max_digits=10, decimal_places=2)
    case_documents = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="prepared")
    prepared_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    prepared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "legal_cases"
