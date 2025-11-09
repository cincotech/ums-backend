import uuid

from django.db import models

from services.core_service.academic_module.faculty_app.models import Faculty
from services.core_service.academic_module.university_app.models import University
from services.dependent_service.infrastructure_module.room_app.models import Room
from services.foundational_service.auth_module.user_app.models import User


class BaseProfile(models.Model):
    position = models.CharField(max_length=100, null=True)
    room = models.ForeignKey(
        Room, on_delete=models.RESTRICT, null=True, related_name="room_profiles"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True)

    class Meta:
        abstract = True


class Dean(BaseProfile):
    faculty = models.ForeignKey(
        Faculty, on_delete=models.RESTRICT, null=True, related_name="dean_profile"
    )

    class Meta:
        abstract = True


class Rector(BaseProfile):
    university = models.ForeignKey(
        University, on_delete=models.RESTRICT, null=True, related_name="rector_profile"
    )

    class Meta:
        abstract = True


class StudentService(BaseProfile):
    class Meta:
        abstract = True


class FinanceService(BaseProfile):
    class Meta:
        abstract = True


class GeneralService(BaseProfile):
    class Meta:
        abstract = True


class RectorOffice(BaseProfile):
    class Meta:
        abstract = True


class QualityInsurance(BaseProfile):
    class Meta:
        abstract = True


class AcademicAffairs(BaseProfile):
    class Meta:
        abstract = True


class Profile(
    Dean,
    Rector,
    StudentService,
    FinanceService,
    GeneralService,
    RectorOffice,
    QualityInsurance,
    AcademicAffairs,
):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.RESTRICT, related_name="profiles"
    )

    class Meta:
        db_table = "profiles"


class Supervisor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.RESTRICT, related_name="supervisor"
    )
    is_supervisor_active = models.BooleanField(default=True)
