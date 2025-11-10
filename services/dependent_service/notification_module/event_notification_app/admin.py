# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

from .models import Notification


# ----------------------------
# Notification Resource
# ----------------------------
class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        fields = ("id", "email", "telephone", "message", "sent_at", "delivery_status")
        export_order = (
            "id",
            "email",
            "telephone",
            "message",
            "sent_at",
            "delivery_status",
        )


# ----------------------------
# Notification Admin
# ----------------------------
@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = NotificationResource
    list_display = ("email", "telephone", "delivery_status", "sent_at")
    list_filter = ("delivery_status",)
    search_fields = ("email", "telephone", "message")
    ordering = ("-sent_at",)

    fieldsets = (
        (
            "Notification Information",
            {"fields": ("email", "telephone", "message", "sent_at", "delivery_status")},
        ),
    )

    # Optional: Customize Unfold form fields
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
        models.TextField: {
            "widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 3})
        },
    }
