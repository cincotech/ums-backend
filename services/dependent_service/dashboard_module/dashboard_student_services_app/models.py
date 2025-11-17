import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class DocumentRequest(models.Model):
    DOCUMENT_TYPES = (
        ("diploma", "Diplôme"),
        ("success_certificate", "Attestation de Réussite"),
        ("attendance_certificate", "Attestation de Fréquentation"),
        ("generic_certificate", "Attestation À qui de Droit"),
    )

    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("processing", "En Traitement"),
        ("ready", "Prêt"),
        ("delivered", "Livré"),
        ("rejected", "Rejeté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    processed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "document_requests"


class AbsenceJustification(models.Model):
    ABSENCE_TYPES = (
        ("medical", "Maladie"),
        ("family_emergency", "Urgence Familiale"),
        ("official_duty", "Devoir Officiel"),
        ("other", "Autre"),
    )

    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("approved", "Approuvé"),
        ("rejected", "Rejeté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    absence_type = models.CharField(max_length=50, choices=ABSENCE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    supporting_documents = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "absence_justifications"


class StudentActivity(models.Model):
    ACTIVITY_TYPES = (
        ("club", "Club Étudiant"),
        ("association", "Association"),
        ("event", "Événement"),
        ("conference", "Conférence"),
        ("sports", "Activité Sportive"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="organized_activities"
    )
    participants = models.ManyToManyField(
        Student, related_name="participated_activities", blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_activities"


class Scholarship(models.Model):
    SCHOLARSHIP_TYPES = (
        ("government", "Gouvernementale"),
        ("private", "Privée"),
        ("international", "Internationale"),
        ("merit", "Mérite Académique"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    scholarship_type = models.CharField(max_length=50, choices=SCHOLARSHIP_TYPES)
    provider = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    managed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scholarships"


class CounselingSession(models.Model):
    SESSION_TYPES = (
        ("orientation", "Orientation"),
        ("academic_counseling", "Conseil Académique"),
        ("methodological", "Méthodologique"),
        ("career_guidance", "Orientation Professionnelle"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    counselor = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Student, blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=255)
    is_group_session = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_sessions"


class StudentStatusChange(models.Model):
    """Track special cases: withdrawals, exclusions, suspensions"""

    STATUS_TYPES = (
        ("withdrawal", "Abandon"),
        ("exclusion", "Exclusion"),
        ("suspension", "Suspension"),
        ("cancellation", "Annulation Année Académique"),
        ("transfer", "Transfert"),
    )

    APPROVAL_STATUS = (
        ("pending", "En Attente"),
        ("approved", "Approuvé"),
        ("rejected", "Rejeté"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    inscription = models.ForeignKey(
        "inscription_app.Inscription",
        on_delete=models.CASCADE,
        related_name="status_changes",
    )
    status_type = models.CharField(max_length=50, choices=STATUS_TYPES)
    reason = models.TextField()
    supporting_documents = models.JSONField(default=list, blank=True)
    requested_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="requested_status_changes"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_status_changes",
    )
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS, default="pending"
    )
    effective_date = models.DateField()
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "student_status_changes"
        ordering = ["-requested_at"]
