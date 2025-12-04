from rest_framework import serializers

from services.core_service.academic_module.quality_app.models import QualityReport
from services.core_service.academic_module.quality_app.serializers import QualityReportSerializer
from .models import (
    AcademicPerformanceReport,
    ComplianceAudit,
    CourseSatisfactionSurvey,
    ProgramExecutionTracking,
    QualityStandard,
    StudentRetentionAudit,
)


class QualityStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityStandard
        fields = ["id", "title", "description", "compliance_criteria", "is_active", "created_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class ComplianceAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAudit
        fields = ["id", "standard", "audit_period", "compliance_status", "findings", "recommendations", "audited_by", "audit_date"]
        read_only_fields = ["id", "audit_date"]


class AcademicPerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPerformanceReport
        fields = ["id", "academic_year", "semester", "success_rate", "failure_rate", "average_grade", "underperforming_courses", "generated_by", "generated_at"]
        read_only_fields = ["id", "generated_at"]


class ProgramExecutionTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramExecutionTracking
        fields = ["id", "program_name", "academic_year", "planned_coverage", "actual_coverage", "progress_percentage", "objectives_met", "last_updated"]
        read_only_fields = ["id", "last_updated"]


class StudentRetentionAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRetentionAudit
        fields = ["id", "academic_year", "total_enrolled", "retained_students", "retention_rate", "dropout_rate", "dropout_reasons", "audited_at"]
        read_only_fields = ["id", "audited_at"]


class CourseSatisfactionSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSatisfactionSurvey
        fields = ["id", "course_name", "teacher_name", "academic_year", "course_quality_rating", "teacher_rating", "environment_rating", "comments", "survey_date"]
        read_only_fields = ["id", "survey_date"]
