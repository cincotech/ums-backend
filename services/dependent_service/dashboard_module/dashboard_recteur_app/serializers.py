from rest_framework import serializers

from services.core_service.academic_module.quality_app.serializers import QualityReportSerializer
from .models import PaymentDerogation, VisitorCourseAttribution


class PaymentDerogationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDerogation
        fields = "__all__"
        read_only_fields = ["status", "rector_decision_by", "decision_date"]


class PaymentDerogationDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["approved", "rejected"])
    comment = serializers.CharField(required=False)


class VisitorCourseAttributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorCourseAttribution
        fields = "__all__"
        read_only_fields = ["rector_validation", "validation_date"]
