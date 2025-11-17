from rest_framework import serializers

from .models import ComplianceAudit, QualityStandard, StudentSurvey


class AcademicPerformanceSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    course_name = serializers.CharField()
    success_rate = serializers.FloatField()
    failure_rate = serializers.FloatField()
    average_grade = serializers.FloatField()
    total_students = serializers.IntegerField()


class ProgramProgressSerializer(serializers.Serializer):
    program_name = serializers.CharField()
    completion_rate = serializers.FloatField()
    on_schedule = serializers.BooleanField()
    covered_topics = serializers.IntegerField()
    total_topics = serializers.IntegerField()


class StudentDemographicsSerializer(serializers.Serializer):
    total_enrolled = serializers.IntegerField()
    retention_rate = serializers.FloatField()
    dropout_rate = serializers.FloatField()
    by_program = serializers.DictField()
    by_level = serializers.DictField()


class StudentSurveySerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentSurvey
        fields = [
            "id",
            "survey_type",
            "student_name",
            "course_name",
            "teacher_name",
            "rating",
            "comments",
            "submitted_at",
        ]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"
        return None


class QualityStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityStandard
        fields = [
            "id",
            "standard_type",
            "title",
            "description",
            "compliance_criteria",
            "is_active",
            "created_at",
        ]


class ComplianceAuditSerializer(serializers.ModelSerializer):
    standard_title = serializers.CharField(source="standard.title", read_only=True)
    audited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAudit
        fields = [
            "id",
            "standard_title",
            "audit_period",
            "compliance_status",
            "findings",
            "recommendations",
            "audited_by_name",
            "audit_date",
        ]

    def get_audited_by_name(self, obj):
        return f"{obj.audited_by.first_name} {obj.audited_by.last_name}"


class QualityDashboardStatsSerializer(serializers.Serializer):
    total_courses_analyzed = serializers.IntegerField()
    average_course_rating = serializers.FloatField()
    compliance_rate = serializers.FloatField()
    pending_audits = serializers.IntegerField()
    recent_surveys = serializers.IntegerField()
