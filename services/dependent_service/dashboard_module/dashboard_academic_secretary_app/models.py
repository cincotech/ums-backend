import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import ClassGroup
from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class JurySession(models.Model):
    """
    Représente une session officielle de jury académique.

    Une session de jury est organisée pour examiner les résultats
    académiques d'un groupe de classe à la fin d'une période
    d'évaluation (semestre ou année académique).

    Responsabilités :
        - Examiner les résultats compilés des étudiants.
        - Délibérer sur les cas particuliers.
        - Valider les décisions académiques finales.
        - Produire un procès-verbal officiel.

    Une session de jury est généralement associée à :
        - Une année académique.
        - Un groupe de classe.
        - Un ensemble de membres du jury.

    Cycle de vie :
        scheduled  -> session planifiée
        in_progress -> délibération en cours
        completed   -> délibération terminée

    Exemple :
        Jury L3 Informatique 2025-2026
        Date : 15/07/2026
        Membres : Doyen, Chef de département, Enseignants
    """
    STATUS_CHOICES = (
        ("scheduled", "Planifié"),
        ("in_progress", "En Cours"),
        ("completed", "Terminé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=255)
    session_date = models.DateTimeField()
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE, related_name="jury_sessions"
    )
    jury_members = models.ManyToManyField(
        User,
        through="JuryMember",
        related_name="jury_sessions",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    minutes_document = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jury_sessions"

    def __str__(self):
        return f"{self.session_name} - {self.class_group.class_fk.class_name} ({self.class_group.group_name}) - {self.session_date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.status in ["in_progress", "completed"]:
            if not self._state.adding:
                has_president = JuryMember.objects.filter(
                    jury_session=self,
                    role="president"
                ).exists()
                if not has_president:
                    raise ValidationError(
                        f"Cannot set status to '{self.get_status_display()}': session must have a president"
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def has_president(self, user):
        return JuryMember.objects.filter(
            jury_session=self, user=user, role="president"
        ).exists()

    def get_president(self):
        president_member = (
            JuryMember.objects.filter(jury_session=self, role="president")
            .select_related("user")
            .first()
        )
        return president_member.user if president_member else None


class JuryMember(models.Model):
    """
    Représente un membre du jury académique.

    Un membre du jury est un enseignant ou un responsable académique
    qui participe aux délibérations d'une session de jury.

    Rôles possibles :
        - Président : dirige les délibérations et prend la parole principale.
        - Membre : participe aux discussions et votes.
        - Secrétaire : rédige le procès-verbal et assure la traçabilité.

    Un membre de jury peut être associé à plusieurs sessions de jury
    au cours de sa carrière académique.

    Exemple :
        Prof. Martin - Président
        Dr. Dupont - Membre
        Mme. Durand - Secrétaire
    """
    ROLE_CHOICES = (
        ("president", "Président"),
        ("member", "Membre"),
        ("secretary", "Secrétaire"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jury_session = models.ForeignKey(
        JurySession,
        on_delete=models.CASCADE,
        related_name="jury_member_records",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jury_memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        db_table = "jury_members"
        unique_together = ("jury_session", "user")

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.role == "president":
            existing_president = JuryMember.objects.filter(
                jury_session=self.jury_session,
                role="president"
            ).exclude(pk=self.pk).exists()
            if existing_president:
                raise ValidationError("Only one president allowed per jury session")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.get_role_display()}"
class JuryDecision(models.Model):
    """
    Représente la décision académique finale prise par le jury
    pour un étudiant donné.

    Cette décision constitue la source officielle permettant
    de déterminer la progression académique de l'étudiant.

    Sources utilisées lors de la délibération :
        - Résultats compilés.
        - Notes de suppléments.
        - Situations particulières.
        - Décisions administratives.

    Décisions possibles :
        admitted :
            L'étudiant est admis et passe au niveau supérieur.

        repeat :
            L'étudiant redouble son année.

        deferred :
            La décision est reportée dans l'attente
            d'informations complémentaires.

        excluded :
            L'étudiant est exclu selon les règlements
            académiques en vigueur.

    Cette entité doit être considérée comme la référence
    officielle pour les opérations de promotion et de
    réinscription annuelle.
    """
    DECISION_TYPES = (
        ("AAC", "Avance avec complément"),
        ("AAA", "Assimilé aux ajournés"),
        ("R1S", "Réussite 1ère session"),
        ("R2S", "Réussite 2ème session"),
        ("ND", "Non décision"),
        ("EXC", "Exclusion"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jury_session = models.ForeignKey(JurySession, on_delete=models.CASCADE, related_name="jury_decisions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    decision = models.CharField(max_length=20, choices=DECISION_TYPES, default="ND")
    notes = models.TextField(null=True, blank=True)
    # allow temporary decisions without a validator; will be set when decision is validated
    validated_by = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    validated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jury_decisions"


class GradeComplaint(models.Model):
    """
    Représente une demande officielle de révision de note
    introduite par un étudiant.

    Un étudiant peut contester une note lorsqu'il estime
    qu'une erreur de calcul, de transcription ou d'évaluation
    a été commise.

    Processus métier :

        submitted
            La réclamation vient d'être introduite.

        assigned
            Un responsable a été désigné pour traiter
            la demande.

        in_review
            La réclamation est en cours d'analyse.

        resolved
            Une décision a été prise et la note a été
            confirmée ou modifiée.

        rejected
            La demande est refusée.

    Historique conservé :
        - Note initiale.
        - Motif de réclamation.
        - Nouvelle note éventuelle.
        - Décision finale.
        - Commentaires de traitement.

    Exemple :
        Étudiant :
            Jean Dupont

        Cours :
            Analyse Mathématique

        Note initiale :
            8/20

        Motif :
            Erreur de totalisation des points.
    """
    STATUS_CHOICES = (
        ("submitted", "Soumise"),
        ("assigned", "Attribuée"),
        ("in_review", "En Révision"),
        ("resolved", "Résolue"),
        ("rejected", "Rejetée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    original_grade = models.FloatField()
    complaint_reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    new_grade = models.FloatField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "grade_complaints"


class OfficialDocument(models.Model):
    """
    Représente un document administratif officiel produit
    par l'institution académique.

    Ce module centralise la génération, la validation,
    la signature et l'archivage des documents officiels.

    Types de documents pris en charge :

        transcript
            Relevé officiel des notes.

        certificate
            Certificat académique ou administratif.

        minutes
            Procès-verbal d'une réunion ou d'un jury.

        circular
            Circulaire administrative.

        service_note
            Note de service interne.

    Cycle documentaire :

        draft
            Document en préparation.

        pending_signature
            Document prêt à être signé.

        signed
            Document validé officiellement.

        archived
            Document clôturé et archivé.

    Traçabilité :
        - Auteur du document.
        - Signataire officiel.
        - Dates de création et signature.

    Objectif :
        Garantir l'authenticité et la conservation
        des documents institutionnels.
    """
    DOCUMENT_TYPES = (
        ("transcript", "Relevé de Notes"),
        ("certificate", "Certificat"),
        ("minutes", "Procès-Verbal"),
        ("circular", "Circulaire"),
        ("service_note", "Note de Service"),
    )

    STATUS_CHOICES = (
        ("draft", "Brouillon"),
        ("pending_signature", "En Attente de Signature"),
        ("signed", "Signé"),
        ("archived", "Archivé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_documents"
    )
    signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "official_documents"


class TeacherPaymentClaim(models.Model):
    """
    Représente une demande de paiement des prestations
    pédagogiques réalisées par un enseignant.

    Cette demande permet de calculer et de valider les
    rémunérations dues sur base des heures effectivement
    dispensées.

    Informations financières :
        - Enseignant concerné.
        - Cours enseigné.
        - Nombre d'heures prestées.
        - Taux horaire.
        - Montant total à payer.

    Workflow de validation :

        submitted
            Demande introduite.

        verified
            Contrôle administratif effectué.

        approved
            Validation hiérarchique accordée.

        signed
            Signature officielle obtenue.

        sent_to_finance
            Transmise au service financier.

        rejected
            Demande refusée.

    Objectifs :
        - Assurer la traçabilité des prestations.
        - Garantir le contrôle administratif.
        - Faciliter le traitement financier.
        - Constituer un historique des paiements.

    Exemple :

        Enseignant :
            Prof. Martin

        Cours :
            Programmation Python

        Heures :
            45

        Tarif :
            25 USD/heure

        Montant :
            1125 USD
    """
    STATUS_CHOICES = (
        ("submitted", "Soumise"),
        ("verified", "Vérifiée"),
        ("approved", "Approuvée"),
        ("signed", "Signée"),
        ("sent_to_finance", "Envoyée aux Finances"),
        ("rejected", "Rejetée"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    hours_taught = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="submitted"
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_claims",
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_claims",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "teacher_payment_claims"
