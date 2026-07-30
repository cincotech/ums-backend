# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin, TabularInline

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course

from .models import Module, Semester


# ----------------------------
# Course Inline for Module
# ----------------------------
class CourseInline(TabularInline):
    model = Course
    extra = 0
    fields = (
        "course_code",
        "course_name",
        "cm",
        "td",
        "tp",
        "credits",
    )
    formfield_overrides = {
        models.PositiveSmallIntegerField: {
            "widget": admin.widgets.AdminIntegerFieldWidget(attrs={"size": 4})
        },
    }


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
        fields = (
            "id",
            "module_name",
            "code",
            "semester",
            "class_fk",
            "class_name",
            "total_credits",
        )
        export_order = (
            "id",
            "module_name",
            "code",
            "semester",
            "class_name",
            "total_credits",
        )


# ----------------------------
# Module Admin
# ----------------------------
@admin.register(Module)
class ModuleAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ModuleResource
    inlines = [CourseInline]
    list_display = ("module_name", "code", "semester", "class_fk", "total_credits")
    list_filter = ("semester", "class_fk")
    search_fields = ("module_name", "code", "class_fk__class_name")
    ordering = ("class_fk__class_name", "semester__number", "module_name")

    readonly_fields = ("total_credits",)

    fieldsets = (
        (
            "UE Information",
            {
                "fields": (
                    "module_name",
                    "code",
                    "semester",
                    "class_fk",
                    "total_credits",
                )
            },
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Semester Admin
# ----------------------------
@admin.register(Semester)
class SemesterAdmin(ModelAdmin):
    list_display = ("number", "name")
    search_fields = ("name",)
    ordering = ("number",)
