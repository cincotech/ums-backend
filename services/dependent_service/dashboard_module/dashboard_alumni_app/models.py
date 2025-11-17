import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student


class AlumniProfile(models.Model):
    SECTOR_CHOICES = (
        ("tech", "Technologie"),
        ("finance", "Finance"),
        ("health", "Santé"),
        ("education", "Éducation"),
        ("consulting", "Conseil"),
        ("other", "Autre"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    current_position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    city = models.CharField(max_length=100)
    linkedin_profile = models.URLField(null=True, blank=True)
    is_mentor = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_profiles"


class JobOffer(models.Model):
    JOB_TYPES = (
        ("internship", "Stage"),
        ("full_time", "CDI"),
        ("part_time", "CDD"),
        ("freelance", "Freelance"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_job_offers"


class MentorshipProgram(models.Model):
    STATUS_CHOICES = (
        ("active", "Actif"),
        ("completed", "Terminé"),
        ("paused", "En Pause"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Student, on_delete=models.CASCADE)
    expertise_area = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mentorship_programs"


class AlumniTestimonial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_testimonials"


class AlumniEvent(models.Model):
    EVENT_TYPES = (
        ("conference", "Conférence"),
        ("workshop", "Atelier"),
        ("networking", "Réseautage"),
        ("graduation", "Remise de Diplômes"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    max_attendees = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_events"


class AlumniEventRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_event_registrations"
        unique_together = ["event", "alumni"]


class AlumniDonation(models.Model):
    DONATION_TYPES = (
        ("scholarship", "Bourse d'Études"),
        ("research", "Recherche"),
        ("equipment", "Équipement"),
        ("general", "Général"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES)
    purpose = models.TextField()
    transaction_id = models.CharField(max_length=100, unique=True)
    donated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_donations"
