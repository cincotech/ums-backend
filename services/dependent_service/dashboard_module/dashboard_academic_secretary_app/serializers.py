from rest_framework import serializers

from services.core_service.student_module.inscription_app.models import (
    Inscription,
    ComplementRequirement,
)
from services.dependent_service.exam_module.exam_app.models import (
    Exam,
    ExamRoom,
    ExamSupervisor,
)
from services.dependent_service.exam_module.result_app.models import Result

from .models import (
    GradeComplaint,
    JuryDecision,
    JurySession,
    OfficialDocument,
    TeacherPaymentClaim,
)

# ==================== DASHBOARD ====================


class AcademicSecretaryStatsSerializer(serializers.Serializer):
    upcoming_exams = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    pending_claims = serializers.IntegerField()
    upcoming_juries = serializers.IntegerField()
    active_inscriptions = serializers.IntegerField()
    pending_attributions = serializers.IntegerField()


# ==================== EXAM MANAGEMENT ====================


class ExamSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    exam_type_name = serializers.CharField(source="exam_type.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    supervisors = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id",
            "course",
            "course_name",
            "course_code",
            "exam_type",
            "exam_type_name",
            "start_date",
            "end_date",
            "duration_minutes",
            "max_marks",
            "instructions",
            "status",
            "created_by",
            "created_by_name",
            "rooms",
            "supervisors",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_rooms(self, obj):
        return [
            {
                "id": str(room.id),
                "room_name": room.room.room_name if room.room else None,
                "capacity": room.capacity,
            }
            for room in obj.exam_rooms.all()
        ]

    def get_supervisors(self, obj):
        return [
            {
                "id": str(sup.id),
                "supervisor_name": f"{sup.supervisor.first_name} {sup.supervisor.last_name}",
            }
            for sup in obj.exam_supervisors.all()
        ]


class ExamRoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.room_name", read_only=True)

    class Meta:
        model = ExamRoom
        fields = ["id", "exam", "room", "room_name", "capacity"]
        read_only_fields = ["id"]


class ExamSupervisorSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamSupervisor
        fields = ["id", "exam", "supervisor", "supervisor_name"]
        read_only_fields = ["id"]

    def get_supervisor_name(self, obj):
        return f"{obj.supervisor.first_name} {obj.supervisor.last_name}"


# ==================== GRADE MONITORING ====================


class GradeEntryStatusSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    course_name = serializers.CharField()
    course_code = serializers.CharField()
    teacher_id = serializers.UUIDField()
    teacher_name = serializers.CharField()
    total_students = serializers.IntegerField()
    grades_entered = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    academic_year = serializers.CharField()


class CourseResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    session_name = serializers.CharField(source="session.session_name", read_only=True)

    class Meta:
        model = Result
        fields = [
            "id",
            "course",
            "course_name",
            "inscription",
            "student_name",
            "student_matricule",
            "session",
            "session_name",
            "mark",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        return f"{obj.inscription.student.user.first_name} {obj.inscription.student.user.last_name}"

    def get_student_matricule(self, obj):
        return obj.inscription.get_matricule_for_type()


# ==================== JURY MANAGEMENT ====================


class JurySessionSerializer(serializers.ModelSerializer):
    jury_member_names = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    decision_count = serializers.SerializerMethodField()

    class Meta:
        model = JurySession
        fields = [
            "id",
            "session_name",
            "session_date",
            "class_group",
            "jury_members",
            "jury_member_names",
            "status",
            "minutes_document",
            "created_by",
            "created_by_name",
            "decision_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "class_group"]

    def get_jury_member_names(self, obj):
        return [
            f"{user.first_name} {user.last_name}" for user in obj.jury_members.all()
        ]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_decision_count(self, obj):
        return obj.jurydecision_set.count()


class JuryDecisionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    jury_session_name = serializers.CharField(
        source="jury_session.session_name", read_only=True
    )
    validated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = JuryDecision
        fields = [
            "id",
            "jury_session",
            "jury_session_name",
            "student",
            "student_name",
            "student_matricule",
            "decision",
            "notes",
            "validated_by",
            "validated_by_name",
            "validated_at",
        ]
        read_only_fields = ["id", "validated_by", "validated_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_student_matricule(self, obj):
        active_sm = obj.student.get_active_matricule()
        return active_sm.matricule if active_sm else None

    def get_validated_by_name(self, obj):
        return f"{obj.validated_by.first_name} {obj.validated_by.last_name}"


class ComplementRequirementSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    inscription_id = serializers.SerializerMethodField()
    feesheet_name = serializers.SerializerMethodField()

    class Meta:
        model = ComplementRequirement
        fields = [
            "id",
            "student",
            "student_name",
            "inscription",
            "inscription_id",
            "requirements",
            "course_count",
            "unit_price",
            "amount_due",
            "annual_renewal",
            "feesheet",
            "feesheet_name",
            "due_date",
            "status",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "amount_due", "created_at"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_inscription_id(self, obj):
        return str(obj.inscription.id) if obj.inscription else None

    def get_feesheet_name(self, obj):
        return obj.feesheet.wording.wording_name if obj.feesheet else None


# ==================== GRADE COMPLAINTS ====================


class GradeComplaintSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = GradeComplaint
        fields = [
            "id",
            "student",
            "student_name",
            "student_matricule",
            "course",
            "course_name",
            "course_code",
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

    def get_student_matricule(self, obj):
        active_sm = obj.student.get_active_matricule()
        return active_sm.matricule if active_sm else None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


# ==================== OFFICIAL DOCUMENTS ====================


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
            "created_by",
            "created_by_name",
            "signed_by",
            "signed_by_name",
            "created_at",
            "signed_at",
        ]
        read_only_fields = ["id", "created_by", "signed_by", "created_at", "signed_at"]

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_signed_by_name(self, obj):
        if obj.signed_by:
            return f"{obj.signed_by.first_name} {obj.signed_by.last_name}"
        return None


# ==================== PAYMENT CLAIMS ====================


class TeacherPaymentClaimSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPaymentClaim
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "course",
            "course_name",
            "course_code",
            "hours_taught",
            "hourly_rate",
            "total_amount",
            "status",
            "verified_by",
            "verified_by_name",
            "approved_by",
            "approved_by_name",
            "submitted_at",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "verified_by",
            "approved_by",
            "submitted_at",
            "processed_at",
        ]

    def get_teacher_name(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None


# ==================== INSCRIPTIONS ====================


class InscriptionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    class_name = serializers.CharField(source="class_fk.class_name", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )

    class Meta:
        model = Inscription
        fields = [
            "id",
            "student",
            "student_name",
            "student_matricule",
            "class_fk",
            "class_name",
            "academic_year",
            "academic_year_name",
            "regist_status",
            "date_inscription",
            "withdrawal_date",
            "is_year_close",
        ]
        read_only_fields = ["id", "withdrawal_date"]

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_student_matricule(self, obj):
        return obj.get_matricule_for_type()


class InscriptionStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    pending = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    by_class = serializers.ListField()


class CompilationStatusSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    compiled_results = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    status_breakdown = serializers.ListField()
