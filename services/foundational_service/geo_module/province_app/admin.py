from django.contrib import admin
from django.db import models
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.country_app.models import Country

from .models import Province


# ----------------------------
# Import/Export Resource
# ----------------------------
class ProvinceResource(resources.ModelResource):
    country_name = resources.Field(
        column_name="country_name",
        attribute="country",
        widget=resources.widgets.ForeignKeyWidget(Country, "country_name"),
    )

    class Meta:
        model = Province
        fields = ("id", "province_name", "country", "country_name")
        export_order = ("id", "province_name", "country_name")


# ----------------------------
# Province Admin
# ----------------------------
@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProvinceResource
    list_display = ("province_name", "country")
    list_filter = ("country",)
    search_fields = ("province_name", "country__country_name")
    ordering = ("province_name",)

    fieldsets = (("Province Information", {"fields": ("province_name", "country")}),)

    # Optional: Customize Unfold form fields (if you have Unfold widgets)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
