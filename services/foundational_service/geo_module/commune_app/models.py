import uuid

from django.db import models

from services.foundational_service.geo_module.province_app.models import Province


class Commune(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commune_name = models.CharField(max_length=45)
    province = models.ForeignKey(
        Province, on_delete=models.RESTRICT, related_name="communes"
    )

    class Meta:
        db_table = "communes"

    def __str__(self):
        """Retourne le nom lisible de la commune."""
        return self.commune_name
