import uuid

from django.db import models

from services.core_service.academic_module.course_app.models import Course
from services.core_service.academic_module.teacher_app.models import Teacher
from services.core_service.student_module.student_profile_app.models import Student
from services.foundational_service.auth_module.user_app.models import User


class StudentSurvey(models.Model):
    SURVEY_TYPES = (
        ("course_evaluation", "Course Evaluation"),
        ("teacher_evaluation", "Teacher Evaluation"),
        ("environment_satisfaction", "Environment Satisfaction"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey_type = models.CharField(max_length=50, choices=SURVEY_TYPES)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, null=True, blank=True
    )
    responses = models.JSONField(default=dict)
    rating = models.IntegerField()  # 1-5 scale
    comments = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_surveys"


class QualityStandard(models.Model):
    STANDARD_TYPES = (
        ("academic", "Academic Standard"),
        ("administrative", "Administrative Standard"),
        ("accreditation", "Accreditation Requirement"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard_type = models.CharField(max_length=50, choices=STANDARD_TYPES)
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
