from rest_framework import serializers

from services.dependent_service.dashboard_module.dashboard_collection_agent_app.models import (
    Payment,
)
from services.dependent_service.dashboard_module.dashboard_shared_app.models import (
    Message,
    Notification,
)
from services.dependent_service.document_module.request_app.models import Request
from services.dependent_service.exam_module.result_app.models import (
    CompiledResult,
    Result,
)
from services.dependent_service.scheduling_module.scheduling_app.models import (
    Attendance,
)


class StudentDashboardStatsSerializer(serializers.Serializer):
    unread_notifications = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    current_gpa = serializers.FloatField()
    attendance_rate = serializers.FloatField()
    amount_paid = serializers.FloatField()
    total_amount = serializers.FloatField()
    credits_earned = serializers.IntegerField()


class StudentProfileSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    matricule = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    program = serializers.CharField()
    academic_year = serializers.CharField()
    payment_status = serializers.CharField()


class StudentGradesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["id", "course", "mark", "grade"]


class StudentTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompiledResult
        fields = ["id", "results", "average_mark", "status", "is_promoted"]


class StudentScheduleSerializer(serializers.Serializer):
    course_name = serializers.CharField()
    teacher_name = serializers.CharField()
    day_of_week = serializers.CharField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    room = serializers.CharField()


class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "date", "status"]


class StudentNotificationSerializer(serializers.ModelSerializer):
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


class StudentDocumentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ["id", "document", "request_date", "request_status"]


class StudentMessageSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "message_type",
            "recipient_name",
            "sender_name",
            "subject",
            "content",
            "is_read",
            "sent_at",
        ]
        read_only_fields = ["id", "sent_at"]

    def get_recipient_name(self, obj):
        return f"{obj.recipient.first_name} {obj.recipient.last_name}"

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"


class StudentPaymentInfoSerializer(serializers.Serializer):
    """Serializer for payment information with installments"""
    payments = serializers.ListField(child=serializers.DictField())
    installments = serializers.ListField(child=serializers.DictField())
    payment_summary = serializers.SerializerMethodField()
    
    def get_payment_summary(self, obj):
        """Get payment summary information"""
        payments = obj.get('payments', [])
        installments = obj.get('installments', [])
        
        total_paid = sum(float(p.get('amount_paid', 0)) for p in payments)
        total_due = sum(float(i.get('amount', 0)) for i in installments)
        
        return {
            'total_paid': total_paid,
            'total_due': total_due,
            'balance': total_due - total_paid,
            'payment_count': len(payments),
            'installment_count': len(installments)
        }


class AcademicProgressSerializer(serializers.Serializer):
    total_credits_required = serializers.IntegerField()
    credits_earned = serializers.IntegerField()
    credits_remaining = serializers.IntegerField()
    current_semester = serializers.CharField()
    gpa = serializers.FloatField()
    completion_percentage = serializers.FloatField()


class StudentJuryDecisionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    jury_session_name = serializers.CharField(source="jury_session.session_name")
    jury_session_date = serializers.DateTimeField(source="jury_session.session_date")
    decision = serializers.CharField()
    notes = serializers.CharField()
    validated_by_name = serializers.SerializerMethodField()
    validated_at = serializers.DateTimeField()

    def get_validated_by_name(self, obj):
        return f"{obj.validated_by.first_name} {obj.validated_by.last_name}"


class StudentGradeComplaintSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    course_id = serializers.UUIDField(write_only=True, required=False)
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    original_grade = serializers.FloatField()
    complaint_reason = serializers.CharField()
    status = serializers.CharField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    new_grade = serializers.FloatField(read_only=True)
    resolution_notes = serializers.CharField(read_only=True)
    submitted_at = serializers.DateTimeField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class StudentExamSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    course_name = serializers.CharField(source="course.course_name")
    exam_type_name = serializers.CharField(source="exam_type.name")
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField()
    status = serializers.CharField()
    max_marks = serializers.DecimalField(max_digits=5, decimal_places=2)


class StudentOfficialDocumentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    document_type = serializers.CharField()
    title = serializers.CharField()
    content = serializers.CharField()
    created_by_name = serializers.SerializerMethodField()
    signed_by_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    signed_at = serializers.DateTimeField()

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_signed_by_name(self, obj):
        if obj.signed_by:
            return f"{obj.signed_by.first_name} {obj.signed_by.last_name}"
        return None
