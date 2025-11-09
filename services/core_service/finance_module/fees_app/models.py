import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear


class Wording(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wording_name = models.CharField(max_length=60)

    class Meta:
        db_table = "wordings"


class FeesSheet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="fees_sheets_class"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="fees_sheets_academicyear"
    )
    wording = models.ForeignKey(
        Wording, on_delete=models.RESTRICT, related_name="fees_sheets_wording"
    )
    base_amount = models.PositiveIntegerField()
    installements = models.JSONField(default=list, null=True)

    class Meta:
        db_table = "fees_sheets"
