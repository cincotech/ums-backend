# Register your models here.
from django.contrib import admin
from django.db import models
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from unfold.admin import ModelAdmin

from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User

from .models import Equipment, EquipmentAllocation, EquipmentMaintenance, EquipmentType


# ----------------------------
# EquipmentType Resource
# ----------------------------
class EquipmentTypeResource(resources.ModelResource):
    class Meta:
        model = EquipmentType
        fields = ("id", "name")
        export_order = ("id", "name")


@admin.register(EquipmentType)
class EquipmentTypeAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = EquipmentTypeResource
    list_display = ("name",)
    search_fields = ("name",)


# ----------------------------
# Equipment Resource
# ----------------------------
class EquipmentResource(resources.ModelResource):
    equipment_type_name = fields.Field(
        column_name="equipment_type_name",
        attribute="equipment_type",
        widget=ForeignKeyWidget(EquipmentType, "name"),
    )

    class Meta:
        model = Equipment
        fields = (
            "id",
            "equipment_name",
            "equipment_type",
            "equipment_type_name",
            "serial_number",
            "equipment_number",
            "purchase_date",
            "status",
        )
        export_order = (
            "id",
            "equipment_name",
            "equipment_type_name",
            "serial_number",
            "equipment_number",
            "purchase_date",
            "status",
        )


@admin.register(Equipment)
class EquipmentAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = EquipmentResource
    list_display = ("equipment_name", "equipment_type", "equipment_number", "status")
    list_filter = ("status", "equipment_type")
    search_fields = ("equipment_name", "equipment_number", "equipment_type__name")
    ordering = ("equipment_name",)
    fieldsets = (
        (
            "Equipment Information",
            {
                "fields": (
                    "equipment_name",
                    "equipment_type",
                    "serial_number",
                    "equipment_number",
                    "purchase_date",
                    "status",
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
# EquipmentAllocation Resource
# ----------------------------
class EquipmentAllocationResource(resources.ModelResource):
    equipment_name = fields.Field(
        column_name="equipment_name",
        attribute="equipment",
        widget=ForeignKeyWidget(Equipment, "equipment_name"),
    )
    room_name = fields.Field(
        column_name="room_name",
        attribute="room",
        widget=ForeignKeyWidget(Room, "room_name"),
    )
    allocated_user_email = fields.Field(
        column_name="allocated_user_email",
        attribute="allocated_to",
        widget=ForeignKeyWidget(User, "email"),
    )

    class Meta:
        model = EquipmentAllocation
        fields = (
            "id",
            "equipment",
            "equipment_name",
            "room",
            "room_name",
            "allocated_to",
            "allocated_user_email",
            "allocation_date",
            "return_date",
            "status",
        )
        export_order = (
            "id",
            "equipment_name",
            "room_name",
            "allocated_user_email",
            "allocation_date",
            "return_date",
            "status",
        )


@admin.register(EquipmentAllocation)
class EquipmentAllocationAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = EquipmentAllocationResource
    list_display = (
        "equipment",
        "room",
        "allocated_to",
        "allocation_date",
        "return_date",
        "status",
    )
    list_filter = ("status", "room")
    search_fields = (
        "equipment__equipment_name",
        "room__room_name",
        "allocated_to__email",
    )
    ordering = ("allocation_date",)
    fieldsets = (
        (
            "Allocation Information",
            {
                "fields": (
                    "equipment",
                    "room",
                    "allocated_to",
                    "allocation_date",
                    "return_date",
                    "status",
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
# EquipmentMaintenance Resource
# ----------------------------
class EquipmentMaintenanceResource(resources.ModelResource):
    equipment_name = fields.Field(
        column_name="equipment_name",
        attribute="equipment",
        widget=ForeignKeyWidget(Equipment, "equipment_name"),
    )

    class Meta:
        model = EquipmentMaintenance
        fields = (
            "id",
            "equipment",
            "equipment_name",
            "maintenance_date",
            "return_date",
            "description",
            "performed_by",
            "cost",
        )
        export_order = (
            "id",
            "equipment_name",
            "maintenance_date",
            "return_date",
            "description",
            "performed_by",
            "cost",
        )


@admin.register(EquipmentMaintenance)
class EquipmentMaintenanceAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_class = EquipmentMaintenanceResource
    list_display = (
        "equipment",
        "maintenance_date",
        "return_date",
        "performed_by",
        "cost",
    )
    list_filter = ("maintenance_date",)
    search_fields = ("equipment__equipment_name", "performed_by")
    ordering = ("maintenance_date",)
    fieldsets = (
        (
            "Maintenance Information",
            {
                "fields": (
                    "equipment",
                    "maintenance_date",
                    "return_date",
                    "description",
                    "performed_by",
                    "cost",
                )
            },
        ),
    )
    formfield_overrides = {
        models.CharField: {
            "widget": admin.widgets.AdminTextInputWidget(attrs={"class": "vTextField"})
        },
    }
