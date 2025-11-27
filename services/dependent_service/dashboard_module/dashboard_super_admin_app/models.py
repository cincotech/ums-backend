import uuid

from django.db import models
from django.utils import timezone

from services.core_service.academic_module.university_app.models import University
from services.foundational_service.auth_module.user_app.models import User


class SystemConfiguration(models.Model):
    """Global system configurations for Super Admin"""

    CONFIG_CATEGORIES = (
        ("feature", "Fonctionnalité"),
        ("security", "Sécurité"),
        ("notification", "Notification"),
        ("global", "Global"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50, choices=CONFIG_CATEGORIES)
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_system_configs"
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="modified_system_configs",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_configurations"
        unique_together = [["category", "key"]]
        indexes = [
            models.Index(fields=["category", "is_active"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.category}: {self.key}"


class AuditLog(models.Model):
    """Unified audit log for system-wide and university-level activities"""

    SEVERITY_LEVELS = (
        ("info", "Info"),
        ("warning", "Avertissement"),
        ("error", "Erreur"),
        ("critical", "Critique"),
    )

    ACTION_TYPES = (
        ("login", "Connexion"),
        ("logout", "Déconnexion"),
        ("create", "Création"),
        ("update", "Modification"),
        ("delete", "Suppression"),
        ("password_reset", "Réinitialisation Mot de Passe"),
        ("role_change", "Changement de Rôle"),
        ("permission_change", "Changement de Permission"),
        ("config_change", "Changement Configuration"),
        ("backup_initiated", "Sauvegarde Initiée"),
        ("restore_initiated", "Restauration Initiée"),
        ("security_breach", "Violation Sécurité"),
        ("failed_login", "Échec Connexion"),
        ("account_locked", "Compte Verrouillé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="audit_logs"
    )
    university = models.ForeignKey(
        University,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default="info")
    entity_type = models.CharField(max_length=100, null=True, blank=True)
    entity_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["university", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
            models.Index(fields=["severity"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        user_email = self.user.email if self.user else "System"
        return f"{user_email} - {self.action} - {self.timestamp}"


class BackupRecord(models.Model):
    """Database backup and restore management"""

    BACKUP_TYPES = (
        ("full", "Sauvegarde Complète"),
        ("incremental", "Sauvegarde Incrémentale"),
        ("differential", "Sauvegarde Différentielle"),
    )

    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("running", "En Cours"),
        ("completed", "Terminée"),
        ("failed", "Échouée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    backup_type = models.CharField(max_length=50, choices=BACKUP_TYPES, default="full")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    backup_location = models.CharField(max_length=500, null=True, blank=True)
    initiated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="initiated_backups"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "backup_records"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.backup_type} - {self.status} - {self.started_at}"

    def mark_completed(self, file_path, file_size):
        self.status = "completed"
        self.completed_at = timezone.now()
        self.file_path = file_path
        self.file_size = file_size
        self.save()

    def mark_failed(self, error_message):
        self.status = "failed"
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()


class EmergencyRecovery(models.Model):
    """Emergency recovery operations for Super Admin"""

    RECOVERY_TYPES = (
        ("password_reset", "Réinitialisation Mot de Passe"),
        ("account_unlock", "Déverrouillage Compte"),
        ("role_restoration", "Restauration Rôle"),
        ("data_recovery", "Récupération Données"),
        ("system_restore", "Restauration Système"),
    )

    STATUS_CHOICES = (
        ("pending", "En Attente"),
        ("in_progress", "En Cours"),
        ("completed", "Terminé"),
        ("failed", "Échoué"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recovery_type = models.CharField(max_length=50, choices=RECOVERY_TYPES)
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="emergency_recoveries",
        null=True,
        blank=True,
    )
    performed_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="performed_recoveries"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reason = models.TextField()
    details = models.JSONField(default=dict)
    result = models.TextField(blank=True, null=True)
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "emergency_recoveries"
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"{self.recovery_type} - {self.status}"


class UniversityProfile(models.Model):
    """University profile and metadata"""

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
        ("trial", "Trial"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.OneToOneField(
        University, on_delete=models.CASCADE, related_name="profile"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="university_logos/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    max_users = models.IntegerField(default=1000)
    max_storage_gb = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "university_profiles"

    def __str__(self):
        return f"Profile - {self.university.university_name}"


class Module(models.Model):
    """System modules for subscription"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "modules_subscription"

    def __str__(self):
        return self.name


class UniversitySubscription(models.Model):
    """University subscription to modules"""

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired"),
        ("suspended", "Suspended"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="subscriptions"
    )
    module = models.ForeignKey(
        Module, on_delete=models.RESTRICT, related_name="subscriptions"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField()
    end_date = models.DateField()
    is_trial = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_subscriptions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "university_subscriptions"
        unique_together = [["university", "module"]]
        indexes = [
            models.Index(fields=["university", "status"]),
            models.Index(fields=["module", "status"]),
            models.Index(fields=["end_date"]),
        ]

    def __str__(self):
        return f"{self.university.university_name} - {self.module.name}"

    def is_expired(self):
        return timezone.now().date() > self.end_date

    def days_remaining(self):
        if self.is_expired():
            return 0
        return (self.end_date - timezone.now().date()).days
