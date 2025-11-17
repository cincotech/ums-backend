import uuid

from django.db import models

from services.foundational_service.auth_module.user_app.models import User


class Notification(models.Model):
    """Unified notification system for all dashboard users"""

    NOTIFICATION_TYPES = (
        ("payment", "Paiement"),
        ("schedule_change", "Changement Emploi du Temps"),
        ("registration", "Inscription"),
        ("exam_result", "Résultat Examen"),
        ("document_ready", "Document Prêt"),
        ("general", "Général"),
        ("system", "Système"),
        ("academic", "Académique"),
    )

    USER_TYPES = (
        ("student", "Étudiant"),
        ("teacher", "Enseignant"),
        ("admin", "Administrateur"),
        ("alumni", "Alumni"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    recipient_type = models.CharField(max_length=20, choices=USER_TYPES)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"


class Message(models.Model):
    """Unified messaging system for all dashboard users"""

    MESSAGE_TYPES = (
        ("internal", "Interne"),
        ("official", "Officiel"),
        ("support", "Support"),
        ("announcement", "Annonce"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages_unified"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages_unified"
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"


class AuditLog(models.Model):
    """Unified audit logging system"""

    ACTION_TYPES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("password_reset", "Password Reset"),
        ("role_change", "Role Change"),
        ("payment", "Payment"),
        ("document_request", "Document Request"),
        ("grade_entry", "Grade Entry"),
        ("exam_schedule", "Exam Schedule"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=255, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"


class SystemConfiguration(models.Model):
    """Unified system configuration management"""

    CONFIG_TYPES = (
        ("academic_year", "Academic Year"),
        ("fee_type", "Fee Type"),
        ("security", "Security"),
        ("feature", "Feature"),
        ("global", "Global"),
        ("notification", "Notification"),
        ("payment", "Payment"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPES)
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_configurations"
        unique_together = ["config_type", "key"]


class BackupRecord(models.Model):
    """System backup management"""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_type = models.CharField(max_length=50, default="full")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    initiated_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "backup_records"
