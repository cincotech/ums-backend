import uuid

from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.student_module.inscription_app.models import Inscription


# Create your models here.
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=20)

    class Meta:
        db_table = "sessions"


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course, on_delete=models.RESTRICT, related_name="results"
    )
    inscription = models.ForeignKey(
        Inscription, on_delete=models.RESTRICT, related_name="results_inscription"
    )
    session = models.ForeignKey(
        Session, on_delete=models.RESTRICT, related_name="results_session"
    )
    mark = models.FloatField()

    class Meta:
        db_table = "results"
        unique_together = ("course", "inscription", "session")


class CompiledResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS = (
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("repeat", "Repeat"),
        ("incomplete", "Incomplete"),
    )
    results = models.JSONField(default=dict)
    inscription = models.ForeignKey(
        Inscription, on_delete=models.RESTRICT, related_name="compiled_results"
    )
    average_mark = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=60, choices=STATUS)
    is_promoted = models.BooleanField(default=False)

    class Meta:
        db_table = "compiled_results"


class Supplement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscription = models.ForeignKey(
        Inscription, on_delete=models.RESTRICT, related_name="supplements_inscription"
    )
    course = models.ForeignKey(
        Course, on_delete=models.RESTRICT, related_name="supplements"
    )
    validation = models.BooleanField(default=False)
    validation_date = models.DateField(null=True, blank=True)
    mark = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "supplements"
