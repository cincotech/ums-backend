import uuid

from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.student_module.inscription_app.models import Inscription


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

    Contraintes :
        - Un étudiant ne peut avoir qu'une seule note
          par cours et par session.

    Exemple :
        Étudiant : Jean
        Cours : Mathématiques
        Session : Normale
        Note : 14.5
    """

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

    mark = models.FloatField(help_text="Note obtenue par l'étudiant pour ce cours.")

    class Meta:
        db_table = "results"

        # Empêche la duplication d'une note
        # pour le même cours, la même inscription
        # et la même session.
        unique_together = ("course", "inscription", "session")

    def __str__(self):
        return f"{self.inscription.student} - " f"{self.course.name} - " f"{self.mark}"


class CompiledResult(models.Model):
    """
    Résultat académique global calculé pour une inscription.

    Cette table représente la décision académique calculée
    à partir de l'ensemble des notes de l'étudiant pour
    l'année académique concernée.

    Sources possibles :
        - Résultats des cours
        - Résultats des suppléments
        - Règles pédagogiques

    Elle sert notamment à déterminer :
        - La promotion
        - Le redoublement
        - L'échec
        - L'incomplétude du dossier
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
        help_text=(
            "Détails compilés des résultats par cours " "ou par unité d'enseignement."
        ),
    )

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.RESTRICT,
        related_name="compiled_results",
        help_text="Inscription concernée par cette compilation.",
    )

    average_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Moyenne générale calculée.",
    )

    status = models.CharField(
        max_length=60,
        choices=STATUS,
        help_text=(
            "Statut académique final : " "passed, failed, repeat ou incomplete."
        ),
    )

    is_promoted = models.BooleanField(
        default=False,
        help_text=(
            "Indique si l'étudiant est autorisé " "à passer au niveau supérieur."
        ),
    )

    class Meta:
        db_table = "compiled_results"

    def __str__(self):
        return f"{self.inscription} - " f"{self.status} " f"({self.average_mark})"


class Supplement(models.Model):
    """
    Représente une épreuve de supplément (rattrapage)
    accordée à un étudiant pour un cours donné.

    Un supplément permet à l'étudiant de repasser
    un cours insuffisamment validé afin de satisfaire
    les conditions académiques de réussite.

    Exemple :
        Mathématiques : 8/20
        Supplément : 12/20
        Validation : True
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

    validation = models.BooleanField(
        default=False,
        help_text=(
            "Indique si le supplément a été validé " "par l'administration ou le jury."
        ),
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
        return f"{self.inscription.student} - " f"{self.course.name} " f"(Supplement)"
