import uuid

from django.db import models

from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User


# Create your models here.
class EquipmentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=45)


class Equipment(models.Model):

    STATUS = (
        ("working", "Working"),
        ("available", "Available"),
        ("under_maintenance", "Under Maintenance"),
        ("out_of_order", "Out of Order"),
        ("disposed", "Disposed"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment_name = models.CharField(max_length=100)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.RESTRICT)
    serial_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    equipment_number = models.CharField(max_length=9)
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=86, choices=STATUS, default="available")

    class Meta:
        db_table = "equipments"


class EquipmentAllocation(models.Model):
    STATUS = (("active", "Active"), ("returned", "Returned"), ("lost", "Lost"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.RESTRICT)
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    allocated_to = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True
    )
    allocation_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=120, choices=STATUS, default="active")

    class Meta:
        db_table = "equipment_allocations"


class EquipmentMaintenance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(
        Equipment, on_delete=models.RESTRICT, related_name="maintenances"
    )
    maintenance_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    performed_by = models.CharField(max_length=255, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = "equipment_maintenance"
