# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.department_app.models import Department

from .models import Class


# ----------------------------
# Class Resource
# ----------------------------
class ClassResource(resources.ModelResource):
    department_name = fields.Field(
        column_name="department_name",
        attribute="department",
        widget=ForeignKeyWidget(Department, "department_name"),
    )

    class Meta:
        model = Class
        fields = ("id", "class_name", "department", "department_name")
        export_order = ("id", "class_name", "department_name")


# ----------------------------
# Class Admin
# ----------------------------
@admin.register(Class)
class ClassAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ClassResource
    list_display = ("class_name", "department")
    list_filter = ("department",)
    search_fields = ("class_name", "department__department_name")
    ordering = ("class_name",)

    fieldsets = (("Class Information", {"fields": ("class_name", "department")}),)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
        models.JSONField: {
            "widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 3, "cols": 40})
        },
    }
