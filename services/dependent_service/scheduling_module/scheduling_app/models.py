import uuid

from django.db import models

from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.infrastructure_module.room_app.models import Room


class ScheduleSlot(models.Model):
    DAY = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day_of_week = models.CharField(max_length=9, choices=DAY)
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule_name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "schedule_slots"
    def __str__(self):
        return self.schedule_name

class Timetable(models.Model):
    STATUS = (
        ("Planned", "Planned"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribution = models.ForeignKey(Attribution, on_delete=models.RESTRICT,blank=True,null=True)
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    slot = models.ManyToManyField(ScheduleSlot)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, null=True, blank=True)

    class Meta:
        db_table = "timetables"


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS = (("Present", "Present"), ("Absent", "Absent"), ("Excused", "Excused"))
    timetable = models.ForeignKey(
        Timetable, on_delete=models.RESTRICT, related_name="attendances"
    )
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    status = models.CharField(max_length=8, choices=STATUS)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attendances"


class ActivityReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable = models.ForeignKey(
        Timetable, on_delete=models.RESTRICT, related_name="activity_reports"
    )
    planned_hours = models.PositiveIntegerField(null=True, blank=True)
    delivered_hours = models.PositiveIntegerField(null=True, blank=True)
    completion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    observations = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "activity_reports"
