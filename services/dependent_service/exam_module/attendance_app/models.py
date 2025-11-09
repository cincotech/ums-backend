import uuid

from django.db import models

from services.core_service.student_module.card_app.models import StudentCard
from services.core_service.student_module.inscription_app.models import Inscription
from services.dependent_service.exam_module.exam_app.models import ExamRoom


# Create your models here.
class ExamAttendance(models.Model):

    STATUS = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("unauthorized", "Unauthorized"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    examroom = models.ForeignKey(ExamRoom, on_delete=models.RESTRICT)
    card = models.ForeignKey(
        StudentCard, on_delete=models.RESTRICT, null=True, blank=True
    )
    inscription = models.ForeignKey(Inscription, on_delete=models.RESTRICT)
    attendance_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=STATUS, default="present")

    class Meta:
        db_table = "exam_attendances"
