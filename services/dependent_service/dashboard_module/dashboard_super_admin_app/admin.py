from django.contrib import admin

from .models import AuditLog, BackupRecord, EmergencyRecovery, SystemConfiguration


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ["category", "key", "is_active", "created_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["key", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Configuration", {"fields": ("category", "key", "value", "description")}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Audit",
            {"fields": ("created_by", "modified_by", "created_at", "updated_at")},
        ),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "severity", "success", "timestamp"]
    list_filter = ["action", "severity", "success", "timestamp"]
    search_fields = ["user__email", "description", "entity_type"]
    readonly_fields = ["timestamp", "id"]
    fieldsets = (
        ("User & Action", {"fields": ("user", "action", "severity")}),
        ("Entity", {"fields": ("entity_type", "entity_id")}),
        ("Details", {"fields": ("description", "changes", "success", "error_message")}),
        ("Request", {"fields": ("ip_address", "user_agent", "location")}),
        ("University", {"fields": ("university",)}),
        ("Timestamp", {"fields": ("timestamp",)}),
    )


@admin.register(BackupRecord)
class BackupRecordAdmin(admin.ModelAdmin):
    list_display = [
        "backup_type",
        "status",
        "initiated_by",
        "started_at",
        "completed_at",
    ]
    list_filter = ["backup_type", "status", "started_at"]
    search_fields = ["file_path"]
    readonly_fields = ["started_at", "id"]
    fieldsets = (
        ("Backup Info", {"fields": ("backup_type", "status")}),
        ("File", {"fields": ("file_path", "file_size", "backup_location")}),
        ("Timeline", {"fields": ("started_at", "completed_at")}),
        ("Metadata", {"fields": ("metadata", "error_message")}),
        ("User", {"fields": ("initiated_by",)}),
    )


@admin.register(EmergencyRecovery)
class EmergencyRecoveryAdmin(admin.ModelAdmin):
    list_display = ["recovery_type", "target_user", "status", "initiated_at"]
    list_filter = ["recovery_type", "status", "initiated_at"]
    search_fields = ["target_user__email", "reason"]
    readonly_fields = ["initiated_at", "id"]
    fieldsets = (
        ("Recovery Info", {"fields": ("recovery_type", "status")}),
        ("Users", {"fields": ("target_user", "performed_by")}),
        ("Details", {"fields": ("reason", "details", "result")}),
        ("Timeline", {"fields": ("initiated_at", "completed_at")}),
    )
