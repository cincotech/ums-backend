import uuid

from django.core.exceptions import ValidationError
from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.module_app.models import Module, Semester
from services.core_service.academic_module.public_app.models import Program
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
            attribution__principal_teacher__user=self.teacher,
            attribution__academic_year=self.academic_year,
        )
        total_assigned = 0
        for progress in progress_entries:
            timetables = Timetable.objects.filter(attribution=progress.attribution)
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


class CurriculumTemplate(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publié"
        ARCHIVED = "archived", "Archivé"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(
        Program, on_delete=models.RESTRICT, related_name="curriculum_templates"
    )
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="curriculum_templates"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="curriculum_templates",
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name="curriculum_templates"
    )
    title = models.CharField(max_length=255, blank=True)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    expected_credits = models.PositiveSmallIntegerField(default=30)
    expected_vhp_hours = models.PositiveIntegerField(null=True, blank=True)
    duplicated_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_curriculum_templates",
    )
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_curriculum_templates",
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_templates"
        ordering = [
            "-academic_year__start_date",
            "class_fk__level",
            "semester__number",
            "-version",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["class_fk", "academic_year", "semester", "version"],
                name="unique_curriculum_template_version",
            ),
            models.UniqueConstraint(
                fields=["class_fk", "academic_year", "semester"],
                condition=models.Q(status="published"),
                name="unique_published_curriculum_template",
            ),
        ]

    def __str__(self):
        return (
            f"{self.class_fk.class_name} - {self.semester} - "
            f"{self.academic_year} (v{self.version})"
        )

    def clean(self):
        super().clean()
        errors = {}

        if (
            self.program_id
            and self.class_fk_id
            and self.program.faculty_id != self.class_fk.department.faculty_id
        ):
            errors["program"] = (
                "Le programme et la classe doivent appartenir à la même faculté."
            )

        faculty = self.class_fk.department.faculty if self.class_fk_id else None
        if (
            faculty
            and faculty.university_id
            and self.academic_year_id
            and self.academic_year.university_id
            and faculty.university_id != self.academic_year.university_id
        ):
            errors["academic_year"] = (
                "L’année académique doit appartenir à l’université de la faculté."
            )

        if errors:
            raise ValidationError(errors)


class CurriculumTeachingUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        CurriculumTemplate,
        on_delete=models.CASCADE,
        related_name="teaching_units",
    )
    module = models.ForeignKey(
        Module, on_delete=models.PROTECT, related_name="curriculum_teaching_units"
    )
    position = models.PositiveSmallIntegerField()
    is_required = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "curriculum_teaching_units"
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["template", "module"],
                name="unique_module_per_curriculum_template",
            ),
            models.UniqueConstraint(
                fields=["template", "position"],
                name="unique_teaching_unit_position_per_template",
            ),
        ]

    def __str__(self):
        return f"{self.template} - {self.module}"

    def clean(self):
        super().clean()
        errors = {}

        if self.template_id and self.module_id:
            if self.module.class_fk_id != self.template.class_fk_id:
                errors["module"] = "L’UE doit appartenir à la classe de la maquette."
            if self.module.semester_id != self.template.semester_id:
                errors["module"] = "L’UE doit appartenir au semestre de la maquette."

        if errors:
            raise ValidationError(errors)


class CurriculumCourse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teaching_unit = models.ForeignKey(
        CurriculumTeachingUnit,
        on_delete=models.CASCADE,
        related_name="curriculum_courses",
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="curriculum_courses"
    )
    position = models.PositiveSmallIntegerField()
    coefficient = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    tpe_hours = models.PositiveSmallIntegerField(default=0)
    tge_hours = models.PositiveSmallIntegerField(default=0)
    is_mandatory = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "curriculum_courses"
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["teaching_unit", "course"],
                name="unique_course_per_curriculum_teaching_unit",
            ),
            models.UniqueConstraint(
                fields=["teaching_unit", "position"],
                name="unique_course_position_per_teaching_unit",
            ),
            models.CheckConstraint(
                condition=models.Q(coefficient__gt=0),
                name="curriculum_course_coefficient_positive",
            ),
        ]

    def __str__(self):
        return f"{self.teaching_unit} - {self.course.course_name}"

    @property
    def vhp_hours(self):
        return self.course.cm + self.course.td + self.course.tp

    @property
    def resolved_tge_hours(self):
        return self.tge_hours or self.vhp_hours + self.tpe_hours

    def clean(self):
        super().clean()
        errors = {}

        if self.teaching_unit_id and self.course_id:
            template = self.teaching_unit.template
            if self.course.module.class_fk_id != template.class_fk_id:
                errors["course"] = "L’ECUE doit appartenir à la classe de la maquette."
            elif self.course.module.semester_id != template.semester_id:
                errors["course"] = "L’ECUE doit appartenir au semestre de la maquette."

            duplicate = CurriculumCourse.objects.filter(
                teaching_unit__template=self.teaching_unit.template,
                course=self.course,
            )
            if self.pk:
                duplicate = duplicate.exclude(pk=self.pk)
            if duplicate.exists():
                errors["course"] = (
                    "Cet ECUE existe déjà dans cette maquette semestrielle."
                )

        if errors:
            raise ValidationError(errors)
