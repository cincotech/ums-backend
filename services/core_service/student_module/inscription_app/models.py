import uuid

from django.db import models

from services.core_service.academic_module.class_app.models import Class
from services.core_service.academic_module.university_app.models import AcademicYear
from services.core_service.student_module.student_profile_app.models import Student


# Create your models here.
class Inscription(models.Model):
    GROUPE = [(chr(65 + i), chr(65 + i)) for i in range(26)]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    class_fk = models.ForeignKey(
        Class, on_delete=models.RESTRICT, related_name="inscriptions"
    )
    date_inscription = models.DateField()
    regist_status = models.CharField(max_length=4, default="ACT")
    groupe = models.CharField(max_length=1, choices=GROUPE, default="A")
    withdrawal_date = models.DateField(null=True, blank=True)
    is_year_close = models.BooleanField(default=False)

    class Meta:
        db_table = "inscriptions"
        unique_together = ("student", "academic_year", "class_fk")

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
