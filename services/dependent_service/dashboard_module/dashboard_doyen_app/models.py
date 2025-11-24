import uuid

from django.db import models

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.academic_module.university_app.models import AcademicYear
from services.dependent_service.scheduling_module.scheduling_app.models import Timetable
from services.foundational_service.auth_module.user_app.models import User


class TeachingProgress(models.Model):
    """
    Progress of a teacher for a specific course attribution.
    Automatically aggregated from related ActivityReports in Timetable.
    One entry per Attribution per academic year.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribution = models.OneToOneField(
        Attribution, on_delete=models.CASCADE, related_name="teaching_progress"
    )
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="teaching_progresses"
    )
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="submitted_progress"
    )

    class Meta:
        db_table = "teaching_progress"
        ordering = ["faculty", "attribution"]

    def __str__(self):
        return f"{self.attribution.course.course_name} - {self.progress_percentage}%"

    def update_progress_from_timetable(self):
        """
        Calculate progress based on related Timetable ActivityReports.
        """
        timetables = Timetable.objects.filter(attribution=self.attribution)
        total_planned = 0
        total_delivered = 0
        for timetable in timetables:
            reports = timetable.activity_reports.all()
            for report in reports:
                if report.planned_hours:
                    total_planned += report.planned_hours
                if report.delivered_hours:
                    total_delivered += report.delivered_hours

        if total_planned > 0:
            self.progress_percentage = round((total_delivered / total_planned) * 100, 2)
        else:
            self.progress_percentage = 0
        self.save()


class TeacherWorkload(models.Model):
    """
    Tracks teacher workload per academic year.
    Assigned hours are calculated from related Attributions and TeachingProgress.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="workloads"
    )
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="workloads"
    )
    academic_year = academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.RESTRICT, related_name="teaching_academic_year"
    )
    total_hours = models.IntegerField(default=0)  # Max hours teacher can teach
    assigned_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0
    )  # Hours actually delivered
    is_permanent = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_workload"
        unique_together = ("faculty", "teacher", "academic_year")

    def __str__(self):
        return f"{self.teacher.username} - {self.academic_year} - {self.assigned_hours}/{self.total_hours}h"

    def update_from_progress(self):
        """
        Update assigned_hours based on TeachingProgress for this academic year.
        """
        progress_entries = TeachingProgress.objects.filter(
            attribution__principal_teacher=self.teacher,
            academic_year=self.academic_year,
        )
        total_assigned = 0
        for progress in progress_entries:
            # Each TeachingProgress should calculate total delivered hours from related ActivityReports
            timetables = progress.attribution.timetables.all()
            for timetable in timetables:
                for report in timetable.activity_reports.all():
                    if report.delivered_hours:
                        total_assigned += report.delivered_hours

        self.assigned_hours = total_assigned
        self.save()


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
