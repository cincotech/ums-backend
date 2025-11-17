from rest_framework import serializers

from services.core_service.student_module.inscription_app.models import Inscription

from .models import (
    AbsenceJustification,
    CounselingSession,
    DocumentRequest,
    Scholarship,
    StudentActivity,
)


class DocumentRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentRequest
        fields = [
            "id",
            "student",
            "student_name",
            "document_type",
            "purpose",
            "status",
            "requested_at",
            "processed_at",
            "notes",
        ]
        read_only_fields = ["id", "requested_at", "processed_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class AbsenceJustificationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = AbsenceJustification
        fields = [
            "id",
            "student",
            "student_name",
            "absence_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "submitted_at",
            "reviewed_at",
        ]
        read_only_fields = ["id", "submitted_at", "reviewed_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class StudentActivitySerializer(serializers.ModelSerializer):
    organizer_name = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentActivity
        fields = [
            "id",
            "activity_type",
            "name",
            "description",
            "organizer_name",
            "participant_count",
            "start_date",
            "end_date",
            "location",
            "is_approved",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_organizer_name(self, obj):
        return f"{obj.organizer.user.first_name} {obj.organizer.user.last_name}"

    def get_participant_count(self, obj):
        return obj.participants.count()


class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "student",
            "student_name",
            "scholarship_type",
            "provider",
            "amount",
            "academic_year",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class CounselingSessionSerializer(serializers.ModelSerializer):
    counselor_name = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = CounselingSession
        fields = [
            "id",
            "session_type",
            "title",
            "description",
            "counselor_name",
            "participant_count",
            "scheduled_date",
            "duration_minutes",
            "location",
            "is_group_session",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_counselor_name(self, obj):
        return f"{obj.counselor.first_name} {obj.counselor.last_name}"

    def get_participant_count(self, obj):
        return obj.participants.count()


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()

    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "student_name",
            "program_name",
            "academic_year",
            "inscription_date",
            "is_active",
        ]
        read_only_fields = ["id", "inscription_date"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_program_name(self, obj):
        return (
            obj.student.graduate_infos.first().department.name
            if obj.student.graduate_infos.exists()
            else "N/A"
        )


class StudentServicesStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    pending_absences = serializers.IntegerField()
    active_scholarships = serializers.IntegerField()
    upcoming_sessions = serializers.IntegerField()
    active_activities = serializers.IntegerField()


class StudentReportSerializer(serializers.Serializer):
    academic_year = serializers.CharField()
    total_enrolled = serializers.IntegerField()
    by_program = serializers.DictField()
    by_level = serializers.DictField()
    success_rate = serializers.FloatField()
    retention_rate = serializers.FloatField()
