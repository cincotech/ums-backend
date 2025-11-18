from rest_framework import serializers

from .models import ExamAttendance


class ExamAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAttendance
        fields = [
            "id",
            "examroom",
            "card",
            "inscription",
            "attendance_time",
            "status",
            "incident_notes",
            "recorded_by",
            "recorded_at",
        ]
        read_only_fields = ["attendance_time", "recorded_at", "recorded_by"]
