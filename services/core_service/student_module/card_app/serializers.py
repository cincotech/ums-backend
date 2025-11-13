from rest_framework import serializers

from services.core_service.student_module.card_app.models import (
    StudentCard,
    StudentCardLog,
)


class StudentCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCard
        fields = "__all__"
        read_only_fields = ("card_number", "issue_date", "expiry_date", "qrcode_data")

    def validate_student(self, value):
        # Ensure student has at least one validated inscription
        if not value.inscriptions.filter(regist_status="ACT").exists():
            raise serializers.ValidationError("Student has no validated inscriptions.")
        return value

    def create(self, validated_data):
        return StudentCard.objects.create(**validated_data)


class StudentCardLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCardLog
        fields = "__all__"
        read_only_fields = ("action_date",)
