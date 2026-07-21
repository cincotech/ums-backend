# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.faculty_app.models import Faculty

from .models import Department


# ----------------------------
# Department Resource
# ----------------------------
class DepartmentResource(resources.ModelResource):

    faculty = fields.Field(
        column_name="faculty",
        attribute="faculty",
        widget=ForeignKeyWidget(Faculty, "id"),
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "department_name",
            "abreviation",
            "faculty",
        )
        export_order = (
            "id",
            "department_name",
            "abreviation",
            "faculty",
        )


# ----------------------------
# Department Admin
# ----------------------------
@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = DepartmentResource
    list_display = ("department_name", "abreviation", "faculty", "is_default")
    list_filter = ("faculty",)
    search_fields = (
        "department_name",
        "abreviation",
        "faculty__faculty_name",
        "is_default",
    )
    ordering = ("department_name",)

    fieldsets = (
        (
            "Department Information",
            {"fields": ("department_name", "abreviation", "faculty", "is_default")},
        ),
    )

    # Optional: Customize Unfold form fields
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
