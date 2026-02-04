import uuid

from django.db import models

from services.core_service.academic_module.faculty_app.models import Faculty


class Program(models.Model):
    """
    Programme académique exposé publiquement
    (Baccalauréat, Master, etc.)

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Faculté réelle (TIC, Sciences, HEC…)
    faculty = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, related_name="programs"
    )

    presentation = models.TextField()

    content = models.JSONField(default=list)
    admission_conditions = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)

    internship = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=50)

    career_opportunities = models.JSONField(default=list)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        # Le cycle vient de la faculté → TypeFormation
        return f"{self.faculty.faculty_abreviation} ({self.faculty.types.name})"

    class Meta:
        db_table = "programs"


def program_image_upload_path(instance, filename):
    """
    media/programs/{type_code}/{program_name}/{filename}
    """
    type_code = instance.program.faculty.types.code.lower()
    type_name = instance.program.faculty.types.name.replace(" ", "_").lower()
    return f"programs/{type_code}/{type_name}/{filename}"


class ProgramImage(models.Model):
    """
    Images associées à un programme académique
    """

    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to=program_image_upload_path)

    title = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    is_cover = models.BooleanField(
        default=False, help_text="Image principale du programme"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image - {self.program.faculty.types.name}"

    class Meta:
        db_table = "program_images"
