from rest_framework import serializers

from .models import Exam, ExamRoom, ExamSupervisor, ExamType


class ExamTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    exam_type_name = serializers.CharField(max_length=50)
    description = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = ExamType
        fields = (
            "id",
            "exam_type_name",
            "description",
        )


class ExamSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    course = serializers.UUIDField()
    exam_type = serializers.UUIDField()
    academic_year = serializers.UUIDField()

    exam_date = serializers.DateField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    status = serializers.CharField(read_only=True)

    class Meta:
        model = Exam
        fields = (
            "id",
            "course",
            "exam_type",
            "academic_year",
            "exam_date",
            "start_time",
            "end_time",
            "status",
        )


class ExamRoomSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    exam = serializers.UUIDField()
    room = serializers.UUIDField()
    range_student = serializers.CharField(
        max_length=10, required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = ExamRoom
        fields = (
            "id",
            "exam",
            "room",
            "range_student",
        )


class ExamSupervisorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    exam_room = serializers.UUIDField()
    supervisor = serializers.UUIDField()

    class Meta:
        model = ExamSupervisor
        fields = (
            "id",
            "exam_room",
            "supervisor",
        )

    def validate(self, data):
        instance = ExamSupervisor(**data)
        instance.clean()  # gère les conflits d'examens
        return data
