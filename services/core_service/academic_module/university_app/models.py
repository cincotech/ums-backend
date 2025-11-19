import uuid

from django.db import models

from services.foundational_service.auth_module.user_app.models import User
from services.foundational_service.geo_module.country_app.models import Country


class AcademicYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.CharField(max_length=15)
    description = models.CharField(max_length=255)
    civil_year = models.CharField(max_length=4)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    closed_date = models.DateField(null=True, blank=True)
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_academic_years",
    )

    class Meta:
        db_table = "academic_years"

    def __str__(self):
        return self.academic_year


class University(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university_name = models.CharField(max_length=255)
    university_abrev = models.CharField(max_length=15, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.RESTRICT, related_name="universities"
    )

    def __str__(self):
        return self.university_name

    class Meta:
        db_table = "universities"


class UniversityDegree(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    degree_name = models.CharField(max_length=255)
    description = models.CharField(max_length=200)

    class Meta:
        db_table = "university_degrees"

    def __str__(self):
        return self.degree_name
