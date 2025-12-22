import uuid

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
    user = models.OneToOneField(
        User, on_delete=models.RESTRICT, related_name="teachers"
    )
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
        return self.user.email


class Attribution(models.Model):
    STATUS = (("Pending", "Pending"), ("Accepted", "Accepted"), ("Refused", "Refused"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    principal_teacher = models.ForeignKey(
        Teacher, on_delete=models.RESTRICT, related_name="principal_attributions"
    )
    substitute_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="substitute_attributions",
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.RESTRICT)
    date_attribution = models.DateField()
    status_principal_teacher = models.CharField(
        max_length=10, choices=STATUS, default="Pending"
    )
    status_substitute_teacher = models.CharField(
        max_length=10, choices=STATUS, default="Pending"
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

    class Meta:
        db_table = "attributions"


class Suggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion_date = models.DateField()
    suggestion = models.TextField(null=True, blank=True)
    attribution = models.ForeignKey(Attribution, on_delete=models.RESTRICT)
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)

    class Meta:
        db_table = "suggestions"
