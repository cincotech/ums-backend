# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.module_app.models import Module

from .models import Course


# ----------------------------
# Course Resource
# ----------------------------
class CourseResource(resources.ModelResource):
    module_name = fields.Field(
        column_name="module_name",
        attribute="module",
        widget=ForeignKeyWidget(Module, "module_name"),
    )

    class Meta:
        model = Course
        fields = ("id", "course_name", "cm", "td", "tp", "module", "module_name")
        export_order = ("id", "course_name", "cm", "td", "tp", "module_name")


# ----------------------------
# Course Admin
# ----------------------------
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CourseResource
    list_display = ("course_name", "module", "cm", "td", "tp")
    list_filter = ("module",)
    search_fields = ("course_name", "module__module_name")
    ordering = ("course_name",)

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
