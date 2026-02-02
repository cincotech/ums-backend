from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    GuestDocument,
    GuestNotification,
    GuestRequest,
    RoleDocumentRequirement,
)


@admin.register(GuestRequest)
class GuestRequestAdmin(ModelAdmin):
    list_display = [
        "user",
        "requested_role",
        "status",
        "profile_submitted",
        "created_at",
    ]
    list_filter = ["status", "profile_submitted", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "profile_submitted_at",
        "reviewed_at",
    ]
    autocomplete_fields = ["user", "requested_role", "reviewed_by"]


@admin.register(GuestDocument)
class GuestDocumentAdmin(ModelAdmin):
    list_display = ["guest_request", "name", "type", "status", "uploaded_at"]
    list_filter = ["type", "status", "uploaded_at"]
    search_fields = ["name", "guest_request__user__email"]
    readonly_fields = ["uploaded_at", "verified_at", "file_size", "mime_type"]
    autocomplete_fields = ["guest_request", "verified_by"]


@admin.register(GuestNotification)
class GuestNotificationAdmin(ModelAdmin):
    list_display = ["guest_request", "title", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["title", "message", "guest_request__user__email"]
    readonly_fields = ["created_at"]
    autocomplete_fields = ["guest_request", "document"]


@admin.register(RoleDocumentRequirement)
class RoleDocumentRequirementAdmin(ModelAdmin):
    list_display = ["role", "label", "document_type", "required", "max_size_mb"]
    list_filter = ["role", "document_type", "required"]
    search_fields = ["label", "description", "role__name"]
    autocomplete_fields = ["role"]
