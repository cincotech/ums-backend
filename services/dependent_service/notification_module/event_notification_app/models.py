import uuid

from django.db import models


# Create your models here.
class Notification(models.Model):
    """External notification delivery (email/SMS)

    Note: This is different from dashboard_shared_app.Notification
    which handles in-app notifications for users.

    This model tracks external notification delivery via email/SMS.
    """

    DELIVERY = (("sent", "Sent"), ("failed", "Failed"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=125, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField()
    delivery_status = models.CharField(max_length=6, choices=DELIVERY)

    class Meta:
        db_table = (
            "external_notifications"  # Changed from "notifications" to avoid conflict
        )
