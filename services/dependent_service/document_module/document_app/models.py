import uuid

from django.db import models


# Create your models here.
class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_name = models.CharField(max_length=100)
    document_description = models.TextField(null=True, blank=True)
    document_price = models.PositiveIntegerField(default=0)
    processing_time = models.PositiveIntegerField(default=5)

    class Meta:
        db_table = "documents"
