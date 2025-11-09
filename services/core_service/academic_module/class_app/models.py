import uuid

from django.db import models

from services.core_service.academic_module.department_app.models import Department


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=10)
    department = models.ForeignKey(
        Department, on_delete=models.RESTRICT, related_name="classes"
    )
    class_group = models.JSONField(default=list)

    class Meta:
        db_table = "classes"
