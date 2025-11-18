import uuid

from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class Schedule(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="schedules"
    )
    academic_year = models.CharField(max_length=9)
    semester = models.IntegerField(choices=((1, "Semester 1"), (2, "Semester 2")))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_date = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "doyen_schedules"
        unique_together = ("faculty", "academic_year", "semester")


class TeachingProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribution = models.OneToOneField(Attribution, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    progress_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(User, on_delete=models.RESTRICT)

    class Meta:
        db_table = "teaching_progress"


class TeacherWorkload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)
    total_hours = models.IntegerField(default=0)
    assigned_hours = models.IntegerField(default=0)
    is_permanent = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_workload"
        unique_together = ("faculty", "teacher", "academic_year")


class StudentGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=9)
    students = models.ManyToManyField(Student, related_name="doyen_groups")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_groups"
        unique_together = ("faculty", "group_name", "academic_year")


class AcademicProgram(models.Model):
    LEVEL_CHOICES = (
        ("license", "License"),
        ("master", "Master"),
        ("doctorate", "Doctorate"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="programs"
    )
    program_name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_programs"


class TeachingUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        AcademicProgram, on_delete=models.CASCADE, related_name="units"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    credits = models.IntegerField()
    semester = models.IntegerField(choices=((1, "Semester 1"), (2, "Semester 2")))

    class Meta:
        db_table = "teaching_units"
        unique_together = ("program", "course")


class RoomAllocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    allocated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "room_allocations"


class SecretaryNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_date = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        db_table = "secretary_notes"
