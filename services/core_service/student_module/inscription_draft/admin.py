from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from .models import InscriptionDraft


class InscriptionDraftResource(resources.ModelResource):
    user_name = fields.Field(
        column_name="user_name",
        attribute="user",
        widget=ForeignKeyWidget(
            InscriptionDraft._meta.get_field("user").related_model, "username"
        ),
    )

    class Meta:
        model = InscriptionDraft
        fields = (
            "id",
            "user",
            "user_name",
            "session_id",
            "current_step",
            "form_data",
            "title",
            "status",
            "is_completed",
            "created_at",
            "updated_at",
        )
        export_order = (
            "id",
            "user_name",
            "session_id",
            "current_step",
            "title",
            "status",
            "is_completed",
            "created_at",
            "updated_at",
        )


@admin.register(InscriptionDraft)
class InscriptionDraftAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = InscriptionDraftResource
    list_display = (
        "user",
        "session_id",
        "current_step",
        "title",
        "status",
        "is_completed",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "session_id",
        "title",
    )
    list_filter = (
        "is_completed",
        "current_step",
        "status",
    )
    ordering = ("-updated_at",)
    fieldsets = (
        (
            "Draft Information",
            {
                "fields": (
                    "user",
                    "session_id",
                    "current_step",
                    "form_data",
                    "title",
                    "status",
                    "is_completed",
                )
            },
        ),
    )
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
