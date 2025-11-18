import uuid

from django.db import models

from services.dependent_service.infrastructure_module.building_app.models import (
    Building,
)


# Create your models here.
class Room(models.Model):
    ROOM_TYPE = (
        ("classroom", "Classroom"),
        ("laboratory", "Laboratory"),
        ("amphi", "Amphi"),
        ("office", "Office"),
        ("meeting", "Meeting"),
    )
    building = models.ForeignKey(
        Building, on_delete=models.RESTRICT, related_name="rooms"
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE, default="classroom")
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "rooms"
