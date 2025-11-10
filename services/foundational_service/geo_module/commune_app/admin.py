# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.province_app.models import Province

from .models import Commune


# ----------------------------
# Import/Export Resource
# ----------------------------
class CommuneResource(resources.ModelResource):
    province_name = fields.Field(
        column_name="province_name",
        attribute="province",
        widget=ForeignKeyWidget(Province, "province_name"),
    )

    class Meta:
        model = Commune
        fields = ("id", "commune_name", "province", "province_name")
        export_order = ("id", "commune_name", "province_name")


# ----------------------------
# Commune Admin
# ----------------------------
@admin.register(Commune)
class CommuneAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CommuneResource
    list_display = ("commune_name", "province")
    list_filter = ("province",)
    search_fields = ("commune_name", "province__province_name")
    ordering = ("commune_name",)

    fieldsets = (("Commune Information", {"fields": ("commune_name", "province")}),)

    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
