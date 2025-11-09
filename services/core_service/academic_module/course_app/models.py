import uuid

from django.db import models

from services.core_service.academic_module.module_app.models import Module


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module, on_delete=models.RESTRICT, related_name="courses"
    )
    course_name = models.CharField(max_length=255, null=True, blank=True)
    cm = models.PositiveSmallIntegerField(null=True, blank=True)
    td = models.PositiveSmallIntegerField(null=True, blank=True)
    tp = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "courses"
