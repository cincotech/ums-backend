from rest_framework import serializers

from .models import (
    ExamAttendance,
    ExamSession,
    GradeComplaint,
    JuryDecision,
    JurySession,
    OfficialDocument,
    TeacherPaymentClaim,
)


class ExamSessionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    supervisor_names = serializers.SerializerMethodField()

    class Meta:
        model = ExamSession
        fields = [
            "id",
            "course",
            "course_name",
            "exam_date",
            "duration_minutes",
            "room",
            "supervisors",
            "supervisor_names",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_supervisor_names(self, obj):
        return [f"{user.first_name} {user.last_name}" for user in obj.supervisors.all()]


class ExamAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamAttendance
        fields = [
            "id",
            "exam_session",
            "student",
            "student_name",
            "status",
            "incident_notes",
            "recorded_at",
        ]
        read_only_fields = ["id", "recorded_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class JurySessionSerializer(serializers.ModelSerializer):
    jury_member_names = serializers.SerializerMethodField()

    class Meta:
        model = JurySession
        fields = [
            "id",
            "session_name",
            "session_date",
            "jury_members",
            "jury_member_names",
            "status",
            "minutes_document",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_jury_member_names(self, obj):
        return [
            f"{user.first_name} {user.last_name}" for user in obj.jury_members.all()
        ]


class JuryDecisionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = JuryDecision
        fields = [
            "id",
            "jury_session",
            "student",
            "student_name",
            "decision",
            "notes",
            "validated_at",
        ]
        read_only_fields = ["id", "validated_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"


class GradeComplaintSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = GradeComplaint
        fields = [
            "id",
            "student",
            "student_name",
            "course",
            "course_name",
            "original_grade",
            "complaint_reason",
            "status",
            "assigned_to",
            "assigned_to_name",
            "new_grade",
            "resolution_notes",
            "submitted_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "submitted_at", "resolved_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class OfficialDocumentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    signed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OfficialDocument
        fields = [
            "id",
            "document_type",
            "title",
            "content",
            "status",
            "created_by_name",
            "signed_by_name",
            "created_at",
            "signed_at",
        ]
        read_only_fields = ["id", "created_at", "signed_at"]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_signed_by_name(self, obj):
        if obj.signed_by:
            return f"{obj.signed_by.first_name} {obj.signed_by.last_name}"
        return None


class TeacherPaymentClaimSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)

    class Meta:
        model = TeacherPaymentClaim
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "course",
            "course_name",
            "hours_taught",
            "hourly_rate",
            "total_amount",
            "status",
            "submitted_at",
            "processed_at",
        ]
        read_only_fields = ["id", "submitted_at", "processed_at"]

    def get_teacher_name(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"


class AcademicSecretaryStatsSerializer(serializers.Serializer):
    pending_exams = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    pending_claims = serializers.IntegerField()
    upcoming_juries = serializers.IntegerField()


class GradeEntryStatusSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    course_name = serializers.CharField()
    teacher_name = serializers.CharField()
    total_students = serializers.IntegerField()
    grades_entered = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    deadline = serializers.DateTimeField()
