import uuid

from django.db import models

from services.foundational_service.geo_module.commune_app.models import Commune


class Zone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone_name = models.CharField(max_length=45)
    commune = models.ForeignKey(
        Commune, on_delete=models.RESTRICT, related_name="zones"
    )

    class Meta:
        db_table = "zones"

    def __str__(self):
        return self.zone_name
