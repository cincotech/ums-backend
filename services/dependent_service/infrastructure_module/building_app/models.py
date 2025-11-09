import uuid

from django.db import models

from services.core_service.academic_module.university_app.models import University


# Create your models here.
class Building(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university = models.ForeignKey(
        University, on_delete=models.RESTRICT, related_name="buildings"
    )
    building_name = models.CharField(max_length=100)
    building_code = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "buildings"
