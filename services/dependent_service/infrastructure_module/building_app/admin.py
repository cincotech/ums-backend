# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.core_service.academic_module.university_app.models import University

from .models import Building


# ----------------------------
# Building Resource
# ----------------------------
class BuildingResource(resources.ModelResource):
    university_name = fields.Field(
        column_name="university_name",
        attribute="university",
        widget=ForeignKeyWidget(University, "university_name"),
    )

    class Meta:
        model = Building
        fields = (
            "id",
            "building_name",
            "building_code",
            "location",
            "university",
            "university_name",
        )
        export_order = (
            "id",
            "building_name",
            "building_code",
            "location",
            "university_name",
        )


# ----------------------------
# Building Admin
# ----------------------------
@admin.register(Building)
class BuildingAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = BuildingResource
    list_display = ("building_name", "building_code", "university", "location")
    list_filter = ("university",)
    search_fields = ("building_name", "building_code", "university__university_name")
    ordering = ("building_name",)
    fieldsets = (
        (
            "Building Information",
            {"fields": ("university", "building_name", "building_code", "location")},
        ),
    )

    # Optional: Customize Unfold form fields
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
