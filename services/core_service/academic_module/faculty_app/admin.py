# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.university_app.models import University

from .models import Faculty, TypeFormation


# ----------------------------
# TypeFormation Resource
# ----------------------------
class TypeFormationResource(resources.ModelResource):
    class Meta:
        model = TypeFormation
        fields = ("id", "name", "description", "code")
        export_order = ("id", "name", "description", "code")


# ----------------------------
# Faculty Resource
# ----------------------------
class FacultyResource(resources.ModelResource):
    university_name = fields.Field(
        column_name="university_name",
        attribute="university",
        widget=ForeignKeyWidget(University, "university_name"),
    )

    type_name = fields.Field(
        column_name="typeformation_name",
        attribute="types",
        widget=ForeignKeyWidget(TypeFormation, "name"),
    )

    class Meta:
        model = Faculty
        fields = (
            "id",
            "faculty_name",
            "faculty_abreviation",
            "types",
            "type_name",
            "university",
            "university_name",
        )
        export_order = (
            "id",
            "faculty_name",
            "faculty_abreviation",
            "type_name",
            "university_name",
        )


# ----------------------------
# TypeFormation Admin
# ----------------------------
@admin.register(TypeFormation)
class TypeFormationAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = TypeFormationResource
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)

    fieldsets = (("Type Formation Information", {"fields": ("name", "description")}),)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Faculty Admin
# ----------------------------
@admin.register(Faculty)
class FacultyAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = FacultyResource
    list_display = ("faculty_name", "faculty_abreviation", "types", "university")
    list_filter = ("types", "university")
    search_fields = (
        "faculty_name",
        "faculty_abreviation",
        "university__university_name",
    )
    ordering = ("faculty_name",)

    fieldsets = (
        (
            "Faculty Information",
            {"fields": ("faculty_name", "faculty_abreviation", "types", "university")},
        ),
    )

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
