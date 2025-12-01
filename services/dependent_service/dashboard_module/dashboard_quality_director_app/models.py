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


class AcademicPerformanceReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.CharField(max_length=9)
    semester = models.IntegerField(choices=((1, "Semester 1"), (2, "Semester 2")))
    success_rate = models.FloatField()
    failure_rate = models.FloatField()
    average_grade = models.FloatField()
    underperforming_courses = models.JSONField(default=list)
    generated_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "academic_performance_reports"
        unique_together = ("academic_year", "semester")


class ProgramExecutionTracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_name = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9)
    planned_coverage = models.IntegerField()
    actual_coverage = models.IntegerField()
    progress_percentage = models.FloatField()
    objectives_met = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "program_execution_tracking"
        unique_together = ("program_name", "academic_year")


class StudentRetentionAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.CharField(max_length=9)
    total_enrolled = models.IntegerField()
    retained_students = models.IntegerField()
    retention_rate = models.FloatField()
    dropout_rate = models.FloatField()
    dropout_reasons = models.JSONField(default=dict)
    audited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_retention_audits"
        unique_together = ("academic_year",)


class CourseSatisfactionSurvey(models.Model):
    RATING_CHOICES = ((1, "Poor"), (2, "Fair"), (3, "Good"), (4, "Very Good"), (5, "Excellent"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=9)
    course_quality_rating = models.IntegerField(choices=RATING_CHOICES)
    teacher_rating = models.IntegerField(choices=RATING_CHOICES)
    environment_rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(null=True, blank=True)
    survey_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_satisfaction_surveys"
