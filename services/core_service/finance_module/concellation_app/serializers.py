from rest_framework import serializers

from services.core_service.finance_module.concellation_app.models import (
    DebtCancellation,
)


class DebtCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtCancellation
        fields = "__all__"

    def validate_cancelled_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Cancelled amount must be greater than zero."
            )
        return value
