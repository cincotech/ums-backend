import uuid

from django.db import models

from services.core_service.academic_module.module_app.models import Module


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module, on_delete=models.RESTRICT, related_name="courses"
    )
    course_code = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255)
    cm = models.PositiveSmallIntegerField(default=0)  # Lecture hours
    td = models.PositiveSmallIntegerField(default=0)  # Tutorial hours
    tp = models.PositiveSmallIntegerField(default=0)  # Lab hours
    credits = models.PositiveSmallIntegerField(default=0)  # ECTS or equivalent

    class Meta:
        db_table = "courses"
        unique_together = ("module", "course_name")

    def __str__(self):
        return f"{self.course_name} - {self.credits} credits -{self.module.class_fk.class_name}"
