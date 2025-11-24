import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class


class Module(models.Model):
    SEMESTER_CHOICES = [(str(i), str(i)) for i in range(1, 13)]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="modules"
    )
    module_name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    semester_id = models.CharField(max_length=2, choices=SEMESTER_CHOICES)

    class Meta:
        db_table = "modules"

    def __str__(self):
        return f"{self.module_name} ({self.semester_id})"

    @property
    def total_credits(self):
        """
        Calculate the total credits of all courses in this module.
        """
        return self.courses.aggregate(total=models.Sum("credits"))["total"] or 0
