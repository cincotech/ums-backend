import uuid
import logging

from django.core.exceptions import ValidationError
from django.db import models
from typing import TYPE_CHECKING

from .mixins.inscription_status import InscriptionStatusMixin
from .services.matricule_service import MatriculeService
from .services.inscription_automation import InscriptionAutomation
from .validators.inscription_validator import InscriptionValidator

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student, StudentMatricule

if TYPE_CHECKING:
    pass  # No need for TYPE_CHECKING imports since we're importing everything above

# Create your models here.
logger = logging.getLogger(__name__)


class Inscription(InscriptionStatusMixin, models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),  # In progress
        ("Completed", "Completed"),  # Finished all
        ("Withdrawn", "Withdrawn"),  # Left
        ("Dropped", "Dropped"),  # Left mid-term
        ("Pending", "Pending"),  # Waiting for confirmation
        ("Suspended", "Suspended"),  # Temporarily stopped
        ("Canceled", "Canceled"),  # Canceled
        ("Replaced", "Replaced"),  # Moved to another class
        ("Complement", "Complement"),  # Needs to complete some part
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    class_fk = models.ForeignKey(
        Class,
        on_delete=models.RESTRICT,
        related_name="inscriptions",
        null=True,
        blank=True,
    )
    class_group = models.ForeignKey(
        ClassGroup, on_delete=models.RESTRICT, null=True, blank=True
    )
    date_inscription = models.DateField()
    regist_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="Pending"
    )
    withdrawal_date = models.DateField(null=True, blank=True)
    is_year_close = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'user_app.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscription_created'
    )
    modified_by = models.ForeignKey(
        'user_app.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscription_modified'
    )
    modified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inscriptions"
        # Permettre plusieurs inscriptions pour le même étudiant dans la même année
        # mais dans des classes différentes du même niveau/département
        unique_together = ("student", "academic_year", "class_fk")
        indexes = [models.Index(fields=["student", "academic_year", "class_fk"])]

    def __str__(self):
        return f"{self.student} - {self.class_fk} ({self.regist_status})"

    # ----------------- STATUS HANDLER FUNCTIONS -----------------
    def has_verified_payment(self):
        """Check if THIS SPECIFIC inscription has verified payment for inscription fees.
        Updated for multi-inscription support: checks only payments for this specific inscription.
        """
        from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import Payment

        # Check payments specifically for THIS inscription only
        # Utiliser 'inscription' au lieu de 'inscription_id' car c'est une ForeignKey
        return Payment.objects.filter(
            inscription=self,  # ← Utiliser l'objet directement
            paymentplan__feessheet__wording__wording_name__icontains="inscription",
            payment_status="verified",
        ).exists()
    
    def has_any_verified_payment_in_year(self):
        """Check if student has ANY verified payment for inscription fees in this academic year.
        Useful for replace() scenarios where payment from previous inscription should be considered.
        """
        from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import Payment

        # All inscription IDs of this student in this academic year (including Replaced)
        inscription_ids = Inscription.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
        ).values_list("id", flat=True)

        return Payment.objects.filter(
            inscription_id__in=inscription_ids,
            paymentplan__feessheet__wording__wording_name__icontains="inscription",
            payment_status="verified",
        ).exists()

    # ----------------- HELPER FUNCTIONS -----------------
    def _get_se_mark(self):
        """
        Returns the student's highschool percentage (se_mark) as a float.
        Returns None if not available.
        """
        hs_info = self.student.hs_infos.first()
        if not hs_info or not hs_info.se_mark:
            return None
        try:
            return float(hs_info.se_mark)
        except (ValueError, TypeError):
            return None

    def _has_university_background(self):
        """Returns True when the student has a university parcours/background."""
        return self.student.graduate_infos.exists()

    def _validate_registration_eligibility(self, target_type):
        """
        Applies hierarchical admission rules:
        - F/I baseline entries always require valid highschool information.
        - Without university background, highschool se_mark drives eligibility.
        - With university background, advanced tracks (M/D) bypass highschool.
        """
        target_type_code = target_type.code
        baseline_type_codes = {"F", "I"}
        advanced_type_codes = {"M", "D"}
        has_university_background = self._has_university_background()

        if has_university_background and target_type_code in advanced_type_codes:
            return

        se_mark = self._get_se_mark()
        if se_mark is None:
            if has_university_background and target_type_code in baseline_type_codes:
                raise ValidationError(
                    "Impossible de s'inscrire en Institut ou Faculté avec un parcours universitaire "
                    "sans informations de lycée. Pour cette inscription de base, les informations du lycée "
                    "sont obligatoires."
                )
            raise ValidationError(
                "Impossible de s'inscrire : les informations de lycée (se_mark) sont manquantes. "
                "Veuillez d'abord compléter vos informations de lycée."
            )

        if target_type_code not in baseline_type_codes and not has_university_background:
            raise ValidationError(
                "Impossible de s'inscrire en Master ou Doctorat sans parcours universitaire. "
                "Les informations de lycée donnent seulement accès à l'Institut ou à la Faculté."
            )

        if se_mark < 50 and target_type_code != "I":
            raise ValidationError(
                f"Impossible de s'inscrire en {target_type.name} : votre pourcentage au lycée "
                f"est de {se_mark}%. Avec un score inférieur à 50%, l'inscription est limitée à l'Institut."
            )

        if se_mark >= 50 and target_type_code not in baseline_type_codes and not has_university_background:
            raise ValidationError(
                "Impossible de s'inscrire à ce programme avec seulement les informations de lycée. "
                "Un parcours universitaire est requis pour le Master ou le Doctorat."
            )

    def is_active(self):
        return self.regist_status == "Active"

    def is_completed(self):
        return self.regist_status == "Completed"

    @property
    def can_change_class(self):
        """Determine if the student can move to another class in the same faculty"""
        return self.regist_status in ["Completed", "Complement"]

    def get_matricule_for_type(self):
        """Returns the matricule of this student for the TypeFormation of this inscription."""
        try:
            type_formation = self.class_fk.department.faculty.types
        except AttributeError:
            return None
        sm = StudentMatricule.objects.filter(
            student=self.student, type_formation=type_formation
        ).first()
        return sm.matricule if sm else None

    def generate_matricule(self):
        """
        Generates and assigns a matricule per TypeFormation.
        Returns the existing one if already generated for this type.
        Format: {TypeCode}{civil_year}/{00001}
        Delegates to MatriculeService for implementation.
        """
        return MatriculeService.generate_for_inscription(self)

    def transfer_academic_year(self, target_academic_year, user=None):
        """
        Move this inscription to another academic year atomically.
        Delegates to MatriculeService for implementation.
        """
        return MatriculeService.transfer_academic_year(self, target_academic_year, user)

    def _transfer_matricule_year_if_needed(self, old_academic_year):
        """
        Keep the student's TypeFormation matricule coherent when an inscription
        was created in the wrong year and is corrected before another inscription
        uses that old-year matricule.
        Delegates to MatriculeService for implementation.
        """
        MatriculeService._transfer_matricule_year_if_needed(self, old_academic_year)
    def get_or_create_default_group(self):
        """
        Returns the default class group (G1) for this inscription's class and academic year.
        Creates it if it does not exist, and ensures it is marked as default.
        Delegates to MatriculeService for implementation.
        """
        return MatriculeService.get_or_create_default_group(self)

    # ----------------- CLEAN AND SAVE METHODS -----------------
    def clean(self):
        """
        Delegates validation to InscriptionValidator.
        """
        InscriptionValidator.validate(self)

    def save(self, *args, **kwargs):
        """
        Save method delegating to InscriptionAutomation service.
        """
        user = kwargs.pop('user', None)
        
        is_create = self._state.adding
        old_status = None
        if not is_create and self.pk:
            try:
                old = self.__class__.objects.filter(pk=self.pk).only('regist_status').first()
                old_status = old.regist_status if old else None
            except Exception:
                old_status = None
        
        # Pre-save preparation
        InscriptionAutomation.prepare(self, user)
        
        # Run validation
        self.clean()
        
        # Persist to database
        super().save(*args, **kwargs)

        # POST-SAVE automation hook
        try:
            InscriptionAutomation.after_save(self, created=is_create)
        except Exception as e:
            logger.exception("InscriptionAutomation.after_save failed: %s", e)

        # Ensure JuryDecision rows exist for this student when a new inscription
        # is created or when an inscription becomes active (validated).
        try:
            from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
                JurySession,
                JuryDecision,
            )

            should_populate = False
            if is_create:
                should_populate = True
            elif old_status != self.regist_status and self.regist_status == "Active":
                should_populate = True

            if should_populate and self.regist_status in ["Active", "Pending", "Complement"]:
                if self.class_fk_id:
                    jury_sessions = JurySession.objects.filter(
                        class_group__class_fk_id=self.class_fk_id
                    ).select_related("class_group")
                elif self.class_group_id:
                    jury_sessions = JurySession.objects.filter(
                        class_group_id=self.class_group_id
                    ).select_related("class_group")
                else:
                    jury_sessions = JurySession.objects.none()

                for js in jury_sessions:
                    try:
                        if js.class_group.academic_year_id != self.academic_year_id:
                            continue
                        JuryDecision.objects.get_or_create(
                            jury_session=js,
                            student_id=self.student_id,
                            defaults={"decision": "ND", "notes": "", "validated_by": None},
                        )
                    except Exception as e:
                        logger.exception(
                            "JuryDecision.get_or_create failed for "
                            "jury_session=%s student_id=%s: %s",
                            js.id, self.student_id, e,
                        )
        except Exception as e:
            logger.exception("JuryDecision populating block failed: %s", e)


class ComplementRequirement(models.Model):
    """
    Représente un besoin de complément pour un étudiant (ex: matières ou procédures
    complémentaires à réaliser suite à une décision de type AAC - Avance avec complément).

    Objectif:
        - Permettre au bureau des inscriptions et à la finance de suivre les compléments
        - Lier un complément à une inscription si pertinent
    """

    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("validated", "Validé"),
        ("paid", "Payé"),
        ("cancelled", "Annulé"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="complement_requirements")
    inscription = models.ForeignKey(
        "Inscription", on_delete=models.SET_NULL, null=True, blank=True, related_name="complement_requirements"
    )
    course = models.ForeignKey(
        "course_app.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complement_requirements",
    )
    requirements = models.TextField(null=True, blank=True)
    course_count = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_renewal = models.BooleanField(default=True)
    feesheet = models.ForeignKey(
        "dashboard_collection_agent_app.FeesSheet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complement_requirements",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    jury_decision = models.ForeignKey(
        "dashboard_academic_secretary_app.JuryDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="complement_requirements",
    )
    created_by = models.ForeignKey(
        'user_app.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='complement_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "complement_requirements"

    def __str__(self):
        return f"ComplementRequirement({self.student}, {self.status}, amount_due:{self.amount_due})"

    def save(self, *args, **kwargs):
        if self.feesheet and self.unit_price != self.feesheet.base_amount:
            self.unit_price = self.feesheet.base_amount

        self.amount_due = self.unit_price * self.course_count
        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        return self.amount_due