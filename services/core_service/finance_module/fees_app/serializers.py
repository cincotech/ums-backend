from rest_framework import serializers

from services.core_service.finance_module.fees_app.models import FeesSheet, Wording


class WordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wording
        fields = "__all__"


class FeesSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeesSheet
        fields = "__all__"

    def validate_base_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Base amount must be greater than zero.")
        return value
