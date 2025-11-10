from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear

from .models import FeesSheet, Wording


# ----------------------------
# Wording Resource
# ----------------------------
class WordingResource(resources.ModelResource):
    class Meta:
        model = Wording
        fields = ("id", "wording_name")
        export_order = ("id", "wording_name")


# ----------------------------
# Wording Admin
# ----------------------------
@admin.register(Wording)
class WordingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = WordingResource
    list_display = ("wording_name",)
    search_fields = ("wording_name",)
    ordering = ("wording_name",)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# FeesSheet Resource
# ----------------------------
class FeesSheetResource(resources.ModelResource):
    class_name = fields.Field(
        column_name="class_name",
        attribute="class_fk",
        widget=ForeignKeyWidget(Class, "class_name"),
    )
    academic_year_name = fields.Field(
        column_name="academic_year",
        attribute="academic_year",
        widget=ForeignKeyWidget(AcademicYear, "academic_year"),
    )
    wording_name = fields.Field(
        column_name="wording_name",
        attribute="wording",
        widget=ForeignKeyWidget(Wording, "wording_name"),
    )

    class Meta:
        model = FeesSheet
        fields = (
            "id",
            "class_fk",
            "class_name",
            "academic_year",
            "academic_year_name",
            "wording",
            "wording_name",
            "base_amount",
            "installements",
        )
        export_order = (
            "id",
            "class_name",
            "academic_year_name",
            "wording_name",
            "base_amount",
            "installements",
        )


# ----------------------------
# FeesSheet Admin
# ----------------------------
@admin.register(FeesSheet)
class FeesSheetAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = FeesSheetResource
    list_display = (
        "class_fk",
        "academic_year",
        "wording",
        "base_amount",
        "display_installements",
    )
    list_filter = ("class_fk", "academic_year", "wording")
    search_fields = (
        "class_fk__class_name",
        "academic_year__academic_year",
        "wording__wording_name",
    )
    ordering = ("class_fk",)

    fieldsets = (
        (
            "FeesSheet Information",
            {
                "fields": (
                    "class_fk",
                    "academic_year",
                    "wording",
                    "base_amount",
                    "installements",
                )
            },
        ),
    )

    formfield_overrides = {
        models.PositiveIntegerField: {
            "widget": admin.widgets.AdminIntegerFieldWidget(
                attrs={"class": "vIntegerField"}
            )
        },
        models.JSONField: {
            "widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 3, "cols": 40})
        },
    }

    # Optional: Display installements as a readable string
    def display_installements(self, obj):
        if obj.installements:
            return ", ".join(str(i) for i in obj.installements)
        return "-"

    display_installements.short_description = "Installements"
