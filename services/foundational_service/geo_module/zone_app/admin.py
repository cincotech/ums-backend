# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.commune_app.models import Commune

from .models import Zone


# ----------------------------
# Import/Export Resource
# ----------------------------
class ZoneResource(resources.ModelResource):
    commune_name = fields.Field(
        column_name="commune_name",
        attribute="commune",
        widget=ForeignKeyWidget(Commune, "commune_name"),
    )

    class Meta:
        model = Zone
        fields = ("id", "zone_name", "commune", "commune_name")
        export_order = ("id", "zone_name", "commune_name")


# ----------------------------
# Zone Admin
# ----------------------------
@admin.register(Zone)
class ZoneAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ZoneResource
    list_display = ("zone_name", "commune")
    list_filter = ("commune",)
    search_fields = ("zone_name", "commune__commune_name")
    ordering = ("zone_name",)

    fieldsets = (("Zone Information", {"fields": ("zone_name", "commune")}),)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
