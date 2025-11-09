import uuid

from django.db import models

from services.core_service.student_module.student_profile_app.models import Student


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
    card_number = models.CharField(max_length=30, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=8, choices=STATUS, default="active")
    printed_by = models.CharField(max_length=100, null=True, blank=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    qrcode_data = models.TextField()

    class Meta:
        db_table = "student_cards"


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
