import uuid

from django.db import models

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.faculty_app.models import TypeFormation
from services.core_service.academic_module.university_app.models import AcademicYear, UniversityDegree
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
    colline = models.ForeignKey(
        Colline, on_delete=models.RESTRICT, related_name="birthplaces"
    )
    cam = models.PositiveSmallIntegerField(null=True, blank=True)
    parent = models.ManyToManyField(Parent, related_name="students_parents")

    class Meta:
        db_table = "students"

    def get_active_matricule(self):
        """Retourne le StudentMatricule le plus récent (par année civile décroissante)."""
        return self.matricules.select_related('academic_year').order_by('-academic_year__civil_year', '-id').first()

    def __str__(self):
        active_sm = self.get_active_matricule()
        if active_sm:
            return f"{self.user.get_full_name()} ({active_sm.matricule})"
        return self.user.get_full_name()


class StudentFile(models.Model):
    """
    Model for storing student files/documents that universities can request
    during inscription process.
    """

    FILE_TYPES = [
        ("birth_certificate", "Birth Certificate"),
        ("highschool_diploma", "Highschool Diploma"),
        ("transcript", "Transcript/Report Card"),
        ("id_copy", "Copy of ID/Passport"),
        ("medical_certificate", "Medical Certificate"),
        ("photo", "Passport Photo"),
        ("parent_id_copy", "Parent ID Copy"),
        ("other", "Other Document"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="files")
    file_type = models.CharField(max_length=30, choices=FILE_TYPES)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="student_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_student_files",
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "student_files"
        unique_together = ("student", "file_type")

    def __str__(self):
        matricule = self.student.matricules.first()
        return f"{matricule.matricule if matricule else 'No matricule'} - {self.get_file_type_display()}"


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


class StudentMatricule(models.Model):
    """One matricule per student per TypeFormation (F, M, I, D)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="matricules"
    )
    type_formation = models.ForeignKey(
        TypeFormation, on_delete=models.RESTRICT, related_name="student_matricules"
    )
    matricule = models.CharField(max_length=120, unique=True)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.RESTRICT, related_name="student_matricules"
    )

    class Meta:
        db_table = "student_matricules"
        unique_together = ("student", "type_formation")

    def __str__(self):
        return f"{self.student.user.get_full_name()} | {self.type_formation.code} | {self.matricule}"
