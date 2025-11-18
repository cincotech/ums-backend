import uuid

from django.core.exceptions import ValidationError
from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.university_app.models import AcademicYear
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.authorization_app.models import (
    Supervisor,
)
from services.foundational_service.auth_module.user_app.models import User


class ExamType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_type_name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "exam_types"


class Exam(models.Model):
    STATUS = (
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.RESTRICT)
    exam_type = models.ForeignKey(ExamType, on_delete=models.RESTRICT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.RESTRICT)
    exam_date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS, default="scheduled")
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "exams"


class ExamRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.RESTRICT, related_name="rooms")
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    range_student = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "exam_rooms"


class ExamSupervisor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_room = models.ForeignKey(
        ExamRoom, on_delete=models.RESTRICT, related_name="supervisors"
    )
    supervisor = models.ForeignKey(Supervisor, on_delete=models.RESTRICT)

    def clean(self):
        exam = self.exam_room.exam
        start = exam.start_time
        end = exam.end_time
        date = exam.exam_date
        conflits = ExamSupervisor.objects.filter(
            supervisor=self.supervisor,
            exam_room__exam__exam_date=date,
            exam_room__exam__start_time__lt=end,
            exam_room__exam__end_time__gt=start,
        ).exclude(pk=self.pk)
        if conflits.exists():
            raise ValidationError(
                f"Supervisor {self.supervisor.supervisor_name} {self.supervisor.supervisor_surname} has a scheduling conflict for the exam on {date} from {start} to {end}."
            )

    class Meta:
        db_table = "exam_supervisors"
        unique_together = ("exam_room", "supervisor")
