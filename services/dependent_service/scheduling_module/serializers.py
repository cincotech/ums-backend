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
    slots = ScheduleSlotSerializer(many=True, read_only=True)
    slot_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = Timetable
        fields = "__all__"
        extra_kwargs = {"slots": {"read_only": True}}

    def create(self, validated_data):
        slot_ids = validated_data.pop("slot_ids", [])
        timetable = Timetable.objects.create(**validated_data)
        if slot_ids:
            timetable.slots.set(slot_ids)
        return timetable

    def update(self, instance, validated_data):
        slot_ids = validated_data.pop("slot_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if slot_ids is not None:
            instance.slots.set(slot_ids)
        return instance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class ActivityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityReport
        fields = "__all__"
