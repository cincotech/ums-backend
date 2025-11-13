import uuid

from django.db import models

from services.core_service.academic_module.university_app.models import University


class TypeFormation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    code = models.CharField(
        max_length=2, unique=True, blank=True, help_text="Code for the type: F, I, M, D"
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        db_table = "type_formations"


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
