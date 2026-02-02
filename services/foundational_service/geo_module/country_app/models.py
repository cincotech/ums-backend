import uuid

from django.db import models


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, null=True, blank=True)
    country_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "countries"

    def __str__(self):
        return self.country_name
