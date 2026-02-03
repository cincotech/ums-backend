import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import ClassGroup
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class JurySession(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Planifié"),
        ("in_progress", "En Cours"),
        ("completed", "Terminé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=255)
    session_date = models.DateTimeField()
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE, related_name="jury_sessions"
    )
    jury_members = models.ManyToManyField(User, related_name="jury_sessions")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    minutes_document = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jury_sessions"

    def __str__(self):
        return f"{self.session_name} - {self.class_group.class_fk.class_name} ({self.class_group.group_name}) - {self.session_date}"


class JuryDecision(models.Model):
    DECISION_TYPES = (
        ("admitted", "Admis"),
        ("deferred", "Ajourné"),
        ("repeat", "Redoublement"),
        ("excluded", "Exclu"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jury_session = models.ForeignKey(JurySession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    decision = models.CharField(max_length=20, choices=DECISION_TYPES)
    notes = models.TextField(null=True, blank=True)
    validated_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    validated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jury_decisions"


class GradeComplaint(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Soumise"),
        ("assigned", "Attribuée"),
        ("in_review", "En Révision"),
        ("resolved", "Résolue"),
        ("rejected", "Rejetée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    original_grade = models.FloatField()
    complaint_reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    new_grade = models.FloatField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "grade_complaints"


class OfficialDocument(models.Model):
    DOCUMENT_TYPES = (
        ("transcript", "Relevé de Notes"),
        ("certificate", "Certificat"),
        ("minutes", "Procès-Verbal"),
        ("circular", "Circulaire"),
        ("service_note", "Note de Service"),
    )

    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("pending_signature", "En Attente de Signature"),
        ("signed", "Signé"),
        ("archived", "Archivé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_documents"
    )
    signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "official_documents"


class TeacherPaymentClaim(models.Model):
    STATUS_CHOICES = (
        ("submitted", "Soumise"),
        ("verified", "Vérifiée"),
        ("approved", "Approuvée"),
        ("signed", "Signée"),
        ("sent_to_finance", "Envoyée aux Finances"),
        ("rejected", "Rejetée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    hours_taught = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_claims",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_claims",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "teacher_payment_claims"
