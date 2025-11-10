# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.dependent_service.infrastructure_module.building_app.models import (
    Building,
)

from .models import Room


# ----------------------------
# Room Resource
# ----------------------------
class RoomResource(resources.ModelResource):
    building_name = fields.Field(
        column_name="building_name",
        attribute="building",
        widget=ForeignKeyWidget(Building, "building_name"),
    )

    class Meta:
        model = Room
        fields = (
            "id",
            "room_name",
            "building",
            "building_name",
            "capacity",
            "room_type",
            "is_available",
        )
        export_order = (
            "id",
            "room_name",
            "building_name",
            "capacity",
            "room_type",
            "is_available",
        )


# ----------------------------
# Room Admin
# ----------------------------
@admin.register(Room)
class RoomAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = RoomResource
    list_display = ("room_name", "building", "room_type", "capacity", "is_available")
    list_filter = ("building", "room_type", "is_available")
    search_fields = ("room_name", "building__building_name")
    ordering = ("room_name",)
    fieldsets = (
        (
            "Room Information",
            {
                "fields": (
                    "room_name",
                    "building",
                    "room_type",
                    "capacity",
                    "is_available",
                )
            },
        ),
    )

    # Optional: Customize Unfold form fields
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
