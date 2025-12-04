import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear

# from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    bank_abreviation = models.CharField(max_length=10)

    class Meta:
        db_table = "banks"


class Wording(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wording_name = models.CharField(max_length=60)

    class Meta:
        db_table = "wordings"


3


class FeesSheet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="fees_sheets_class"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="fees_sheets_academicyear"
    )
    wording = models.ForeignKey(
        Wording, on_delete=models.RESTRICT, related_name="fees_sheets_wording"
    )
    base_amount = models.PositiveIntegerField()
    installements = models.JSONField(default=list, null=True)  # a supplime

    class Meta:
        db_table = "fees_sheets"


class PaymentInstallement(models.Model):
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
    feessheet = models.ForeignKey(
        FeesSheet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="paymentplan_feessheet",
    )
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


class Payment(models.Model):
    METHOD = (
        ("bank_deposit", "Bank Deposit"),
        ("bank_transfert", "Bank Transfer"),
        ("bank_check", "Bank Check"),
        ("mobile_money", "Mobile Money"),
        ("other", "Other"),
    )
    STATUS = (
        ("verified", "Verified"),
        ("unverified", "Unverified"),
        ("rejected", "Rejected"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paymentplan = models.ForeignKey(
        PaymentPlan, on_delete=models.RESTRICT, related_name="payments_paymentplan"
    )
    amount_paid = models.PositiveIntegerField()
    payment_date = models.DateField(null=True, blank=True)
    reception_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=METHOD)
    bank = models.ForeignKey(
        Bank, on_delete=models.RESTRICT, null=True, related_name="bank"
    )
    bank_slip_ref = models.CharField(max_length=128, null=True)
    transaction_code = models.CharField(max_length=50, null=True)
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="payments_inscription",
    )
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="payments_user"
    )
    description = models.CharField(max_length=250, null=True)
    remittance_slip_uri = models.ImageField(
        upload_to="payment_slips/", null=True, blank=True
    )
    payment_status = models.CharField(
        max_length=20, choices=STATUS, default="unverified"
    )
    # history = HistoricalRecords()

    class Meta:
        db_table = "payments"


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
