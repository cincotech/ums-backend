import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student


# Create your models here.
class Inscription(models.Model):
    GROUPE = [(chr(65 + i), chr(65 + i)) for i in range(26)]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    date_inscription = models.DateField()
    regist_status = models.CharField(max_length=4, default="ACT")
    groupe = models.CharField(max_length=1, choices=GROUPE, default="A")
    withdrawal_date = models.DateField(null=True, blank=True)
    is_year_close = models.BooleanField(default=False)

    class Meta:
        db_table = "inscriptions"
        unique_together = ("student", "academic_year", "class_fk")
