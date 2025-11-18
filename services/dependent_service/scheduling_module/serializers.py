from rest_framework import serializers

from services.dependent_service.scheduling_module.scheduling_app.models import (
    ActivityReport,
    Attendance,
    ScheduleSlot,
    Timetable,
)


class ScheduleSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleSlot
        fields = "__all__"


class TimetableSerializer(serializers.ModelSerializer):
    slot = ScheduleSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Timetable
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class ActivityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityReport
        fields = "__all__"
