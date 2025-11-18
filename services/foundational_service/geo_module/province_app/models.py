import uuid

from django.db import models

from services.foundational_service.geo_module.country_app.models import Country


class Province(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    province_name = models.CharField(max_length=45)
    country = models.ForeignKey(
        Country, on_delete=models.RESTRICT, related_name="provinces"
    )

    class Meta:
        db_table = "provinces"
        unique_together = ("country", "province_name")

    def __str__(self):
        """Retourne le nom lisible de la province."""
        return self.province_name
