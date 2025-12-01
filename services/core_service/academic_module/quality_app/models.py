import uuid
from django.db import models
from django.conf import settings


class QualityReport(models.Model):
    REPORT_TYPES = (
        ("academic_performance", "Academic Performance"),
        ("retention_rate", "Retention Rate"),
        ("success_rate", "Success Rate"),
        ("program_advancement", "Program Advancement"),
        ("custom", "Custom Report"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    title = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    summary = models.TextField(null=True, blank=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name="generated_reports")

    class Meta:
        db_table = "quality_reports"

    def __str__(self):
        return self.title
