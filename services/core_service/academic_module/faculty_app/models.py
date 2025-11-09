import uuid

from django.db import models

from services.core_service.academic_module.university_app.models import University


class TypeFormation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=5)
    description = models.TextField(null=True, blank=True)


class Faculty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty_name = models.CharField(max_length=255)
    faculty_abreviation = models.CharField(max_length=10, null=True, blank=True)
    types = models.ForeignKey(
        TypeFormation, on_delete=models.RESTRICT, related_name="typeformation"
    )
    university = models.ForeignKey(
        University,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="faculties",
    )

    class Meta:
        db_table = "faculties"
