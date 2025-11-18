from django.contrib import admin

from .models import AuditLog, BackupRecord, Message, Notification, SystemConfiguration


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "recipient",
        "recipient_type",
        "notification_type",
        "is_read",
        "created_at",
    ]
    list_filter = ["recipient_type", "notification_type", "is_read", "created_at"]
    search_fields = ["title", "message", "recipient__email"]
    readonly_fields = ["created_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "sender",
        "recipient",
        "message_type",
        "is_read",
        "sent_at",
    ]
    list_filter = ["message_type", "is_read", "sent_at"]
    search_fields = ["subject", "content", "sender__email", "recipient__email"]
    readonly_fields = ["sent_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "model_name", "timestamp"]
    list_filter = ["action", "model_name", "timestamp"]
    search_fields = ["user__email", "model_name", "object_id"]
    readonly_fields = ["timestamp"]


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ["config_type", "key", "is_active", "created_by", "updated_at"]
    list_filter = ["config_type", "is_active", "created_at"]
    search_fields = ["key", "config_type"]
    readonly_fields = ["created_at", "updated_at"]


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
    search_fields = ["backup_type", "initiated_by__email"]
    readonly_fields = ["started_at", "completed_at"]
