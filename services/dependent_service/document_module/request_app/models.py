import uuid

from django.db import models

from services.core_service.finance_module.payment_app.models import Payment
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.document_module.document_app.models import Document


# Create your models here.
class Request(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("ready", "Ready"),
        ("collected", "Collected"),
        ("cancelled", "Cancelled"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    document = models.ForeignKey(Document, on_delete=models.RESTRICT)
    request_date = models.DateTimeField()
    request_status = models.CharField(max_length=12, choices=STATUS)
    payment_verified = models.BooleanField(default=False)
    admin_comment = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.RESTRICT, null=True, blank=True
    )

    class Meta:
        db_table = "requests"
