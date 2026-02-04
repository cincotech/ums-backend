from django.db import models
from services.core_service.academic_module.faculty_app.models import Faculty
import uuid


class Program(models.Model):
    """
    Programme académique exposé publiquement
    (Baccalauréat, Master, etc.)

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Faculté réelle (TIC, Sciences, HEC…)
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="programs"
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
