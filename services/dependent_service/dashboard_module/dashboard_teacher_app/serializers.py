from rest_framework import serializers

from services.core_service.academic_module.teacher_app.models import Attribution
from services.dependent_service.dashboard_module.dashboard_academic_secretary_app.models import (
    TeacherPaymentClaim,
)
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Message,
    Notification,
)
from services.dependent_service.exam_module.exam_app.models import ExamSupervisor
from services.dependent_service.exam_module.result_app.models import Result
from services.dependent_service.scheduling_module.scheduling_app.models import (
    Attendance,
    Timetable,
)


class TeacherDashboardStatsSerializer(serializers.Serializer):
    active_courses = serializers.IntegerField()
    upcoming_exams = serializers.IntegerField()
    pending_grades = serializers.IntegerField()
    pending_claims = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class TeacherProfileSerializer(serializers.Serializer):
    teacher_id = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    teacher_grade = serializers.CharField()
    degree = serializers.CharField()
    university = serializers.CharField()
    speciality = serializers.CharField()
    total_courses_taught = serializers.IntegerField()


class AttributionSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    course_code = serializers.CharField(source="course.course_code", read_only=True)
    academic_year_name = serializers.CharField(
        source="academic_year.academic_year", read_only=True
    )
    principal_teacher_name = serializers.SerializerMethodField()
    substitute_teacher_name = serializers.SerializerMethodField()
    submitted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Attribution
        fields = [
            "id",
            "course",
            "course_name",
            "course_code",
            "principal_teacher",
            "principal_teacher_name",
            "substitute_teacher",
            "substitute_teacher_name",
            "academic_year",
            "academic_year_name",
            "date_attribution",
            "status_principal_teacher",
            "status_substitute_teacher",
            "commentaire",
            "submitted_by",
            "submitted_by_name",
        ]
        read_only_fields = ["id", "submitted_by", "submitted_by_name"]

    def get_principal_teacher_name(self, obj):
        return f"{obj.principal_teacher.user.first_name} {obj.principal_teacher.user.last_name}"

    def get_substitute_teacher_name(self, obj):
        if obj.substitute_teacher:
            return f"{obj.substitute_teacher.user.first_name} {obj.substitute_teacher.user.last_name}"
        return None

    def get_submitted_by_name(self, obj):
        return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}"


class TeacherCourseSerializer(serializers.Serializer):
    course_id = serializers.UUIDField(source="course.id")
    course_name = serializers.CharField(source="course.course_name")
    course_code = serializers.CharField(source="course.course_code")
    student_count = serializers.IntegerField()
    grades_entered = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    academic_year = serializers.CharField(
        source="attribution.academic_year.academic_year"
    )


class TeacherCourseStudentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField(source="student.id")
    matricule = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="student.user.email")
    class_name = serializers.CharField(source="inscription.class_fk.class_name")
    mark = serializers.SerializerMethodField()
    attendance_rate = serializers.FloatField()

    def get_full_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}"

    def get_matricule(self, obj):
        """Retourne le matricule correspondant à l'inscription de l'étudiant."""
        if hasattr(obj, 'inscription') and obj.inscription:
            matricule = obj.inscription.get_matricule_for_type()
            if matricule:
                return matricule
        # Fallback: use student's active matricule
        active_sm = obj.student.get_active_matricule()
        return active_sm.matricule if active_sm else None

    def get_mark(self, obj):
        return obj["result"].mark if obj["result"] else None


class GradeEntrySerializer(serializers.Serializer):
    inscription_id = serializers.UUIDField()
    session_id = serializers.UUIDField()
    mark = serializers.FloatField(min_value=0, max_value=100)


class BulkGradeEntrySerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    grades = serializers.ListField(child=serializers.DictField())


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
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
            "session",
            "session_name",
            "mark",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        return f"{obj.inscription.student.user.first_name} {obj.inscription.student.user.last_name}"


class TeacherExamSerializer(serializers.ModelSerializer):
    exam_id = serializers.UUIDField(source="exam.id", read_only=True)
    course_name = serializers.CharField(
        source="exam.course.course_name", read_only=True
    )
    exam_type = serializers.CharField(source="exam.exam_type.name", read_only=True)
    start_date = serializers.DateTimeField(source="exam.start_date", read_only=True)
    end_date = serializers.DateTimeField(source="exam.end_date", read_only=True)
    duration_minutes = serializers.IntegerField(
        source="exam.duration_minutes", read_only=True
    )
    status = serializers.CharField(source="exam.status", read_only=True)

    class Meta:
        model = ExamSupervisor
        fields = [
            "id",
            "exam_id",
            "course_name",
            "exam_type",
            "start_date",
            "end_date",
            "duration_minutes",
            "status",
            "supervisor",
        ]
        read_only_fields = ["id"]


class TeacherScheduleSerializer(serializers.ModelSerializer):
    slots = serializers.SerializerMethodField()
    class_group_name = serializers.CharField(
        source="class_group.group_name", read_only=True
    )
    class_name = serializers.CharField(
        source="class_group.class_fk.class_name", read_only=True
    )

    class Meta:
        model = Timetable
        fields = [
            "id",
            "class_group",
            "class_group_name",
            "class_name",
            "start_date",
            "end_date",
            "is_published",
            "slots",
        ]
        read_only_fields = ["id"]

    def get_slots(self, obj):
        return [
            {
                "id": str(slot.id),
                "course_name": slot.course.course_name,
                "day_of_week": slot.day_of_week,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "room": slot.room.room_name if slot.room else None,
            }
            for slot in obj.slots.all()
        ]


class TeacherPaymentClaimSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPaymentClaim
        fields = [
            "id",
            "teacher",
            "course",
            "course_name",
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
            "teacher",
            "status",
            "verified_by",
            "approved_by",
            "submitted_at",
            "processed_at",
        ]

    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
        return None


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "inscription",
            "student_name",
            "student_matricule",
            "date",
            "status",
            "notes",
        ]
        read_only_fields = ["id"]

    def get_student_name(self, obj):
        return f"{obj.inscription.student.user.first_name} {obj.inscription.student.user.last_name}"

    def get_student_matricule(self, obj):
        return obj.inscription.get_matricule_for_type()


class AttendanceEntrySerializer(serializers.Serializer):
    inscription_id = serializers.UUIDField()
    attendance_date = serializers.DateField()
    status = serializers.ChoiceField(choices=["present", "absent", "justified", "late"])
    notes = serializers.CharField(required=False, allow_blank=True)


class TeacherNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient_type",
            "notification_type",
            "title",
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TeacherMessageSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "message_type",
            "recipient",
            "recipient_name",
            "sender",
            "sender_name",
            "subject",
            "content",
            "is_read",
            "sent_at",
        ]
        read_only_fields = ["id", "sender", "sent_at"]

    def get_recipient_name(self, obj):
        return f"{obj.recipient.first_name} {obj.recipient.last_name}"

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"


class TeachingStatisticsSerializer(serializers.Serializer):
    total_courses = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_grades_entered = serializers.IntegerField()
    average_grade = serializers.FloatField()
