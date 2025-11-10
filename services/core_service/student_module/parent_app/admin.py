# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from .models import Parent, Profession


# ----------------------------
# Profession Resource
# ----------------------------
class ProfessionResource(resources.ModelResource):
    class Meta:
        model = Profession
        fields = ("id", "profession_name")
        export_order = ("id", "profession_name")


# ----------------------------
# Profession Admin
# ----------------------------
@admin.register(Profession)
class ProfessionAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ProfessionResource
    list_display = ("profession_name",)
    search_fields = ("profession_name",)
    ordering = ("profession_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }


# ----------------------------
# Parent Resource
# ----------------------------
class ParentResource(resources.ModelResource):
    profession_name = fields.Field(
        column_name="profession_name",
        attribute="profession",
        widget=ForeignKeyWidget(Profession, "profession_name"),
    )

    class Meta:
        model = Parent
        fields = (
            "id",
            "parent_name",
            "parent_phone",
            "parent_email",
            "profession",
            "profession_name",
            "parent_type",
            "is_alive",
            "is_contact_person",
        )
        export_order = (
            "id",
            "parent_name",
            "parent_phone",
            "parent_email",
            "profession_name",
            "parent_type",
            "is_alive",
            "is_contact_person",
        )


# ----------------------------
# Parent Admin
# ----------------------------
@admin.register(Parent)
class ParentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = ParentResource
    list_display = (
        "parent_name",
        "parent_phone",
        "profession",
        "parent_type",
        "is_alive",
        "is_contact_person",
    )
    search_fields = ("parent_name", "parent_phone", "profession__profession_name")
    list_filter = ("profession", "parent_type", "is_alive")
    ordering = ("parent_name",)
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
