import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class


class Semester(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.PositiveSmallIntegerField(unique=True)  # 1–12
    name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "semesters"
        ordering = ["number"]

    def __str__(self):
        return self.name or f"Semester {self.number}"


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="modules"
    )
    module_name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name="modules"
    )

    class Meta:
        db_table = "modules"

    def __str__(self):
        return f"{self.module_name} ({self.semester})"

    @property
    def total_credits(self):
        return self.courses.aggregate(total=models.Sum("credits"))["total"] or 0
