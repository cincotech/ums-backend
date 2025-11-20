import uuid

from django.db import models

from services.core_service.academic_module.faculty_app.models import Faculty


# Create your models here.
class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=255)
    abreviation = models.CharField(max_length=20)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.RESTRICT, related_name="departments"
    )

    def __str__(self):
        return self.department_name

    class Meta:
        db_table = "departments"
