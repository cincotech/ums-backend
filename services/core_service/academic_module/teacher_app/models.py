import uuid

from django.core.exceptions import ValidationError
from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.university_app.models import (
    AcademicYear,
    University,
    UniversityDegree,
)
from services.foundational_service.auth_module.user_app.models import User


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, related_name="teacher")
    teacher_grade = models.CharField(max_length=200)
    degree = models.ForeignKey(UniversityDegree, on_delete=models.RESTRICT)
    university = models.ForeignKey(University, on_delete=models.RESTRICT)
    speciality = models.CharField(max_length=255, null=True, blank=True)
    url_cv = models.URLField(null=True, blank=True)
    url_other = models.JSONField(default=list, null=True, blank=True)
    url_diploma = models.FileField(upload_to="Teacher_diploma", null=True, blank=True)
    # is_visitor = models.BooleanField(default=False)

    class Meta:
        db_table = "teachers"

    def __str__(self):
        if self.user:
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            return full_name if full_name else self.user.email
        return "Teacher (no user)"


class Attribution(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_REFUSED = "Refused"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REFUSED, "Refused"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    principal_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="principal_attributions",
    )

    substitute_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="substitute_attributions",
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.RESTRICT)
    date_attribution = models.DateField(null=True, blank=True)

    status_principal_teacher = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    status_substitute_teacher = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    commentaire = models.TextField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="submitted_attributions"
    )
    authorized_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="authorized_attributions",
    )
    # Validation fields
    validated_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="validated_attributions",
    )
    validation_date = models.DateTimeField(null=True, blank=True)
    validation_comments = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attributions"

    def clean(self):
        """Validate that substitute_teacher is different from principal_teacher."""
        super().clean()
        if (
            self.substitute_teacher_id
            and self.substitute_teacher_id == self.principal_teacher_id
        ):
            raise ValidationError(
                {
                    "substitute_teacher": "Le professeur remplaçant doit être différent du professeur principal."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Suggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion_date = models.DateField()
    suggestion = models.TextField(null=True, blank=True)
    attribution = models.ForeignKey(Attribution, on_delete=models.RESTRICT)
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)

    class Meta:
        db_table = "suggestions"


def decide_principal_teacher(self, decision: str):
    """
    decision = Accepted | Refused
    """
    if decision not in [self.STATUS_ACCEPTED, self.STATUS_REFUSED]:
        raise ValueError("Décision invalide")

    self.status_principal_teacher = decision

    # Règle miroir automatique
    if decision == self.STATUS_ACCEPTED:
        self.status_substitute_teacher = self.STATUS_REFUSED
    else:
        self.status_substitute_teacher = self.STATUS_ACCEPTED


def refuse_principal_teacher(self):
    """
    Cas métier :
    - Le teacher principal est refusé
    """
    self.status_principal_teacher = self.STATUS_REFUSED
