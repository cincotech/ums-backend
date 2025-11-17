import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class PaymentDerogation(models.Model):
    DEROGATION_TYPES = (
        ("exemption", "Exemption"),
        ("postponement", "Report"),
        ("arrangement", "Aménagement"),
    )

    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("approved", "Approuvé"),
        ("rejected", "Rejeté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    derogation_type = models.CharField(max_length=20, choices=DEROGATION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    supporting_documents = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    requested_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="requested_derogations"
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="reviewed_derogations",
    )
    decision_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payment_derogations"


class RecteurDecision(models.Model):
    DECISION_TYPES = (
        ("payment_derogation", "Dérogation de Paiement"),
        ("course_attribution", "Attribution de Cours"),
        ("exceptional_authorization", "Autorisation Exceptionnelle"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision_type = models.CharField(max_length=50, choices=DECISION_TYPES)
    reference_id = models.CharField(max_length=255)  # ID of related object
    decision = models.CharField(max_length=20)  # approved/rejected
    notes = models.TextField(null=True, blank=True)
    decided_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recteur_decisions"
