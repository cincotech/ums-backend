import base64
import datetime
import json
import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import (  # make sure path is correct
    User,
)


class StudentCard(models.Model):
    STATUS = (
        ("active", "Active"),
        ("expired", "Expired"),
        ("lost", "Lost"),
        ("replaced", "Replaced"),
        ("blocked", "Blocked"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="cards")
    card_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=8, choices=STATUS, default="active")
    printed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="printed_cards",
    )  # Changed to User
    photo = models.ImageField(upload_to="student_cards/photos/", null=True, blank=True)
    qrcode_data = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "student_cards"

    def generate_card_number(self):
        first_initial = (
            self.student.user.first_name[0].upper()
            if self.student.user.first_name
            else "X"
        )
        last_initial = (
            self.student.user.last_name[0].upper()
            if self.student.user.last_name
            else "X"
        )
        active_sm = self.student.get_active_matricule()
        matricule = active_sm.matricule if active_sm else "00000"
        return f"{first_initial}{last_initial}{matricule}"

    def generate_qr_data(self):
        active_sm = self.student.get_active_matricule()
        matricule_display = active_sm.matricule if active_sm else None
        student_info = {
            "student_id": str(self.student.id),
            "name": f"{self.student.user.first_name} {self.student.user.last_name}",
            "matricule": matricule_display,
            "card_number": self.card_number,
            "issue_date": str(self.issue_date),
            "expiry_date": str(self.expiry_date),
            "status": self.status,
            "printed_by": str(self.printed_by.id) if self.printed_by else None,
        }
        json_data = json.dumps(student_info)
        encoded_data = base64.b64encode(json_data.encode()).decode()
        return encoded_data

    def save(self, *args, **kwargs):
        # Ensure student has at least one validated inscription
        if not self.student.inscriptions.filter(regist_status="ACT").exists():
            raise ValueError(
                "Cannot issue card: student has no validated inscriptions."
            )

        if not self.card_number:
            self.card_number = self.generate_card_number()

        if not self.issue_date:
            self.issue_date = datetime.date.today()
        if not self.expiry_date:
            self.expiry_date = self.issue_date.replace(year=self.issue_date.year + 1)

        self.qrcode_data = self.generate_qr_data()

        super().save(*args, **kwargs)


class StudentCardLog(models.Model):
    ACTION = (
        ("issued", "Issued"),
        ("renewed", "Renewed"),
        ("replaced", "Replaced"),
        ("blocked", "Blocked"),
        ("unblocked", "Unblocked"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card = models.ForeignKey(
        StudentCard, on_delete=models.RESTRICT, related_name="logs"
    )
    action = models.CharField(max_length=9, choices=ACTION)
    action_date = models.DateTimeField(auto_now_add=True)
    performed_by = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "student_card_logs"
