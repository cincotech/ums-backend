import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import ClassGroup
from services.core_service.academic_module.teacher_app.models import Attribution
from services.core_service.student_module.student_profile_app.models import Student
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User

# ── Legacy models (kept for compatibility) ────────────────────────────────────


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
        return f"{self.schedule_name} ({self.day_of_week} {self.start_time}-{self.end_time})"


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
    shared_with = models.ManyToManyField(
        ClassGroup,
        related_name="shared_timetables",
        blank=True,
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


class TimetableMerge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    timetables = models.ManyToManyField(Timetable, related_name="timetable_merges")

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_timetable_merges",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


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


# ── New professional timetable models ─────────────────────────────────────────


class TimetableTemplate(models.Model):
    """
    Grille horaire récurrente d'un groupe de classe.
    Représente le planning théorique (pattern hebdomadaire) avant la génération des séances.
    """

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_PUBLISHED, "Publié"),
        (STATUS_ARCHIVED, "Archivé"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="timetable_templates",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="created_timetable_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "timetable_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.class_group})"


class TemplateEntry(models.Model):
    """
    Créneau récurrent dans une grille horaire.
    Ex: « Chaque lundi 8h–10h, CM Algorithmique, Prof. Dupont, Salle 101 »
    """

    DAY_CHOICES = [
        ("Monday", "Lundi"),
        ("Tuesday", "Mardi"),
        ("Wednesday", "Mercredi"),
        ("Thursday", "Jeudi"),
        ("Friday", "Vendredi"),
        ("Saturday", "Samedi"),
        ("Sunday", "Dimanche"),
    ]
    SESSION_TYPE_CHOICES = [
        ("CM", "Cours magistral"),
        ("TD", "Travaux dirigés"),
        ("TP", "Travaux pratiques"),
        ("Seminar", "Séminaire"),
        ("Other", "Autre"),
    ]
    WEEK_TYPE_CHOICES = [
        ("all", "Toutes les semaines"),
        ("A", "Semaine A"),
        ("B", "Semaine B"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        TimetableTemplate,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    day_of_week = models.CharField(max_length=9, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    attribution = models.ForeignKey(
        Attribution,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    session_type = models.CharField(
        max_length=10, choices=SESSION_TYPE_CHOICES, default="CM"
    )
    week_type = models.CharField(max_length=3, choices=WEEK_TYPE_CHOICES, default="all")
    title = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "template_entries"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.template.name} — {self.day_of_week} {self.start_time}"


class CourseSession(models.Model):
    """
    Séance réelle (instance datée).
    Peut être générée depuis un TemplateEntry ou créée manuellement (rattrapage, etc.).
    """

    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_POSTPONED = "postponed"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Planifiée"),
        (STATUS_COMPLETED, "Dispensée"),
        (STATUS_CANCELLED, "Annulée"),
        (STATUS_POSTPONED, "Reportée"),
    ]
    SESSION_TYPE_CHOICES = [
        ("CM", "Cours magistral"),
        ("TD", "Travaux dirigés"),
        ("TP", "Travaux pratiques"),
        ("Seminar", "Séminaire"),
        ("Other", "Autre"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        TimetableTemplate,
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True,
    )
    template_entry = models.ForeignKey(
        TemplateEntry,
        on_delete=models.SET_NULL,
        related_name="sessions",
        null=True,
        blank=True,
    )
    class_group = models.ForeignKey(
        ClassGroup,
        on_delete=models.CASCADE,
        related_name="course_sessions",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    attribution = models.ForeignKey(
        Attribution,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    session_type = models.CharField(
        max_length=10, choices=SESSION_TYPE_CHOICES, default="CM"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_SCHEDULED
    )
    is_makeup = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="created_course_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_sessions"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.class_group} — {self.date} {self.start_time}"
