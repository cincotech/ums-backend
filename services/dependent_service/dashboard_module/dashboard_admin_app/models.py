import uuid

from django.db import models
from django.utils import timezone

from services.core_service.academic_module.university_app.models import University
from services.foundational_service.auth_module.user_app.models import User


class UniversityConfiguration(models.Model):
    """University-specific configurations managed by University Admin"""

    CONFIG_CATEGORIES = (
        ("academic", "Academic Settings"),
        ("financial", "Financial Settings"),
        ("enrollment", "Enrollment Settings"),
        ("notification", "Notification Settings"),
        ("security", "Security Settings"),
        ("feature", "Feature Flags"),
        ("general", "General Settings"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="configurations"
    )
    category = models.CharField(max_length=50, choices=CONFIG_CATEGORIES)
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_configurations"
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="modified_configurations",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "university_configurations"
        unique_together = [["university", "category", "key"]]
        indexes = [
            models.Index(fields=["university", "category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.university.university_name} - {self.category}: {self.key}"


class UniversityStatistics(models.Model):
    """Aggregated statistics for university dashboard"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="statistics"
    )
    total_students = models.IntegerField(default=0)
    total_teachers = models.IntegerField(default=0)
    total_faculties = models.IntegerField(default=0)
    total_departments = models.IntegerField(default=0)
    total_courses = models.IntegerField(default=0)
    active_enrollments = models.IntegerField(default=0)
    pending_payments = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    completed_exams = models.IntegerField(default=0)
    pending_document_requests = models.IntegerField(default=0)
    statistics_data = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "university_statistics"
        verbose_name_plural = "University statistics"

    def __str__(self):
        return f"Statistics for {self.university.university_name}"


class UniversityNotification(models.Model):
    """Notifications for university admins"""

    NOTIFICATION_TYPES = (
        ("system", "System Notification"),
        ("alert", "Alert"),
        ("warning", "Warning"),
        ("info", "Information"),
        ("success", "Success"),
    )

    PRIORITY_LEVELS = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="admin_notifications",
        null=True,
        blank=True,
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_notifications"
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default="low")
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "university_notifications"
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["priority"]),
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
