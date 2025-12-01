from rest_framework import serializers

from services.core_service.finance_module.payment_app.models import Payment
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


class StudentProfileSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    matricule = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    program = serializers.CharField()
    academic_year = serializers.CharField()
    payment_status = serializers.CharField()




class StudentTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompiledResult
        fields = ["id", "results", "average_mark", "status", "is_promoted"]




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



class StudentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "amount_paid", "payment_date", "payment_method", "reference"]
        read_only_fields = ["id", "payment_date"]




class AcademicProgressSerializer(serializers.Serializer):
    total_credits_required = serializers.IntegerField()
    credits_earned = serializers.IntegerField()
    credits_remaining = serializers.IntegerField()
    current_semester = serializers.CharField()
    gpa = serializers.FloatField()
    completion_percentage = serializers.FloatField()
