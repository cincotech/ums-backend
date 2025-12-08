# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.module_app.models import Module

from .models import Course


# ----------------------------
# Course Resource
# ----------------------------
class CourseResource(resources.ModelResource):
    module = fields.Field(
        column_name="module",
        attribute="module",
        widget=ForeignKeyWidget(Module, "id"),
    )

    class Meta:
        model = Course
        fields = ("id", "course_name", "cm", "td", "tp", "module", "credits")
        export_order = ("id", "course_name", "cm", "td", "tp", "module", "credits")


# ----------------------------
# Course Admin
# ----------------------------
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CourseResource
    list_display = ("course_name", "module", "cm", "td", "tp", "credits")
    list_filter = ("module",)
    search_fields = ("course_name", "module__module_name")
    ordering = ("course_name",)
    formats = [base_formats.CSV, base_formats.JSON, base_formats.XLSX]

    fieldsets = (
        ("Course Information", {"fields": ("course_name", "module", "cm", "td", "tp")}),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
        models.PositiveSmallIntegerField: {
            "widget": admin.widgets.AdminIntegerFieldWidget(
                attrs={"class": "vIntegerField"}
            )
        },
    }
