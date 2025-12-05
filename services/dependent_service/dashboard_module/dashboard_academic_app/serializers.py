from rest_framework import serializers

from .models import AttributionValidation


class AttributionValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributionValidation
        fields = "__all__"
        read_only_fields = ["id", "validated_by", "validation_date"]


class AttributionValidationDecisionSerializer(serializers.Serializer):
    validation_status = serializers.ChoiceField(choices=["approved", "rejected"])
    comments = serializers.CharField(required=False, allow_blank=True)
