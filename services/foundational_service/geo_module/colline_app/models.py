import uuid

from django.db import models

from services.foundational_service.geo_module.zone_app.models import Zone


class Colline(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    colline_name = models.CharField(max_length=45)
    zone = models.ForeignKey(Zone, on_delete=models.RESTRICT, related_name="collines")

    class Meta:
        db_table = "collines"

    def __str__(self):
        """Retourne le nom lisible de la colline."""
        return self.colline_name
