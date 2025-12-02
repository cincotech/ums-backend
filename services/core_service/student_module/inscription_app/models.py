import uuid

from django.db import models
from django.utils import timezone

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student


# Create your models here.
class Inscription(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Completed", "Completed"),
        ("Withdrawn", "Withdrawn"),
        ("Dropped", "Dropped"),
        ("Pending", "Pending"),
        ("Suspended", "Suspended"),
        ("Canceled", "Canceled"),
        ("Replaced", "Replaced"),
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
    date_inscription = models.DateField()
    regist_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="Pending"
    )
    withdrawal_date = models.DateField(null=True, blank=True)
    is_year_close = models.BooleanField(default=False)

    class Meta:
        db_table = "inscriptions"
        unique_together = ("student", "academic_year", "class_fk")

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

    def replace(self, new_class):
        if self.regist_status in ["Active", "Pending"]:
            self.regist_status = "Replaced"
            self.save()
            return Inscription.objects.create(
                student=self.student,
                academic_year=self.academic_year,
                class_fk=new_class,
                regist_status="Active",
            )

    # ----------------- HELPER FUNCTIONS -----------------
    def is_active(self):
        return self.regist_status == "Active"

    def is_completed(self):
        return self.regist_status == "Completed"

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

    def save(self, *args, **kwargs):
        # Generate matricule if student doesn't have one
        if not self.student.matricule:
            self.generate_matricule()

        super().save(*args, **kwargs)
