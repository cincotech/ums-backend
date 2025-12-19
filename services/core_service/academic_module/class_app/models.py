import uuid

from django.db import models

from services.core_service.academic_module.department_app.models import Department
from services.core_service.academic_module.university_app.models import AcademicYear


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=50)  # ex: "L1 Informatique"
    department = models.ForeignKey(
        Department, on_delete=models.RESTRICT, related_name="classes"
    )

    class Meta:
        db_table = "classes"
        unique_together = ("class_name", "department")

    def __str__(self):
        return f"{self.class_name} - {self.department.department_name}-{self.department.faculty.faculty_name}"


class ClassGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="groups")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.RESTRICT)
    group_name = models.CharField(max_length=50)  # ex: "G1", "G2"
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "class_groups"
        unique_together = ("class_fk", "academic_year", "group_name")

    def __str__(self):
        return f"{self.group_name} ({self.class_fk.class_name} - {self.academic_year})"
