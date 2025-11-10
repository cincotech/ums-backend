# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.class_app.models import Class

from .models import Module


# ----------------------------
# Module Resource
# ----------------------------
class ModuleResource(resources.ModelResource):
    class_name = fields.Field(
        column_name="class_name",
        attribute="class_fk",
        widget=ForeignKeyWidget(Class, "class_name"),
    )

    class Meta:
        model = Module
        fields = ("id", "module_name", "code", "semester_id", "class_fk", "class_name")
        export_order = ("id", "module_name", "code", "semester_id", "class_name")


# ----------------------------
# Module Admin
# ----------------------------
@admin.register(Module)
class ModuleAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ModuleResource
    list_display = ("module_name", "code", "semester_id", "class_fk")
    list_filter = ("semester_id", "class_fk")
    search_fields = ("module_name", "code", "class_fk__class_name")
    ordering = ("module_name",)

    fieldsets = (
        (
            "Module Information",
            {"fields": ("module_name", "code", "semester_id", "class_fk")},
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
