import uuid
import re

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student, StudentMatricule


# Create your models here.
class Inscription(models.Model):
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

    def activate(self, skip_payment_check=False):
        if self.regist_status in ["Pending", "Suspended"]:
            # Check payment before activation (skip if created by student_service)
            if not skip_payment_check and not self.has_verified_payment():
                raise ValidationError(
                    "Cannot activate inscription: Payment for inscription fees must be verified first."
                )

            self.regist_status = "Active"

            # Assign Student role if user doesn't have it
            user = self.student.user
            if not user.role or user.role.name != "student":
                from services.foundational_service.auth_module.user_app.models import (
                    Role,
                )

                student_role, _ = Role.objects.get_or_create(name="student")
                user.role = student_role
                user.save(update_fields=["role"])

            self.save()

    def complete(self):
        if self.regist_status == "Active":
            self.regist_status = "Completed"
            self.save()

    def withdraw(self):
        if self.regist_status in ["Active", "Pending"]:
            self.regist_status = "Withdrawn"
            self.withdrawal_date = timezone.now().date()
            self.save()

    def drop(self):
        if self.regist_status == "Active":
            self.regist_status = "Dropped"
            self.save()

    def suspend(self):
        if self.regist_status == "Active":
            self.regist_status = "Suspended"
            self.save()

    def cancel(self):
        if self.regist_status in ["Pending", "Active"]:
            self.regist_status = "Canceled"
            self.save()

    @property
    def is_complete(self):
        """Indicates the student has completed the inscription"""
        return self.regist_status in ["Completed"]

    @property
    def is_incomplete(self):
        """Indicates the student has not completed the inscription"""
        return self.regist_status in ["Active", "Pending", "Complement"]

    def replace(self, new_class):
        """
        Replace a student's class/faculty safely:
        - Marks current inscription as 'Replaced'
        - Creates new inscription -> save() handles StudentMatricule generation
        - Never overwrites existing matricules
        - Checks se_mark eligibility for the new TypeFormation
        """
        if self.regist_status not in ["Active", "Pending"]:
            raise ValidationError(
                "Only Active or Pending inscriptions can be replaced."
            )

        try:
            new_type = new_class.department.faculty.types
        except AttributeError:
            raise ValidationError(
                "Faculty type configuration is missing. Please contact the administrator."
            )

        self._validate_registration_eligibility(new_type)

        with transaction.atomic():
            Inscription.objects.filter(pk=self.pk).update(regist_status="Replaced")

            new_inscription = Inscription(
                student=self.student,
                academic_year=self.academic_year,
                class_fk=new_class,
                regist_status="Active",
                date_inscription=self.date_inscription,
            )
            new_inscription.save()
            
            # Transfer payment reference if needed
            # Note: In multi-inscription context, each inscription should have its own payment
            # The payment system should be updated to handle this properly

            return new_inscription

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
                    "Cannot enroll in Institut or Faculté with university background "
                    "without highschool information. For this baseline institution "
                    "entry, highschool information remains mandatory."
                )
            raise ValidationError(
                "Cannot enroll: highschool information (se_mark) is missing. "
                "Please complete your highschool information first."
            )

        if target_type_code not in baseline_type_codes and not has_university_background:
            raise ValidationError(
                "Cannot enroll in Master or Doctorate without university background. "
                "Highschool information only gives access to Institut or Faculté."
            )

        if se_mark < 50 and target_type_code != "I":
            raise ValidationError(
                f"Cannot enroll in {target_type.name}: your highschool percentage "
                f"is {se_mark}%. With a score below 50%, registration is restricted "
                "to Institut."
            )

        if se_mark >= 50 and target_type_code not in baseline_type_codes and not has_university_background:
            raise ValidationError(
                "Cannot enroll in this program with highschool information only. "
                "A university background is required for Master or Doctorate."
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
        """
        try:
            type_formation = self.class_fk.department.faculty.types
            type_code = type_formation.code
        except AttributeError:
            type_code = "X"
            return None

        # Return existing matricule for this type if already exists
        existing = StudentMatricule.objects.filter(
            student=self.student, type_formation=type_formation
        ).first()
        if existing:
            return existing.matricule

        year = self.academic_year.civil_year
        
        # Use transaction to prevent race conditions
        with transaction.atomic():
            matricule = self._get_available_matricule(
                type_code=type_code,
                civil_year=year,
            )

            StudentMatricule.objects.create(
                student=self.student,
                type_formation=type_formation,
                matricule=matricule,
                academic_year=self.academic_year,
            )

        return matricule

    def get_or_create_default_group(self):
        """
        Returns the default class group (G1) for this inscription's class and academic year.
        Creates it if it does not exist, and ensures it is marked as default.
        """
        if not self.class_fk or not self.academic_year:
            return None

        with transaction.atomic():
            group, created = ClassGroup.objects.get_or_create(
                class_fk=self.class_fk,
                academic_year=self.academic_year,
                group_name="G1",
                defaults={"is_default": True},
            )

            if not group.is_default:
                group.is_default = True
                group.save(update_fields=["is_default"])

            return group

    def transfer_academic_year(self, target_academic_year, user=None):
        """
        Move this inscription to another academic year atomically.

        This is intentionally different from a plain PATCH because the class group
        depends on the academic year. When the year changes, the inscription must
        be attached to the default group for the same class in the target year.
        """
        if self.academic_year_id == target_academic_year.id:
            return self

        with transaction.atomic():
            inscription = (
                Inscription.objects.select_for_update()
                .select_related(
                    "academic_year",
                    "class_fk__department__faculty__types",
                    "student",
                )
                .get(pk=self.pk)
            )
            old_academic_year = inscription.academic_year
            inscription.academic_year = target_academic_year
            inscription.class_group = inscription.get_or_create_default_group()

            if user:
                inscription.modified_by = user
                inscription.modified_at = timezone.now()

            inscription.clean()

            update_fields = ["academic_year", "class_group"]
            if user:
                update_fields.extend(["modified_by", "modified_at"])
            super(Inscription, inscription).save(update_fields=update_fields)

            inscription._transfer_matricule_year_if_needed(old_academic_year)

            return inscription

    def _transfer_matricule_year_if_needed(self, old_academic_year):
        """
        Keep the student's TypeFormation matricule coherent when an inscription
        was created in the wrong year and is corrected before another inscription
        uses that old-year matricule.
        """
        try:
            type_formation = self.class_fk.department.faculty.types
            type_code = type_formation.code
        except AttributeError:
            return

        matricule = StudentMatricule.objects.select_for_update().filter(
            student=self.student,
            type_formation=type_formation,
            academic_year=old_academic_year,
        ).first()
        if not matricule:
            return

        old_year_still_used = Inscription.objects.filter(
            student=self.student,
            academic_year=old_academic_year,
            class_fk__department__faculty__types=type_formation,
        ).exclude(pk=self.pk).exists()
        if old_year_still_used:
            return

        old_prefix = f"{type_code}{old_academic_year.civil_year}/"
        if matricule.matricule.startswith(old_prefix):
            preferred_number = self._extract_matricule_number(matricule.matricule)
            matricule.matricule = self._get_available_matricule(
                type_code=type_code,
                civil_year=self.academic_year.civil_year,
                preferred_number=preferred_number,
                exclude_matricule_id=matricule.pk,
            )

        matricule.academic_year = self.academic_year
        matricule.save(update_fields=["academic_year", "matricule"])

    def _extract_matricule_number(self, matricule):
        match = re.search(r"/(\d+)$", matricule or "")
        return int(match.group(1)) if match else None

    def _get_available_matricule(
        self,
        type_code,
        civil_year,
        preferred_number=None,
        exclude_matricule_id=None,
    ):
        prefix = f"{type_code}{civil_year}/"
        existing_qs = StudentMatricule.objects.select_for_update().filter(
            matricule__startswith=prefix
        )
        if exclude_matricule_id:
            existing_qs = existing_qs.exclude(pk=exclude_matricule_id)

        used_numbers = set()
        for existing in existing_qs.values_list("matricule", flat=True):
            number = self._extract_matricule_number(existing)
            if number is not None:
                used_numbers.add(number)

        if preferred_number and preferred_number not in used_numbers:
            return f"{prefix}{str(preferred_number).zfill(5)}"

        next_number = max(used_numbers, default=0) + 1
        while next_number in used_numbers:
            next_number += 1

        return f"{prefix}{str(next_number).zfill(5)}"

    def clean(self):
        """
        Business rules:
        1. Prevent faculty change via update (must use replace).
        2. Ensure student matricule type matches class faculty type.
        3. Ensure student has only one active/pending inscription per academic year.
        4. Ensure payment is verified before activation.
        """
        if not self.student or not self.class_fk:
            return

        # ---------------------------------------------------------
        # 0️⃣ CHECK PAYMENT BEFORE ACTIVATION (skip if created by student_service)
        # ---------------------------------------------------------
        if self.regist_status == "Active" and self.pk:
            previous = Inscription.objects.filter(pk=self.pk).first()
            if previous and previous.regist_status != "Active":
                # Skip payment check if created by student_service
                skip_payment = (self.created_by and
                               hasattr(self.created_by, 'role') and
                               self.created_by.role and
                               self.created_by.role.name == "student_service")
                if not skip_payment and not self.has_verified_payment():
                    raise ValidationError(
                        "Cannot activate inscription: Payment for inscription fees must be verified first."
                    )

        # ---------------------------------------------------------
        # 1️⃣ BLOCK FACULTY CHANGE VIA UPDATE
        # ---------------------------------------------------------
        if self.pk:
            previous = (
                Inscription.objects.filter(pk=self.pk)
                .select_related("class_fk__department__faculty")
                .first()
            )

            if previous:
                old_faculty = previous.class_fk.department.faculty
                new_faculty = self.class_fk.department.faculty

                if old_faculty != new_faculty:
                    raise ValidationError(
                        "Faculty change is not allowed via update. "
                        "If you want to move the student to another faculty, "
                        "please use the 'replace' process."
                    )

            if previous and previous.class_fk != self.class_fk:
                same_faculty = (
                    previous.class_fk.department.faculty
                    == self.class_fk.department.faculty
                )
                if same_faculty and not previous.can_change_class:
                    raise ValidationError(
                        f"Cannot move student to another class in the same faculty. "
                        f"Current inscription status: '{previous.regist_status}'."
                    )

        # ---------------------------------------------------------
        # 2️⃣ MATRICULE TYPE VS FACULTY TYPE CHECK
        # ---------------------------------------------------------
        try:
            class_type_formation = self.class_fk.department.faculty.types
        except AttributeError:
            raise ValidationError(
                "Faculty type configuration is missing. Please contact the administrator."
            )

        # Check via StudentMatricule table (multi-matricule support)
        existing_matricule = StudentMatricule.objects.filter(
            student=self.student
        ).exclude(type_formation=class_type_formation).first()

        if existing_matricule:
            # Student has a matricule for a different type — that's fine, multi-formation allowed
            # But if they already have one for THIS type, no conflict
            pass

        # Legacy check removed — Student.matricule field no longer exists.
        # Validation now relies solely on StudentMatricule entries.

        # ---------------------------------------------------------
        # 3️⃣ SINGLE ACTIVE/PENDING INSCRIPTION PER CLASS PER ACADEMIC YEAR
        # Updated: Allow multiple inscriptions in different classes of same level/department
        # ---------------------------------------------------------
        if not self.academic_year:
            return

        # Vérifier qu'il n'y a pas déjà une inscription pour cette classe spécifique
        qs = Inscription.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=self.class_fk,  # Même classe exacte
            regist_status__in=["Active", "Pending"],
        )

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                "This student already has an active or pending inscription "
                "for this specific class in the selected academic year."
            )

        # ---------------------------------------------------------
        # 4️⃣ NO HIGHER LEVEL INSCRIPTION IN THE SAME ACADEMIC YEAR
        # Same TypeFormation, same level or higher → blocked
        # Exception: different department within the same faculty is allowed
        # (common years where students split into departments)
        # ---------------------------------------------------------
        target_type = self.class_fk.department.faculty.types
        target_level = self.class_fk.level
        target_department = self.class_fk.department
        target_class = self.class_fk
        # 🔒 1. Bloquer doublon exact (même classe)
        same_class = Inscription.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            class_fk=target_class,
            regist_status__in=["Active", "Pending", "Completed"],
        )

        # 🔁 Exclure soi-même en update
        if self.pk:
            same_class = same_class.exclude(pk=self.pk)

        if same_class.exists():
            raise ValidationError(
                "L'étudiant est déjà inscrit dans cette classe pour cette année académique."
            )

        same_year_higher = Inscription.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            class_fk__level__gte=target_level,
            class_fk__department=target_department,  # 🎯 clé ici
            regist_status__in=["Active", "Pending", "Completed"],
        )

        # Exclure l'objet courant en cas de mise à jour
        if self.pk:
            same_year_higher = same_year_higher.exclude(pk=self.pk)

        if same_year_higher.exists():
            raise ValidationError(
                f"The student already has an inscription at level {target_level} or higher "
                f"in this department for this academic year."
            )

        # ---------------------------------------------------------
        # 5️⃣ NO LEVEL SKIP — must have completed previous level
        # ---------------------------------------------------------
        if target_level > 1:
            # Exception: student comes from another university
            # graduate_infos must match the same TypeFormation as the target class
            has_university_background = self.student.graduate_infos.filter(
                department__faculty__types=target_type
            ).exists()

            if not has_university_background:
                previous_level_done = Inscription.objects.filter(
                    student=self.student,
                    class_fk__level=target_level - 1,
                    class_fk__department__faculty__types=target_type,
                    regist_status__in=["Active", "Completed", "Complement"],
                ).exists()

                if not previous_level_done:
                    raise ValidationError(
                        f"The student has no inscription at level {target_level - 1} "
                        f"in the same formation type. "
                        f"Cannot enroll at level {target_level} without completing the previous level. "
                        f"If the student comes from another university, "
                        f"please fill in the university background information first."
                    )

        # ---------------------------------------------------------
        # 6 - REGISTRATION ELIGIBILITY
        # Highschool drives F/I baseline admission. University parcours can
        # override highschool only for advanced tracks such as Master/Doctorate.
        # ---------------------------------------------------------
        self._validate_registration_eligibility(target_type)

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        
        # Set created_by and modified_by before clean() to allow payment check skip
        if user:
            if self._state.adding:
                self.created_by = user
            self.modified_by = user
            self.modified_at = timezone.now()
        
        self.clean()
        
        if self._state.adding and self.class_group is None:
            self.class_group = self.get_or_create_default_group()
        
        # Auto-activate if created by student_service (no payment check)
        if (self._state.adding and user and
            hasattr(user, 'role') and user.role and
            user.role.name == "student_service" and
            self.regist_status == "Pending"):
            self.regist_status = "Active"
            print(f"DEBUG: Auto-activated inscription for user {user.email} with role {user.role.name}")
        # Also activate on update if still pending and user is student_service
        if (not self._state.adding and user and
            hasattr(user, 'role') and user.role and
            user.role.name == "student_service" and
            self.regist_status == "Pending"):
            self.regist_status = "Active"
            print(f"DEBUG: Auto-activated (update) inscription for user {user.email} with role {user.role.name}")

        # Generate matricule for this TypeFormation if not yet created
        try:
            type_formation = self.class_fk.department.faculty.types
            type_code = type_formation.code
        except AttributeError:
            type_code = "X"

        if type_code != "X":
            year = self.academic_year.civil_year
            has_matricule = StudentMatricule.objects.filter(
                student=self.student, type_formation=type_formation
            ).exists()
            if not has_matricule:
                # Use transaction to prevent race conditions in matricule generation
                with transaction.atomic():
                    new_matricule = self._get_available_matricule(
                        type_code=type_code,
                        civil_year=year,
                    )
                    StudentMatricule.objects.create(
                        student=self.student,
                        type_formation=type_formation,
                        matricule=new_matricule,
                        academic_year=self.academic_year,
                    )

        super().save(*args, **kwargs)
