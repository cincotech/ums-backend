import uuid

from django.db import models

from services.core_service.academic_module.teacher_app.models import Attribution
from services.foundational_service.auth_module.user_app.models import User


class AttributionValidation(models.Model):
    VALIDATION_STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribution = models.OneToOneField(Attribution, on_delete=models.CASCADE)
    validated_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, null=True, blank=True
    )
    validation_status = models.CharField(
        max_length=20, choices=VALIDATION_STATUS, default="pending"
    )
    validation_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attribution_validations"
