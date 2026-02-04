# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.faculty_app.models import Faculty

from .models import Program, ProgramImage


# ----------------------------
# Program Resource
# ----------------------------
class ProgramResource(resources.ModelResource):
    faculty_name = fields.Field(
        column_name="faculty_name",
        attribute="faculty",
        widget=ForeignKeyWidget(Faculty, "faculty_name"),
    )

    class Meta:
        model = Program
        fields = (
            "id",
            "presentation",
            "faculty",
            "faculty_name",
            "duration",
            "is_active",
        )
        export_order = (
            "id",
            "presentation",
            "faculty_name",
            "duration",
            "is_active",
        )


class ProgramImageInline(admin.TabularInline):
    model = ProgramImage
    extra = 1


# ----------------------------
# Program Admin
# ----------------------------
@admin.register(Program)
class ProgramAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProgramResource
    inlines = [ProgramImageInline]
    list_display = ("faculty", "duration", "is_active")
    list_filter = ("faculty", "is_active")
    search_fields = ("presentation", "faculty__faculty_name")
    ordering = ("faculty",)

    fieldsets = (
        (
            "Program Information",
            {
                "fields": (
                    "presentation",
                    "faculty",
                    "duration",
                    "is_active",
                )
            },
        ),
        (
            "Program Details",
            {
                "fields": (
                    "content",
                    "admission_conditions",
                    "prerequisites",
                    "career_opportunities",
                    "internship",
                )
            },
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
