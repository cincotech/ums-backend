import uuid

from django.db import models

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.university_app.models import UniversityDegree
from services.core_service.student_module.highschool_info_app.models import (
    Certificate,
    Highschool,
    TrainingCenter,
)
from services.core_service.student_module.parent_app.models import Parent
from services.foundational_service.auth_module.user_app.models import User
from services.foundational_service.geo_module.colline_app.models import Colline


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.RESTRICT, related_name="students_users"
    )
    matricule = models.CharField(max_length=120, unique=True, null=True, blank=True)
    colline = models.ForeignKey(
        Colline, on_delete=models.RESTRICT, related_name="birthplaces"
    )
    cam = models.PositiveSmallIntegerField(null=True, blank=True)
    parent = models.ManyToManyField(Parent, related_name="students_parents")

    class Meta:
        db_table = "students"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricule})"


class Training(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domaine = models.CharField(max_length=255)
    certificate = models.CharField(max_length=255)
    training_center = models.ForeignKey(
        TrainingCenter, on_delete=models.RESTRICT, null=True, blank=True
    )

    class Meta:
        db_table = "trainings"


class StudentHsInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="hs_infos"
    )
    highschool = models.ForeignKey(Highschool, on_delete=models.RESTRICT)
    certificate = models.ForeignKey(Certificate, on_delete=models.RESTRICT)
    se_mark = models.CharField(max_length=6, null=True, blank=True)
    date_of_obtention = models.PositiveSmallIntegerField()
    formation = models.ManyToManyField(Training, related_name="formations")

    class Meta:
        db_table = "student_hs_info"


class StudentGraduateInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="graduate_infos"
    )
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    option = models.CharField(max_length=127, null=True, blank=True)
    mention = models.CharField(max_length=45)
    degree = models.ForeignKey(UniversityDegree, on_delete=models.RESTRICT)

    class Meta:
        db_table = "student_graduate_info"
