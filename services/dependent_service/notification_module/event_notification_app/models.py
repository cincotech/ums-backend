import uuid

from django.db import models


# Create your models here.
class Notification(models.Model):
    DELIVERY = (("sent", "Sent"), ("failed", "Failed"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=125, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField()
    delivery_status = models.CharField(max_length=6, choices=DELIVERY)

    class Meta:
        db_table = "notifications"
