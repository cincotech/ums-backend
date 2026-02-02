import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from services.core_service.academic_module.class_app.models import Class, ClassGroup
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student


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

    class Meta:
        db_table = "inscriptions"
        unique_together = ("student", "academic_year", "class_fk")
        indexes = [models.Index(fields=["student", "academic_year", "class_fk"])]

    def __str__(self):
        return f"{self.student} - {self.class_fk} ({self.regist_status})"

    # ----------------- STATUS HANDLER FUNCTIONS -----------------
    def activate(self):
        if self.regist_status in ["Pending", "Suspended"]:
            self.regist_status = "Active"
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
        - Generates a new matricule if needed to match target class/faculty
        - Creates new inscription without bypassing clean/save validations
        """
        if self.regist_status not in ["Active", "Pending"]:
            raise ValidationError(
                "Only Active or Pending inscriptions can be replaced."
            )

        with transaction.atomic():
            # Mark current inscription as replaced
            self.regist_status = "Replaced"
            self.save()

            # Determine target type code from the new class
            try:
                target_type_code = new_class.department.faculty.types.code
            except AttributeError:
                target_type_code = "X"

            # Regenerate matricule **only if it does not match target type**
            current_matricule_type = (
                self.student.matricule[0] if self.student.matricule else "X"
            )
            if current_matricule_type != target_type_code:
                year = self.academic_year.civil_year
                existing_count = Student.objects.filter(
                    matricule__startswith=f"{target_type_code}{year}"
                ).count()
                new_matricule = (
                    f"{target_type_code}{year}/{str(existing_count + 1).zfill(5)}"
                )
                self.student.matricule = new_matricule
                self.student.save()  # Must save **before** creating new inscription

            # Now create new inscription, clean/save will pass
            new_inscription = Inscription.objects.create(
                student=self.student,
                academic_year=self.academic_year,
                class_fk=new_class,
                regist_status="Active",
            )

            return new_inscription

    # ----------------- HELPER FUNCTIONS -----------------
    def is_active(self):
        return self.regist_status == "Active"

    def is_completed(self):
        return self.regist_status == "Completed"

    @property
    def can_change_class(self):
        """Determine if the student can move to another class in the same faculty"""
        return self.regist_status in ["Completed", "Complement"]

    def generate_matricule(self):
        """
        Generates and assigns a matricule to the student based on:
        type formation code + academic year + sequential number
        Example: F2025/00001
        """
        if self.student.matricule:
            return self.student.matricule

        try:
            # Get type formation code from class -> department -> faculty -> type formation
            type_code = self.class_fk.department.faculty.types.code
        except AttributeError:
            type_code = "X"

        year = (
            self.academic_year.civil_year
        )  # use academic year instead of current year
        existing_count = Student.objects.filter(
            matricule__startswith=f"{type_code}{year}"
        ).count()
        sequential_number = existing_count + 1

        matricule = f"{type_code}{year}/{str(sequential_number).zfill(5)}"
        self.student.matricule = matricule
        self.student.save()
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

    def clean(self):
        """
        Business rules:
        1. Prevent faculty change via update (must use replace).
        2. Ensure student matricule type matches class faculty type.
        3. Ensure student has only one active/pending inscription per academic year.
        """
        if not self.student or not self.class_fk:
            return

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
        matricule = self.student.matricule

        # Ignore temporary/default matricules starting with 'X'
        if matricule and not matricule.startswith("X"):
            student_type_code = matricule[0]

            try:
                class_type_code = self.class_fk.department.faculty.types.code
            except AttributeError:
                raise ValidationError(
                    "Faculty type configuration is missing. Please contact the administrator."
                )

            if student_type_code != class_type_code:
                raise ValidationError(
                    f"Student's matricule starts with '{student_type_code}', "
                    f"which does not match the class faculty type '{class_type_code}'. "
                    "Use the 'replace' process to move the student to a different faculty."
                )

        # ---------------------------------------------------------
        # 3️⃣ SINGLE ACTIVE/PENDING INSCRIPTION PER ACADEMIC YEAR
        # ---------------------------------------------------------
        if not self.academic_year:
            return

        qs = Inscription.objects.filter(
            student=self.student,
            academic_year=self.academic_year,
            regist_status__in=["Active", "Pending"],
        )

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                "This student already has an active inscription in the selected academic year. "
                "You cannot create another one unless you use the 'replace' process."
            )

    def save(self, *args, **kwargs):
        # Validate first
        self.clean()
        if self._state.adding and self.class_group is None:
            self.class_group = self.get_or_create_default_group()

        # Generate new matricule if it starts with X
        try:
            type_code = self.class_fk.department.faculty.types.code
        except AttributeError:
            type_code = "X"

        year = self.academic_year.civil_year

        if not self.student.matricule or self.student.matricule.startswith("X"):
            existing_count = Student.objects.filter(
                matricule__startswith=f"{type_code}{year}"
            ).count()
            self.student.matricule = (
                f"{type_code}{year}/{str(existing_count + 1).zfill(5)}"
            )
            self.student.save()

        super().save(*args, **kwargs)
