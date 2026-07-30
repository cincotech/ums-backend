import uuid

from django.conf import settings
from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.module_app.models import Semester
from services.core_service.student_module.inscription_app.models import Inscription
from services.foundational_service.auth_module.user_app.models import User


class Session(models.Model):
    """
    Représente une session d'évaluation académique.

    Exemples :
        - Session normale
        - Session de rattrapage
        - Session spéciale

    Une même inscription peut avoir des notes différentes
    pour un même cours selon la session concernée.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    session_name = models.CharField(
        max_length=20,
        help_text="Nom de la session (Normale, Rattrapage, Spéciale, etc.).",
    )

    class Meta:
        db_table = "sessions"

    def __str__(self):
        return self.session_name


class Result(models.Model):
    """
    Représente la note obtenue par un étudiant pour un cours
    donné dans une session donnée.
    """

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("validated", "Validated"),
        ("rejected", "Rejected"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="results",
        help_text="Cours concerné par cette note.",
    )

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="results_inscription",
        help_text="Inscription annuelle de l'étudiant concerné.",
    )

    session = models.ForeignKey(
        Session,
        on_delete=models.RESTRICT,
        related_name="results_session",
        help_text="Session d'évaluation associée à cette note.",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        related_name="results",
        null=True,
        blank=True,
        help_text="Semestre associé à cette note.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Statut du workflow de validation des notes.",
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="validated_results",
        null=True,
        blank=True,
        help_text="Utilisateur qui a validé ou rejeté la note.",
    )

    validated_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    mark = models.FloatField(help_text="Note obtenue par l'étudiant pour ce cours.")

    class Meta:
        db_table = "results"
        unique_together = ("course", "inscription", "session")

    def __str__(self):
        return f"{self.inscription.student} - {self.course.course_name} - {self.mark}"


class CompiledResult(models.Model):
    """
    Résultat académique global calculé pour une inscription.
    """

    STATUS = (
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("repeat", "Repeat"),
        ("incomplete", "Incomplete"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    results = models.JSONField(
        default=dict,
        help_text="Détails compilés des résultats par cours ou par unité d'enseignement.",
    )

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="compiled_results",
        help_text="Inscription concernée par cette compilation.",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        related_name="compiled_results",
        null=True,
        blank=True,
        help_text="Semestre associé à la compilation.",
    )

    average_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Moyenne générale calculée.",
    )

    status = models.CharField(
        max_length=60,
        choices=STATUS,
        help_text="Statut académique final : passed, failed, repeat ou incomplete.",
    )

    is_promoted = models.BooleanField(
        default=False,
        help_text="Indique si l'étudiant est autorisé à passer au niveau supérieur.",
    )

    class Meta:
        db_table = "compiled_results"

    def __str__(self):
        return f"{self.inscription} - {self.status} ({self.average_mark})"


class Supplement(models.Model):
    """
    Représente une épreuve de supplément (rattrapage) accordée à un étudiant.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="supplements_inscription",
        help_text="Inscription de l'étudiant concerné.",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.RESTRICT,
        related_name="supplements",
        help_text="Cours concerné par le supplément.",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        related_name="supplements",
        null=True,
        blank=True,
        help_text="Semestre associé au supplément.",
    )

    validation = models.BooleanField(
        default=False,
        help_text="Indique si le supplément a été validé par l'administration ou le jury.",
    )

    validation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date officielle de validation du supplément.",
    )

    mark = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Note obtenue lors du supplément.",
    )

    class Meta:
        db_table = "supplements"

    def __str__(self):
        return f"{self.inscription.student} - {self.course.course_name} (Supplement)"


class ResultComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Note concernée par le commentaire.",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="result_comments",
        help_text="Auteur du commentaire.",
    )
    comment = models.TextField(help_text="Contenu du commentaire.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "result_comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commentaire sur {self.result_id}"


class GradeChangeHistory(models.Model):
    """Trace each grade correction performed after the initial entry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name="grade_changes",
        help_text="Note modifiée.",
    )
    previous_mark = models.FloatField(help_text="Note avant modification.")
    new_mark = models.FloatField(help_text="Note après modification.")
    changed_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="grade_change_history",
        help_text="Utilisateur à l'origine de la modification.",
    )
    reason = models.TextField(blank=True, help_text="Motif de la modification.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade_change_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.result_id}: {self.previous_mark} → {self.new_mark}"
