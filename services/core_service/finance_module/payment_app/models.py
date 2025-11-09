import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from services.core_service.finance_module.fees_app.models import FeesSheet
from services.core_service.student_module.inscription_app.models import Inscription
from services.foundational_service.auth_module.user_app.models import User


class Bank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    bank_abreviation = models.CharField(max_length=10)

    class Meta:
        db_table = "banks"


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
    feessheet = models.ForeignKey(
        FeesSheet, on_delete=models.RESTRICT, related_name="payments_frrssheet"
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
    remittance_slip_uri = models.CharField(max_length=255, null=True)
    payment_status = models.CharField(
        max_length=20, choices=STATUS, default="unverified"
    )
    history = HistoricalRecords()

    class Meta:
        db_table = "payments"
