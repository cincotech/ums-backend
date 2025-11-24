import uuid

from django.db import models

from services.foundational_service.auth_module.user_app.models import User


class QualityStandard(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    compliance_criteria = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "quality_standards"


class ComplianceAudit(models.Model):
    STATUS_CHOICES = (
        ("compliant", "Compliant"),
        ("non_compliant", "Non-Compliant"),
        ("partially_compliant", "Partially Compliant"),
        ("under_review", "Under Review"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard = models.ForeignKey(QualityStandard, on_delete=models.CASCADE)
    audit_period = models.CharField(max_length=100)
    compliance_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(null=True, blank=True)
    audited_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    audit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "compliance_audits"
