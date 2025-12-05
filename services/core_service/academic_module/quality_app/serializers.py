from rest_framework import serializers

from .models import QualityReport


class QualityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityReport
        fields = "__all__"
        read_only_fields = ["id", "generated_date", "generated_by"]
