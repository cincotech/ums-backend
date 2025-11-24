import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import ClassGroup
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User


class ScheduleSlot(models.Model):
    DAYS = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day_of_week = models.CharField(max_length=9, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule_name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "schedule_slots"

    def __str__(self):
        return f"{self.name} ({self.day_of_week} {self.start_time}-{self.end_time})"


class Timetable(models.Model):
    STATUS_CHOICES = (
        ("Planned", "Planned"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="timetables",
        blank=True,
        null=True,
    )
    attribution = models.ForeignKey(
        Attribution, on_delete=models.RESTRICT, blank=True, null=True
    )
    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    slots = models.ManyToManyField(ScheduleSlot)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, null=True, blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_timetables"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "timetables"
        unique_together = ("class_group", "room", "start_date", "end_date")

    def __str__(self):
        return f"Timetable {self.class_group} ({self.start_date} - {self.end_date})"


class Attendance(models.Model):
    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Excused", "Excused"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timetable = models.ForeignKey(
        Timetable, on_delete=models.RESTRICT, related_name="attendances"
    )
    student = models.ForeignKey(Student, on_delete=models.RESTRICT)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attendances"
        unique_together = ("timetable", "student")

    def __str__(self):
        return f"{self.student} - {self.status}"


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

    def __str__(self):
        return f"Report {self.timetable} - {self.completion_rate}%"
