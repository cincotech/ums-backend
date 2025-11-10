# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.zone_app.models import Zone

from .models import Colline


# ----------------------------
# Import/Export Resource
# ----------------------------
class CollineResource(resources.ModelResource):
    zone_name = fields.Field(
        column_name="zone_name",
        attribute="zone",
        widget=ForeignKeyWidget(Zone, "zone_name"),
    )

    class Meta:
        model = Colline
        fields = ("id", "colline_name", "zone", "zone_name")
        export_order = ("id", "colline_name", "zone_name")


# ----------------------------
# Colline Admin
# ----------------------------
@admin.register(Colline)
class CollineAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CollineResource
    list_display = ("colline_name", "zone")
    list_filter = ("zone",)
    search_fields = ("colline_name", "zone__zone_name")
    ordering = ("colline_name",)

    fieldsets = (("Colline Information", {"fields": ("colline_name", "zone")}),)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
