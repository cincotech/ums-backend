import uuid

from django.db import models, transaction
from django.utils import timezone

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

    @property
    def is_active(self):
        """Academic year is active (not closed and within start/end dates)."""
        today = timezone.now().date()
        return not self.is_closed and self.start_date <= today <= self.end_date

    @property
    def is_future(self):
        """Academic year has not started yet."""
        return timezone.now().date() < self.start_date

    @property
    def is_past(self):
        """Academic year has ended."""
        return timezone.now().date() > self.end_date

    def close_year(self, closed_by_user):
        """
        Close this academic year:
        - Set is_closed=True
        - Set closed_date
        - Set closed_by
        - Mark all related inscriptions as closed using related_name
        """
        if self.is_closed:
            return  # Already closed
        if self.is_future:
            raise ValueError("Cannot close an academic year that has not started yet.")

        with transaction.atomic():
            self.is_closed = True
            self.closed_date = timezone.now().date()
            self.closed_by = closed_by_user
            self.save()

            # Use related_name 'inscriptions' to update all related Inscription objects
            self.inscriptions.update(is_year_close=True)

    def close_class_inscriptions(self, class_instance):
        """
        Close inscriptions for a specific class.
        Only affects inscriptions, does NOT close the academic year.
        """
        # Update all inscriptions of this class only
        self.inscriptions.filter(class_fk=class_instance, is_year_close=False).update(
            is_year_close=True
        )


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
