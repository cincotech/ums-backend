# Register your models here.
from django.contrib import admin
from django.db import models

# ----------------------------
# Highschool Resource
# ----------------------------
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.zone_app.models import Zone

from .models import Certificate, Highschool, Option, Section, TrainingCenter


class HighschoolResource(resources.ModelResource):

    # Used ONLY for export
    zone_name = fields.Field(
        column_name="zone_name",
        attribute="zone",
        widget=ForeignKeyWidget(Zone, "zone_name"),
        readonly=True,  # ✅ Prevent importing using zone_name
    )

    class Meta:
        model = Highschool
        fields = ("id", "hs_name", "zone", "zone_name", "code")
        export_order = ("id", "hs_name", "zone_name", "code")


# ----------------------------
# Highschool Admin
# ----------------------------
@admin.register(Highschool)
class HighschoolAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = HighschoolResource
    list_display = ("hs_name", "zone", "code")
    search_fields = ("hs_name", "zone__zone_name", "code")
    list_filter = ("zone",)
    ordering = ("hs_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Section Resource
# ----------------------------
class SectionResource(resources.ModelResource):
    class Meta:
        model = Section
        fields = ("id", "section_name")
        export_order = ("id", "section_name")


@admin.register(Section)
class SectionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = SectionResource
    list_display = ("section_name",)
    search_fields = ("section_name",)
    ordering = ("section_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Certificate Resource
# ----------------------------
class CertificateResource(resources.ModelResource):
    section_name = fields.Field(
        column_name="section_name",
        attribute="section",
        widget=ForeignKeyWidget(Section, "section_name"),
    )

    class Meta:
        model = Certificate
        fields = ("id", "certificate_name", "section", "section_name")
        export_order = ("id", "certificate_name", "section_name")


@admin.register(Certificate)
class CertificateAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = CertificateResource
    list_display = ("certificate_name", "section")
    search_fields = ("certificate_name", "section__section_name")
    list_filter = ("section",)
    ordering = ("certificate_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Option Resource
# ----------------------------
class OptionResource(resources.ModelResource):
    section_name = fields.Field(
        column_name="section_name",
        attribute="section",
        widget=ForeignKeyWidget(Section, "section_name"),
    )

    class Meta:
        model = Option
        fields = ("id", "option_name", "section", "section_name")
        export_order = ("id", "option_name", "section_name")


@admin.register(Option)
class OptionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = OptionResource
    list_display = ("option_name", "section")
    search_fields = ("option_name", "section__section_name")
    list_filter = ("section",)
    ordering = ("option_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# TrainingCenter Resource
# ----------------------------
class TrainingCenterResource(resources.ModelResource):
    commune_name = fields.Field(
        column_name="commune_name",
        attribute="commune",
        widget=ForeignKeyWidget(
            Commune, "commune_name"
        ),  # assuming Commune has 'commune_name'
    )

    class Meta:
        model = TrainingCenter
        fields = ("id", "name", "commune", "commune_name")
        export_order = ("id", "name", "commune_name")


@admin.register(TrainingCenter)
class TrainingCenterAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = TrainingCenterResource
    list_display = ("name", "commune")
    search_fields = ("name", "commune__commune_name")
    list_filter = ("commune",)
    ordering = ("name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
