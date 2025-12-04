
from django.db import models
from django.conf import settings
from django.utils import timezone


class PaymentDerogation(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Approuvée"),
        ("rejected", "Rejetée"),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="derogations")
    reason = models.TextField()
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="derogation_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    rector_decision_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="rector_derogations")
    decision_comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    decision_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Derogation {self.id} - {self.student}"


class VisitorCourseAttribution(models.Model):
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    recommended_by = models.CharField(max_length=255)
    rector_validation = models.BooleanField(default=False)
    validation_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.course_name
