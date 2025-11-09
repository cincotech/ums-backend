import uuid

from django.db import models

from services.foundational_service.geo_module.commune_app.models import Commune
from services.foundational_service.geo_module.zone_app.models import Zone


# Create your models here.
class Highschool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hs_name = models.CharField(max_length=255)
    zone = models.ForeignKey(
        Zone, on_delete=models.RESTRICT, related_name="highschools"
    )
    code = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "highschools"


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section_name = models.CharField(max_length=100)

    class Meta:
        db_table = "sections"


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_name = models.CharField(max_length=255)
    section = models.ForeignKey(
        Section, on_delete=models.RESTRICT, related_name="certificates"
    )

    class Meta:
        db_table = "certificates"


class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option_name = models.CharField(max_length=45)
    section = models.ForeignKey(
        Section, on_delete=models.RESTRICT, related_name="options"
    )

    class Meta:
        db_table = "options"


class TrainingCenter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    commune = models.ForeignKey(
        Commune, on_delete=models.RESTRICT, related_name="training_centers"
    )

    class Meta:
        db_table = "training_centers"
