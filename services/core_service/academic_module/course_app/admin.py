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
        fields = (
            "id",
            "course_code",
            "course_name",
            "cm",
            "td",
            "tp",
            "credits",
            "module",
        )
        export_order = (
            "id",
            "course_code",
            "course_name",
            "cm",
            "td",
            "tp",
            "credits",
            "module",
        )


# ----------------------------
# Course Admin
# ----------------------------
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CourseResource
    list_display = (
        "course_code",
        "course_name",
        "module",
        "cm",
        "td",
        "tp",
        "total_hours",
        "credits",
    )
    list_filter = ("module",)
    search_fields = ("course_name", "course_code", "module__module_name")
    ordering = ("course_name",)
    formats = [base_formats.CSV, base_formats.JSON, base_formats.XLSX]

    readonly_fields = ("id", "total_hours")

    fieldsets = (
        (
            "ECUE Information",
            {"fields": ("course_name", "course_code", "module", "credits")},
        ),
        (
            "Teaching Hours",
            {"fields": ("cm", "td", "tp", "total_hours")},
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
        models.PositiveSmallIntegerField: {
            "widget": admin.widgets.AdminIntegerFieldWidget(
                attrs={"class": "vIntegerField", "size": 4}
            )
        },
    }

    def total_hours(self, obj):
        return obj.cm + obj.td + obj.tp

    total_hours.short_description = "Total Hours"
